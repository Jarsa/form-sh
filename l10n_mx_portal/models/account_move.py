import base64
import io
import logging
import zipfile

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def l10n_mx_edi_action_reinvoice(self):
        """Allows generating a new invoice with the current date from the
        customer portal."""
        mx_date = self.env["l10n_mx_edi.certificate"].sudo().get_mx_current_datetime().date()
        ctx = {"disable_after_commit": True}
        message = ""
        for invoice in self.filtered(lambda inv: inv.state != "draft"):
            if mx_date <= date_utils.end_of(invoice.invoice_date, "month"):
                # Get the credit move line to reconcile with a new invoice
                payment_move_lines = invoice.payment_move_line_ids
                try:
                    invoice.button_cancel()
                except UserError as error:
                    _logger.error(error)
                    message += _("Error on the process, please contact the salesperson.")
                    continue
                invoice.refresh()
                invoice.action_invoice_draft()
                invoice.write({"invoice_date": mx_date.strftime("%Y-%m-%d")})
                invoice.refresh()
                invoice.with_context(**ctx).action_post()
                invoice.refresh()
                # Now reconcile the payment
                if payment_move_lines:
                    invoice.register_payment(payment_move_lines)
                continue

            # Case B: Create a new invoice and pay with a Credit Note
            # Create a Credit Note from old invoice
            refund_invoice = invoice._reverse_moves()
            refund_invoice.action_post()
            # Get the credit move line to reconcile with a new invoice
            refund_move_line = refund_invoice.line_ids.filtered("credit")
            # Create a new invoice
            new_invoice = invoice.copy({"invoice_date": mx_date})
            new_invoice.action_post()
            # Now reconcile the new invoice with the credit note
            new_invoice.js_assign_outstanding_line(refund_move_line.id)
        return message

    def get_cfdi_att(self, attachment_type):
        """Return an attachment related to a signed invoice

        Possible results:
        - .xml: the signed CFDI
        - .pdf: printed copy
        - .zip: a ZIP file containing both XML and PDF files
        """
        assert attachment_type in (".xml", ".pdf", ".zip"), attachment_type
        if attachment_type == ".xml":
            return self._get_l10n_mx_edi_signed_edi_document()[:1].attachment_id
        if attachment_type == ".pdf":
            mail_template_id = self.action_invoice_sent()["context"]["default_template_id"]
            mail_template = self.env["mail.template"].browse(mail_template_id)
            return mail_template.report_template.retrieve_attachment(self)
        return self.env["ir.attachment"].search(
            [
                ("name", "=like", "%.zip"),
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("mimetype", "=", "application/zip"),
            ],
            limit=1,
        )

    def _get_zipped_cfdi(self):
        """Generate a ZIP file containing the CFDI (XML) and printed copy (PDF) of a signed invoice"""
        # If There's already a generated ZIP, don't create a new attachment but return existing one
        zip_attachment = self.get_cfdi_att(attachment_type=".zip")
        if zip_attachment:
            return zip_attachment

        # Ensure a PDF is already generated before generating the ZIP
        self._generate_invoice_report()

        # If there's neither XML nor PDF attachment, don't create ZIP
        attachments_to_zip = self.get_cfdi_att(attachment_type=".xml") + self.get_cfdi_att(attachment_type=".pdf")
        if not attachments_to_zip:
            return attachments_to_zip

        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, "w") as zipped_invoice:
            for attachment in attachments_to_zip:
                zipped_invoice.writestr(attachment.name, base64.b64decode(attachment.datas))
            zipped_invoice.close()
            zip_name = "%s.zip" % attachments_to_zip[0].name.rsplit(".", 1)[0]
            values = {
                "name": zip_name,
                "type": "binary",
                "mimetype": "application/zip",
                "public": False,
                "res_id": self.id,
                "res_model": self._name,
                "datas": base64.b64encode(zip_stream.getvalue()),
            }
        attachment = self.env["ir.attachment"].create(values)
        return attachment

    def _generate_invoice_report(self, send=False):
        """Print the PDF report as it were going to be sent and, optionally, send it right away.

        This is similar to pressing the button "Send & Print" and sending the email using the
        composer that pops up.
        """
        ctx = self.action_invoice_sent()["context"]
        composer = self.env["mail.compose.message"].with_context(**ctx).create({})
        composer.onchange_template_id_wrapper()
        if send:
            composer.send_mail()
        return True
