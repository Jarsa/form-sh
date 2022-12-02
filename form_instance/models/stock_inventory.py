# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def _get_inventory_lines_values(self):
        vals = super()._get_inventory_lines_values()
        product_model = self.env['product.product']
        for val in vals:
            product = product_model.browse(val['product_id'])
            val['cost'] = product.standard_price
        return vals

    def action_validate(self):
        lines = self.line_ids
        for line in lines:
            teorical_qty = line.theoretical_qty
            real_qty = line.product_qty
            line_cost = line.cost
            product_cost = line.product_id.standard_price
            if (teorical_qty != real_qty and line_cost != product_cost):
                line.product_id.write({
                    'standard_price': line_cost
                })
        return super().action_validate()


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    cost = fields.Float()
