# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_mx_edi_signed_to_send = fields.Selection(
        [
            ("not_send", "Not Send"),
            ("to_send", "To Send"),
            ("sent", "Sent"),
            ("with_error", "With Error"),
        ],
        string="Invoice Signed to Send",
        readonly=True,
        copy=False,
        default="not_send",
        help="If set, indicates that the invoice:\n"
        "- 'Not Send': It isn't an invoice, or it is still Draft or not signed.\n"
        "- 'To Send': It will be sent by email automatically.\n"
        "- 'Sent': It has been sent by email automatically.\n"
        "- 'With Error': It failed while it was trying to be sent automatically by email.",
    )

    def _action_to_set_invoices_to_send(self):
        """Method to allow set the field `l10n_mx_edi_signed_to_send` in invoices that had an error after fixing the
        error to allow sending them.
        """
        records_without_error = self.filtered(
            lambda account_move: account_move.l10n_mx_edi_signed_to_send != "with_error"
        )
        if records_without_error:
            raise UserError(
                _("This action can only be performed on signed invoices that have failed to be sent by e-mail.")
            )
        self.l10n_mx_edi_signed_to_send = "to_send"

    def _cron_send_invoice_signed_mail(self, limit=50, minute_delay=5, auto_commit=True):
        """Method that will send an email to the Customer of the Invoice, once the invoice is signed.
        The delay correspond to the time range for the last change of each invoice, so if it was change in the last
        few minutes there can be more changes in the amount or invoice user or partner.
        """
        write_date = fields.Datetime.now() - relativedelta(minutes=minute_delay)
        domain = [
            ("l10n_mx_edi_signed_to_send", "=", "to_send"),
            ("write_date", "<=", write_date),
            ("state", "=", "posted"),
        ]
        invoices = self.env["account.move"].search(domain, limit=limit)
        for invoice in invoices:
            invoice._send_invoice_signed_mail(auto_commit)

    # We are managing the commit manually because this method is being called by a cron, which needs the commit.
    # pylint: disable=invalid-commit
    def _send_invoice_signed_mail(self, auto_commit=False):
        """Method that will send the email to the Customer of the Invoice and will mark the field
        `l10n_mx_edi_signed_to_send` of the invoice as 'sent' to avoid send it again or if there is an error mark it
        to 'with_error' and letting to know the user why the invoice was not sent.
        """
        self.ensure_one()
        if self.l10n_mx_edi_signed_to_send != "to_send":
            return True

        with self.env.cr.savepoint():
            self.l10n_mx_edi_signed_to_send = "sent"

            try:
                template = self.env.ref("l10n_mx_edi_autosent_edi_document.email_template_edi_invoice_signed")
                context = self.action_invoice_sent()["context"]
                context.update(
                    {
                        "active_ids": self.ids,
                        "default_use_template": bool(template),
                        "default_template_id": template.id,
                    }
                )
                with Form(self.env["mail.compose.message"].with_context(**context)) as composer:
                    composer.model = self._name
                    composer.res_id = self.id
                    composer.composition_mode = "comment"
                    composer.partner_ids.add(self.partner_id)
                    composer = composer.save()
                composer.with_context(no_new_invoice=True).send_mail(auto_commit)
            except BaseException as base_exception:
                _logger.exception("%s", base_exception)
                msg_error = _("The signed invoice was not sent because:")
                msg_error += "<br/> %s" % base_exception
                self.message_post(body=msg_error)
                self.l10n_mx_edi_signed_to_send = "with_error"

        if auto_commit:
            self.env.cr.commit()
