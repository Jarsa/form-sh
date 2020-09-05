# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

round_method = round


class UomUom(models.Model):
    _inherit = 'uom.uom'

    @api.multi
    def _compute_quantity(
            self, qty, to_unit, round=True, rounding_method='UP',
            raise_if_failure=True):
        res = super()._compute_quantity(
            qty, to_unit, round, rounding_method, raise_if_failure)
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        return round_method(res, precision)

    @api.multi
    def _compute_price(self, price, to_unit):
        self.ensure_one()
        if not self or not price or not to_unit or self == to_unit:
            return price
        if self.category_id.id != to_unit.category_id.id:
            return price
        amount = price * self.factor
        if to_unit:
            amount = amount / to_unit.factor
        return amount
