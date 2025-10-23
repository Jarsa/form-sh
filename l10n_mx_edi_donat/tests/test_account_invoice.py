from lxml.objectify import fromstring

from odoo.tests import tagged

from odoo.addons.l10n_mx_edi_40.tests.common import TestMxEdiCommon


@tagged("post_install", "-at_install")
class TestL10nMxEdiInvoiceDonat(TestMxEdiCommon):
    def test_l10n_mx_edi_invoice_donat(self):
        self.certificate._check_credentials()
        self.namespaces = {"donat": "http://www.sat.gob.mx/donat"}
        self.env.company.sudo().search([("name", "=", "ESCUELA KEMPER URGATE")]).write(
            {"name": "ESCUELA KEMPER URGATE TEST"}
        )
        self.env.user.company_id.write(
            {
                "name": "ESCUELA KEMPER URGATE",
            }
        )
        self.partner_a.write(
            {
                "l10n_mx_edi_donations": True,
            }
        )
        self.invoice.company_id.write(
            {
                "l10n_mx_edi_donat_auth": "12345",
                "l10n_mx_edi_donat_date": "2017-01-23",
                "l10n_mx_edi_donat_note": "Este comprobante ampara un donativo,"
                " el cual será destinado por la donataria a los fines propios de"
                " su objeto social. En el caso de que los bienes donados hayan"
                " sido deducidos previamente para los efectos del impuesto sobre"
                " la renta, este donativo no es deducible.",
            }
        )
        invoice = self.invoice
        invoice.action_post()
        generated_files = self._process_documents_web_services(self.invoice, {"cfdi_3_3"})
        self.assertTrue(generated_files)
        self.assertEqual(invoice.edi_state, "sent", invoice.message_ids.mapped("body"))
        xml = fromstring(generated_files[0])
        scp = xml.Complemento.xpath("//donat:Donatarias", namespaces=self.namespaces)
        self.assertTrue(scp, "Complement to Donatarias not added correctly")
