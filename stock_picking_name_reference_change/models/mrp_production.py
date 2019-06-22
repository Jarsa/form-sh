# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        res = super().create(values)
        product_name = res.product_tmpl_id.name
        default_code = res.product_tmpl_id.default_code
        units = '%s %s' % (res.product_qty, res.product_uom_id.name)
        if res.product_tmpl_id.description_purchase:
            product_name = res.product_tmpl_id.description_purchase
        for rec in res.picking_ids:
            rec.origin = '%s - [%s] %s - %s' % (
                rec.origin, default_code, product_name, units)
        return res
