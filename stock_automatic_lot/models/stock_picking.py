# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _get_lot_name(self, active_model):
        if active_model in ['stock.picking', 'purchase.order']:
            lot_sequence = self.env.ref(
                'stock_automatic_lot.stock_production_lot_in_data')
        elif active_model in ['mrp.production', 'mrp.workorder']:
            lot_sequence = self.env.ref(
                'stock_automatic_lot.stock_production_lot_manufacture_data')
        return lot_sequence.next_by_id()

    @api.multi
    def button_validate(self):
        lot_obj = self.env['stock.production.lot']
        for ml in self.move_line_ids.filtered(lambda ml: not ml.lot_id):
            if ml.product_id.tracking != 'none':
                lot = lot_obj.create({
                    'name': self._get_lot_name('stock.picking'),
                    'product_id': ml.product_id.id,
                    'product_qty': ml.product_qty})
                ml.lot_id = lot.id
        return super().button_validate()
