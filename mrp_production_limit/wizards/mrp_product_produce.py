# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        self._check_qty_to_produce()
        return super()._onchange_product_qty()

    @api.multi
    def do_produce(self):
        self._check_qty_to_produce()
        return super().do_produce()

    @api.multi
    def _check_qty_to_produce(self):
        self.ensure_one()
        order_id = self._context.get('active_id')
        order = self.env['mrp.production'].browse(order_id)
        quantity = order.product_qty
        qty_produced = order.qty_produced
        # create a instance of this module
        # only to can use this method and
        # no repeat code
        workorder = self.env['mrp.workorder']
        workorder._calcule_limit_production(
            quantity, qty_produced)
