import base64
import io
from datetime import timedelta
from zipfile import ZipFile

from odoo.tests import Form, HttpCase, tagged


@tagged("post_install", "-at_install", "portal")
class TestPortal(HttpCase):
    def setUp(self):
        super().setUp()
        self.customer = self.env.ref("base.res_partner_3")
        self.product = self.env.ref("product.product_product_5")

        # Ensure the EDI format for CFDI is available in the default sales journal
        self.journal_sale = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        self.edi_format = self.env.ref("l10n_mx_edi.edi_cfdi_3_3")
        self.journal_sale.edi_format_ids |= self.edi_format

        self.env.company.sudo().search([("name", "=", "ESCUELA KEMPER URGATE")]).write(
            {"name": "ESCUELA KEMPER URGATE TEST"}
        )
        self.env.user.company_id.write(
            {
                "name": "ESCUELA KEMPER URGATE",
            }
        )

    def create_invoice(self, partner=None, invoice_type="out_invoice", **line_kwargs):
        if partner is None:
            partner = self.customer
        invoice = Form(self.env["account.move"].with_context(default_move_type=invoice_type))
        invoice.partner_id = partner
        invoice.l10n_mx_edi_payment_method_id = self.env.ref("l10n_mx_edi.payment_method_efectivo")
        invoice = invoice.save()
        self.create_inv_line(invoice, **line_kwargs)
        return invoice

    def create_inv_line(self, invoice, product=None, quantity=1, price=150):
        if product is None:
            product = self.product
        with Form(invoice) as inv:
            with inv.invoice_line_ids.new() as line:
                line.product_id = product
                line.quantity = quantity
                line.price_unit = price

    def _test_01_send_invoice_email(self):
        """Test sending an invoice by e-mail from the portal"""
        # Create a signed invoice
        invoice = self.create_invoice()
        invoice.action_post()
        invoice.action_process_edi_web_services()
        self.assertEqual(invoice.edi_state, "sent", invoice.edi_document_ids.mapped("error"))

        # Actually run the tour
        self.start_tour(
            url_path="/my/invoices",
            tour_name="mx_portal_send_mail",
            login=self.customer.email,
        )

        # Check that an email was sent, containing two attachments
        invoice_message = invoice.message_ids.filtered("attachment_ids")[0]
        self.assertIn("Please remit payment at your earliest convenience", invoice_message.body)
        self.assertEqual(len(invoice_message.attachment_ids), 2)

    def test_02_download_zipped_invoice(self):
        """Download a ZIP file of an invoice from the portal, containing XML and PDF"""
        # Create a signed invoice
        invoice = self.create_invoice()
        invoice.action_post()
        invoice.action_process_edi_web_services()
        self.assertEqual(invoice.edi_state, "sent", invoice.edi_document_ids.mapped("error"))

        # Actually run the tour
        self.start_tour(
            url_path="/my/invoices/%s" % invoice.id,
            tour_name="mx_portal_download_zipped_cfdi",
            login=self.customer.email,
        )

        # A ZIP file should've been created
        attachment_zip = self.env["ir.attachment"].search(
            [
                ("res_model", "=", invoice._name),
                ("res_id", "=", invoice.id),
                ("name", "=like", "%.zip"),
            ]
        )
        self.assertEqual(len(attachment_zip), 1, attachment_zip.mapped("name"))

        # Check ZIP content
        zip_content = base64.b64decode(attachment_zip.datas)
        with io.BytesIO(zip_content) as zip_bytes, ZipFile(zip_bytes) as zip_file:
            cfdi_filename = zip_file.namelist()[0]
            self.assertTrue(cfdi_filename.endswith(".xml"), cfdi_filename)

    def test_03_generate_invoice_from_so(self):
        """Test invoice generated from SO"""
        sale = self.env.ref("sale.sale_order_2")
        sale.order_line.product_id.write(
            {
                "invoice_policy": "order",
                "unspsc_code_id": self.ref("product_unspsc.unspsc_code_01010101"),
            }
        )
        sale = sale.copy({"partner_id": self.customer.id})
        sale.action_confirm()

        # Actually run the tour
        self.start_tour(
            url_path="/generate_invoice/%s" % sale.id,
            tour_name="mx_portal_generate_invoice",
            login=self.customer.email,
        )
        self.assertEqual(sale.invoice_status, "invoiced")

    def test_04_regenerate_invoice_from_so(self):
        """Test invoice regenerated from SO"""
        sale = self.env.ref("sale.sale_order_2")
        sale.order_line.product_id.write(
            {
                "invoice_policy": "order",
                "unspsc_code_id": self.ref("product_unspsc.unspsc_code_01010101"),
            }
        )
        sale = sale.copy({"partner_id": self.customer.id})
        sale.action_confirm()
        invoice = sale._create_invoices()
        invoice.invoice_date = sale.date_order - timedelta(days=35)
        invoice.sudo().action_post()

        # Actually run the tour a second time to regenerate
        self.start_tour(
            url_path="/generate_invoice/%s" % sale.id,
            tour_name="mx_portal_generate_invoice",
            login=self.customer.email,
        )
        self.assertEqual(len(sale.invoice_ids), 2, "Second invoice not generated.")
