# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _merge_line_qty(self, moves):
        for move in moves:
            products = move.invoice_line_ids.mapped('product_id')
            lines_to_update = []
            for product in products:
                lines = move.invoice_line_ids.filtered(
                    lambda l: l.product_id.id == product.id)
                if len(lines) > 1:
                    lines_to_update.append((1, lines[0].id, {
                        'quantity': sum(lines.mapped('quantity')),
                        'sale_line_ids': [
                            (6, 0, lines.mapped('sale_line_ids').ids)],
                    }))
                    lines_to_update.extend([(2, line.id, 0) for line in lines[1:]])
            if lines_to_update:
                move.write({
                    'invoice_line_ids': lines_to_update,
                })
                move._onchange_invoice_line_ids()

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped, final, date)
        self._merge_line_qty(moves)
        return moves
