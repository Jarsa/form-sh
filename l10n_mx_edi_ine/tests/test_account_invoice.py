import os

from lxml.objectify import fromstring

from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.tools import misc

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestL10nMxEdiInvoiceINE(TestMxEdiCommon):
    def create_invoice_ine_line(self, invoice_id):
        invoice_ine_line_model = self.env["l10n_mx_edi_ine.entity"]
        self.country = self.env["res.country"].search([("code", "=", "MX")])
        state = self.env["res.country.state"].search([("code", "=", "COL"), ("country_id", "=", self.country.id)])
        lines2create = []
        ine_line = invoice_ine_line_model.new(
            {
                "l10n_mx_edi_ine_entity_id": state.id,
                "l10n_mx_edi_ine_scope": "local",
                "l10n_mx_edi_ine_accounting": "789",
                "invoice_id": invoice_id,
            }
        )
        ine_line_dict = ine_line._convert_to_write({name: ine_line[name] for name in ine_line._cache})
        lines2create.append((0, 0, ine_line_dict))
        ine_line = invoice_ine_line_model.new(
            {
                "l10n_mx_edi_ine_entity_id": state.id,
                "l10n_mx_edi_ine_scope": "local",
                "l10n_mx_edi_ine_accounting": "123,456",
                "invoice_id": invoice_id,
            }
        )
        ine_line_dict = ine_line._convert_to_write({name: ine_line[name] for name in ine_line._cache})
        lines2create.append((0, 0, ine_line_dict))
        invoice_ine_line_model.create(ine_line_dict)

    def test_l10n_mx_edi_simple_ine(self):
        self.certificate._check_credentials()
        xml_expected_simple_str = (
            misc.file_open(os.path.join("l10n_mx_edi_ine", "tests", "expected_simple_ine.xml")).read().encode("UTF-8")
        )
        invoice = self.invoice
        invoice.currency_id = self.env.ref("base.MXN")
        invoice.company_id.sudo().name = "YourCompany INE"
        invoice.l10n_mx_edi_ine_process_type = "ordinary"
        invoice.l10n_mx_edi_ine_committee_type = "national_executive"
        invoice.l10n_mx_edi_ine_accounting = "123456"
        move_form = Form(invoice)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.tax_ids.clear()
        move_form.save()
        invoice.action_post()
        generated_files = self._process_documents_web_services(self.invoice, {"cfdi_3_3"})
        self.assertTrue(generated_files)
        self.assertEqual(invoice.edi_state, "sent", invoice.message_ids.mapped("body"))
        xml = fromstring(generated_files[0])
        namespaces = {"ine": "http://www.sat.gob.mx/ine"}
        ine = xml.Complemento.xpath("//ine:INE", namespaces=namespaces)
        self.assertTrue(ine, "Complement to INE not added correctly")
        xml_expected = fromstring(xml_expected_simple_str)
        self.assertXmlTreeEqual(xml, xml_expected)

    def test_l10n_mx_edi_complex_ine(self):
        self.certificate._check_credentials()
        xml_expected_complex_str = (
            misc.file_open(os.path.join("l10n_mx_edi_ine", "tests", "expected_complex_ine.xml")).read().encode("UTF-8")
        )
        invoice = self.invoice
        invoice.currency_id = self.env.ref("base.MXN")
        invoice.company_id.sudo().name = "YourCompany INE"
        self.create_invoice_ine_line(invoice.id)
        invoice.l10n_mx_edi_ine_process_type = "precampaign"
        move_form = Form(invoice)
        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.tax_ids.clear()
        move_form.save()
        invoice.action_post()
        generated_files = self._process_documents_web_services(self.invoice, {"cfdi_3_3"})
        self.assertTrue(generated_files)
        self.assertEqual(invoice.edi_state, "sent", invoice.message_ids.mapped("body"))
        xml = fromstring(generated_files[0])
        namespaces = {"ine": "http://www.sat.gob.mx/ine"}
        ine = xml.Complemento.xpath("//ine:INE", namespaces=namespaces)
        self.assertTrue(ine, "Complement to INE not added correctly")
        xml_expected = fromstring(xml_expected_complex_str)
        self.assertXmlTreeEqual(xml, xml_expected)
