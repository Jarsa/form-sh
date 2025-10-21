import base64

from lxml.objectify import fromstring

from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestMxEdiTrasladoInvoice(TestMxEdiCommon):
    def test_traslado_invoice(self):
        self.certificate._check_credentials()
        company = self.invoice.company_id
        self.invoice.partner_id = company.partner_id
        self.invoice.partner_id.l10n_mx_edi_fiscal_regime = "616"
        self.invoice.currency_id = self.invoice.company_currency_id
        self.invoice.invoice_date = False
        move_form = Form(self.invoice)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.product_uom_id = self.invoice.invoice_line_ids.product_id.uom_id
            line_form.price_unit = 0.0
            line_form.quantity = 1
            line_form.tax_ids.clear()
        move_form.save()
        self.invoice.action_post()
        self.env["account.edi.document"].sudo().with_context(edi_test_mode=False).search(
            [("state", "in", ("to_send", "to_cancel"))]
        )._process_documents_web_services()
        self.assertEqual(self.invoice.edi_state, "sent", self.invoice.edi_document_ids.mapped("error"))
        xml = fromstring(
            base64.decodebytes(
                self.invoice._get_l10n_mx_edi_signed_edi_document().attachment_id.with_context(bin_size=False).datas
            )
        )
        self.assertEqual(xml.get("TipoDeComprobante"), "T")
        self.assertEqual(xml.get("Total"), "0.00")
        self.assertEqual(xml.Conceptos.Concepto[0].get("Descripcion"), "TRASLADO DE MERCANCIAS product_mx")
