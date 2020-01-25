# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo.tests.common import TransactionCase


class SaleOrderInvoiceMerge(TransactionCase):

    def setUp(self):
        super(SaleOrderInvoiceMerge, self).setUp()
        self.product = self.env.ref('product.product_product_16')
        self.partner_id = self.env.ref('base.res_partner_2').id

    def create_sale_order(self, qty):
        order = self.env['sale.order'].create({
            'partner_id': self.partner_id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.display_name,
                'product_uom_qty': qty,
                'price_unit': 100.0,
            })]
        })
        order.action_confirm()
        return order

    def create_wizard(self, orders):
        wiz_obj = self.env['sale.advance.payment.inv']
        context = {
            'active_ids': orders.ids,
            'open_invoices': True,
        }
        return wiz_obj.with_context(context).create({
            'advance_payment_method': 'delivered'
        })

    def test_01_sale_order_invoice_merge(self):
        order1 = self.create_sale_order(1.0)
        order2 = self.create_sale_order(2.0)
        wiz = self.create_wizard(order1 + order2)
        result = wiz.create_invoices()
        invoice = self.env['account.invoice'].browse(result['res_id'])
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 3.0)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped('price_unit')), 100.0)
        self.assertEqual(
            sum(invoice.invoice_line_ids.mapped('price_subtotal')), 300.0)
