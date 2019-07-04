# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        res = super().create(values)
        res._process_picking_origin()
        return res

    @api.multi
    def _process_picking_origin(self):
        for rec in self:
            product_name = rec.product_tmpl_id.name
            default_code = rec.product_tmpl_id.default_code
            units = '%s %s' % (rec.product_qty, rec.product_uom_id.name)
            if rec.product_tmpl_id.description_purchase:
                product_name = rec.product_tmpl_id.description_purchase
            for rec in rec.picking_ids:
                rec.origin = '%s - [%s] %s - %s' % (
                    rec.origin, default_code, product_name, units)
