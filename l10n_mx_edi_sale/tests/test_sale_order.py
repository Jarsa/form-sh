from odoo.tests.common import TransactionCase


class TestPartnerDefault(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_product_16')
        self.partner.l10n_mx_edi_payment_method_id = self.env.ref(
            'l10n_mx_edi.payment_method_tarjeta_de_credito')
        self.partner.l10n_mx_edi_usage = 'G03'
        self.order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.display_name,
                'product_uom_qty': 1,
                'product_uom': self.product.uom_id.id,
                'price_unit': 100,
            })]
        })

    def test_partner_default(self):
        """Ensure that partner defaults are assigned"""
        order = self.order
        partner = order.partner_id.commercial_partner_id.sudo()
        order._onchange_partner_id()
        self.assertEqual(
            order.l10n_mx_edi_payment_method_id, partner.l10n_mx_edi_payment_method_id,
            'Payment method not assigned correctly')
        self.assertEqual(
            order.l10n_mx_edi_usage, partner.l10n_mx_edi_usage,
            'Usage not assigned correctly')

    def test_order_to_invoice(self):
        """Ensure that values are transfered to invoices"""
        order = self.order
        order._onchange_partner_id()
        order.action_confirm()
        ctx = {
            'active_id': order.id,
            'active_ids': order.ids,
            'active_model': 'sale.order',
            'open_invoices': True,
        }
        wiz = self.env['sale.advance.payment.inv'].with_context(ctx).create({
            'advance_payment_method': 'delivered',
        })
        res = wiz.create_invoices()
        invoice = self.env['account.move'].browse(res['res_id'])
        self.assertEqual(
            invoice.l10n_mx_edi_payment_method_id,
            self.partner.l10n_mx_edi_payment_method_id,
            'Payment method not assigned correctly')
        self.assertEqual(
            invoice.l10n_mx_edi_usage, self.partner.l10n_mx_edi_usage,
            'Usage not assigned correctly')

    def test_order_to_invoice_with_advance(self):
        """Ensure that values are transfered to invoices"""
        order = self.order
        order._onchange_partner_id()
        order.action_confirm()
        ctx = {
            'active_id': order.id,
            'active_ids': order.ids,
            'active_model': 'sale.order',
            'open_invoices': True,
        }
        wiz = self.env['sale.advance.payment.inv'].with_context(ctx).create({
            'advance_payment_method': 'fixed',
            'fixed_amount': 50.0,
        })
        res = wiz.create_invoices()
        invoice = self.env['account.move'].browse(res['res_id'])
        self.assertEqual(
            invoice.l10n_mx_edi_payment_method_id,
            self.partner.l10n_mx_edi_payment_method_id,
            'Payment method not assigned correctly')
        self.assertEqual(
            invoice.l10n_mx_edi_usage, self.partner.l10n_mx_edi_usage,
            'Usage not assigned correctly')
