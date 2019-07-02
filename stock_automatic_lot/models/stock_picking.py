# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _get_lot_sequence(self, active_model):
        if active_model == 'stock.picking' or active_model == 'purchase.order':
            lot_sequence = self.env.ref(
                'stock_automatic_lot.stock_production_lot_in_data')
        elif active_model == 'mrp.production':
            lot_sequence = self.env.ref(
                'stock_automatic_lot.stock_production_lot_manufacture_data')
        return lot_sequence

    @api.multi
    def button_validate(self):
        lot_obj = self.env['stock.production.lot']
        active_model = self._context['active_model']
        lot_sequence = self._get_lot_sequence(active_model)
        for ml in self.move_line_ids:
            if ml.product_id and ml.product_id.tracking != 'none':
                lot = lot_obj.create({
                    'name': lot_sequence.next_by_id(),
                    'product_id': ml.product_id.id,
                    'product_qty': ml.product_qty})
                ml.lot_id = lot.id
        return super().button_validate()
