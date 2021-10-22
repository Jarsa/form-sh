# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StocKRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(
            self, product_id, product_qty, product_uom, location_id,
            name, origin, company_id, values, bom):
        res = super()._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name,
            origin, company_id, values, bom)
        if res.get('name'):
            res.pop('name')
        return res
