# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    subtotal = fields.Float(compute='_compute_subtotal', store=True)

    @api.multi
    @api.depends('quantity_done', 'price_unit')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity_done * rec.price_unit

    def _prepare_extra_move_vals(self, qty):
        res = super()._prepare_extra_move_vals(qty)
        if self.move_dest_ids:
            res['move_dest_ids'] = [(6, 0, self.move_dest_ids.ids)]
        return res

    def _action_assign(self):
        moves = self.filtered(
            lambda m: m.state in [
                'confirmed', 'waiting', 'partially_available'])
        for move in moves:
            done_moves = move.search([
                ('product_id', '=', move.product_id.id),
                ('location_dest_id', '=', move.location_id.id),
                ('state', '=', 'done'),
                ('move_dest_ids', 'not in', move.ids),
            ])
            if done_moves.filtered(
                    lambda m: m.mapped(
                        'move_dest_ids.state') in ['done', 'cancel']):
                for mv in done_moves:
                    if mv.availability > 0:
                        mv.write({
                            'move_dest_ids': [(6, 0, move.ids)]
                        })
        return super()._action_assign()


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    type_operation_line = fields.Selection(
        related='move_id.picking_code',
        store=True)
    price_unit = fields.Float(related='move_id.price_unit')
    subtotal = fields.Float(compute='_compute_subtotal')

    @api.multi
    @api.depends('qty_done', 'price_unit')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty_done * rec.price_unit
