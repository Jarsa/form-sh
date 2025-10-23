# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.model
    def create(self, values):
        values['final_lot_id'] = self._get_lot_id(values)
        return super().create(values)

    @api.model
    def _get_lot_id(self, values):
        production = self.env['mrp.production'].browse(values['production_id'])
        if production.product_id.tracking == 'none':
            return False
        if not production.workorder_ids:
            lot = self.env['stock.production.lot'].create({
                'product_id': production.product_id.id,
                'name': self.env['stock.picking']._get_lot_name(self._name)
            })
        else:
            lot = production.workorder_ids.mapped('final_lot_id')
        return lot.id

    def open_tablet_view(self):
        res = super().open_tablet_view()
        last_step = False
        processed_moves = self.env['stock.move.line']
        while not last_step:
            moves = self.move_line_ids.filtered(
                lambda m: m.state not in ('done', 'cancel') and
                m.product_id == self.component_id and
                m not in processed_moves)
            if moves:
                self.write({
                    'lot_id': moves[0].lot_id.id,
                    'qty_done': moves[0].product_qty,
                })
                processed_moves |= moves[0]
            last_step = self.is_last_step
            if not last_step:
                self.action_next()
        return res
