from odoo.tests.common import TransactionCase


class TestPartnerDefault(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_product_16')
        self.partner.l10n_mx_edi_payment_method_id = self.env.ref(
            'l10n_mx_edi.payment_method_tarjeta_de_credito')
        self.partner.l10n_mx_edi_usage = 'G03'
        self.location_id = self.env.ref('stock.stock_location_stock').id
        self.production_loc = self.env['stock.location'].search(
            [('usage', '=', 'production')], limit=1)
        self.order = self.env['repair.order'].create({
            'partner_id': self.partner.id,
            'invoice_method': 'b4repair',
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.location_id,
            'operations': [(0, 0, {
                'type': 'add',
                'product_id': self.product.id,
                'name': self.product.display_name,
                'product_uom_qty': 1,
                'product_uom': self.product.uom_id.id,
                'price_unit': 100,
                'location_id': self.location_id,
                'location_dest_id': self.production_loc.id,
            })]
        })

    def test_partner_default(self):
        """Ensure that partner defaults are assigned"""
        order = self.order
        partner = order.partner_id.commercial_partner_id.sudo()
        order._onchange_partner_id_invoice_method()
        self.assertEqual(
            order.l10n_mx_edi_payment_method_id,
            partner.l10n_mx_edi_payment_method_id,
            'Payment method not assigned correctly')
        self.assertEqual(
            order.l10n_mx_edi_usage, partner.l10n_mx_edi_usage,
            'Usage not assigned correctly')

    def test_order_to_invoice(self):
        """Ensure that values are transfered to invoices"""
        order = self.order
        order._onchange_partner_id_invoice_method()
        order.action_validate()
        order.action_repair_invoice_create()
        if not order.invoice_id:
            order.action_repair_invoice_create()
        invoice = order.invoice_id
        self.assertEqual(
            invoice.l10n_mx_edi_payment_method_id,
            self.partner.l10n_mx_edi_payment_method_id,
            'Payment method not assigned correctly')
        self.assertEqual(
            invoice.l10n_mx_edi_usage, self.partner.l10n_mx_edi_usage,
            'Usage not assigned correctly')
