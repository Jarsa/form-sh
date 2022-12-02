# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    def do_produce(self):
        lot_obj = self.env['stock.production.lot']
        picking_obj = self.env['stock.picking']
        active_model = self._context['active_model']
        lot = lot_obj.create({
            'name': picking_obj._get_lot_name(active_model),
            'product_id': self.product_id.id,
            'product_qty': self.product_qty})
        self.lot_id = lot.id
        return super().do_produce()
