# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity',
                 'invoice_lines.sibling_invoice_id.state')
    def _get_invoice_qty(self):
        for line in self:
            qty_invoiced = 0.0
            line_name = line.order_id.name
            inv = self.env['account.invoice'].search([
                ('origin', 'ilike', line_name), ('state', '!=', 'cancel')])
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'out_invoice' or inv:
                            qty_invoiced = line.product_uom_qty
                    elif invoice_line.invoice_id.type == 'out_refund':
                        qty_invoiced -= invoice_line.uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom)
                if inv.state == 'cancel':
                        qty_invoiced = 0.0
            line.qty_invoiced = qty_invoiced
