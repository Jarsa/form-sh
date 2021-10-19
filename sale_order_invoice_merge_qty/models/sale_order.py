# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _merge_line_qty(self, invoice_ids):
        invoices = self.env['account.move'].browse(invoice_ids)
        for invoice in invoices:
            products = invoice.invoice_line_ids.mapped('product_id')
            for product in products:
                lines = invoice.invoice_line_ids.filtered(
                    lambda l: l.product_id.id == product.id)
                if len(lines) > 1:
                    context = self._context.copy()
                    context['allow_write'] = True
                    lines[0].with_context(**context).write({
                        'quantity': sum(lines.mapped('quantity')),
                        'sale_line_ids': [
                            (6, 0, lines.mapped('sale_line_ids').ids)],
                    })
                    lines[1:].unlink()

    def action_invoice_create(self, grouped=False, final=False):
        res = super().action_invoice_create(grouped, final)
        self._merge_line_qty(res)
        return res
