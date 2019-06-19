# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        res = super().create(values)
        product_name = res.product_tmpl_id.name
        if res.product_tmpl_id.description_purchase:
            product_name = res.product_tmpl_id.description_purchase
        for rec in res.picking_ids:
            rec.origin = '%s - [%s] %s' % (
                rec.origin, rec.product_id.default_code, product_name)
        return res
