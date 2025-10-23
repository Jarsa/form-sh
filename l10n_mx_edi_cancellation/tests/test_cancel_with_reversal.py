from datetime import timedelta

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestAccountPaymentReversal(TestMxEdiCommon):
    def setUp(self):
        super().setUp()
        self.company = self.env.user.company_id
        self.company.sudo().search([("name", "=", "ESCUELA KEMPER URGATE")]).write(
            {"name": "ESCUELA KEMPER URGATE TEST"}
        )
        self.company.name = "ESCUELA KEMPER URGATE"
        self.certificate._check_credentials()

    def test_cancel_01(self):
        """Try to cancel an invoice with case 01"""
        invoice = self.invoice
        invoice.action_post()
        self._process_documents_web_services(invoice, {"cfdi_3_3"})
        self.assertEqual(invoice.edi_state, "sent", invoice.message_ids.mapped("body"))
        invoice.l10n_mx_edi_cancellation = "01"
        invoice.button_cancel_posted_moves()
        invoice.button_draft()
        invoice2 = invoice.copy()
        invoice2.action_post()
        self._process_documents_web_services(invoice2, {"cfdi_3_3"})
        self.assertEqual(invoice2.edi_state, "sent", invoice.message_ids.mapped("body"))
        invoice.button_cancel()
        self._process_documents_web_services(invoice, {"cfdi_3_3"})
        self.assertEqual(invoice.edi_state, "cancelled", invoice.message_ids.mapped("body"))

    def test_cancel_02_sw(self):
        """Try to cancel an invoice with case 02 with Smart Web"""
        self.company.l10n_mx_edi_pac = "sw"
        self.company.l10n_mx_edi_pac_username = "luis_t@vauxoo.com"
        self.company.l10n_mx_edi_pac_password = "VAU.2021.SW"
        invoice = self.invoice
        invoice.action_post()
        self._process_documents_web_services(invoice, {"cfdi_3_3"})
        self.assertEqual(invoice.edi_state, "sent", invoice.message_ids.mapped("body"))
        invoice.l10n_mx_edi_cancellation = "02"
        invoice.button_cancel_posted_moves()
        self._process_documents_web_services(invoice, {"cfdi_3_3"})
        self.assertEqual(invoice.edi_state, "cancelled", invoice.message_ids.mapped("body"))

    def test_cancel_in_draft(self):
        """Ensure that draft invoice is cancelled correctly"""
        invoice = self.invoice
        invoice.button_cancel()
        self.assertEqual(invoice.state, "cancel", invoice.message_ids.mapped("body"))

    def test_invoice_reversal(self):
        """Ensure that draft invoice is cancelled correctly"""
        date_mx = self.env["l10n_mx_edi.certificate"].sudo().get_mx_current_datetime()
        invoice = self.invoice
        invoice.invoice_date = date_mx - timedelta(days=40)
        invoice.action_post()
        invoice.l10n_mx_edi_cancellation = "03"
        with self.assertRaisesRegex(UserError, "This option only could be used on invoices out of period."):
            invoice.button_cancel_with_reversal()

        invoice.search([("state", "=", "draft")]).unlink()
        invoice.company_id.fiscalyear_lock_date = date_mx.replace(day=1)
        invoice.button_cancel_with_reversal()
        self.assertTrue(invoice.reversal_move_id, invoice.message_ids.mapped("body"))
