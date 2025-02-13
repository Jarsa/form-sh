# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=redefined-builtin

from odoo import models

round_method = round


class UomUom(models.Model):
    _inherit = 'uom.uom'

    def _compute_quantity(
            self, qty, to_unit, round=True, rounding_method='UP',
            raise_if_failure=True):
        res = super()._compute_quantity(
            qty, to_unit, round, rounding_method, raise_if_failure)
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        return round_method(res, precision)
