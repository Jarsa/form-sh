# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import timedelta

from freezegun import freeze_time

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("account_move", "post_install", "-at_install")
class TestAccountMove(TestMxEdiCommon):
    def setUp(self):
        super().setUp()
        self.env.registry.enter_test_mode(self.env.cr)
        self.addCleanup(self.registry.leave_test_mode)

    def test_01_send_invoice_signed_mail(self):
        """Testing the send of a mail saying that the invoice was signed.
        Also, raising an error when trying to set the value 'to_send' in the field `l10n_mx_edi_signed_to_send` of the
        invoice when the invoice was already sent.
        """
        with freeze_time(self.frozen_today), mute_logger("py.warnings"):
            self.invoice.action_post()
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "not_send")
            generated_files = self._process_documents_web_services(self.invoice, {"cfdi_3_3"})
            self.assertTrue(generated_files, "The invoice was not signed.")
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "to_send")

        # Even when the invoice is created and edited with a freeze time of 2017, the write date is the real time of
        # the test so we need to use it to send the email with the delay of 5min (we need to put 6 instead of 5
        # because of milliseconds)
        min_later = self.invoice.write_date + timedelta(minutes=6)
        with freeze_time(min_later):
            self.invoice.flush()
            self.invoice._cron_send_invoice_signed_mail(auto_commit=False)
            self.invoice.refresh()
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "sent")
            mail = self.invoice.message_ids.filtered(
                lambda msg: "Here is your signed\n            invoice" in msg.body
            )
            self.assertTrue(mail)

            error_msg = "This action can only be performed on signed invoices that have failed to be sent by e-mail."
            with self.assertRaises(UserError, msg=error_msg):
                self.invoice._action_to_set_invoices_to_send()
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "sent")

    def test_02_not_send_invoice_signed_mail(self):
        """Testing the trying to send of a mail saying that the invoice was signed, but the mail is not sent:
        - Case 1: The invoice is not signed yet.
        - Case 2: There was an error when trying to send the mail, and setting the field `l10n_mx_edi_signed_to_send`
        to 'with_error', and using the server action to return that value to 'to_send'.
        """
        with freeze_time(self.frozen_today), mute_logger("py.warnings"):
            self.invoice.action_post()
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "not_send")
            # Not signed
            self.invoice._send_invoice_signed_mail()
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "not_send")

            generated_files = self._process_documents_web_services(self.invoice, {"cfdi_3_3"})
            self.assertTrue(generated_files, "The invoice was not signed.")
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "to_send")

        # Even when the invoice is created and edited with a freeze time of 2017, the write date is the real time of
        # the test so we need to use it to send the email with the delay of 5min (we need to put 6 instead of 5
        # because of milliseconds)
        min_later = self.invoice.write_date + timedelta(minutes=6)
        with freeze_time(min_later), mute_logger("odoo.addons.l10n_mx_edi_autosent_edi_document.models.account_move"):
            template = self.env.ref("l10n_mx_edi_autosent_edi_document.email_template_edi_invoice_signed")
            template.unlink()

            self.invoice._cron_send_invoice_signed_mail(auto_commit=False)
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "with_error")
            message_post = self.invoice.message_ids[0].body
            msg_error = "The signed invoice was not sent because:"
            self.assertIn(msg_error, message_post)
            msg_error = "External ID not found in the system: "
            msg_error += "l10n_mx_edi_autosent_edi_document.email_template_edi_invoice_signed"
            self.assertIn(msg_error, message_post)

            self.invoice._action_to_set_invoices_to_send()
            self.assertEqual(self.invoice.l10n_mx_edi_signed_to_send, "to_send")
