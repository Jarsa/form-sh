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
            origin_order = self._get_recursively_origin_mo(rec)
            origin_mo = ''
            if origin_order != rec:
                origin_name = origin_order.name
                origin_product_name = origin_order.product_tmpl_id.name
                origin_default_code = origin_order.product_tmpl_id.default_code
                origin_units = '%s %s' % (
                    origin_order.product_qty, origin_order.product_uom_id.name)
                origin_mo = '%s - [%s] %s - %s' % (
                    origin_name, origin_default_code, origin_product_name,
                    origin_units)
            product_name = rec.product_tmpl_id.name
            default_code = rec.product_tmpl_id.default_code
            units = '%s %s' % (rec.product_qty, rec.product_uom_id.name)
            if rec.product_tmpl_id.description_purchase:
                product_name = rec.product_tmpl_id.description_purchase
            for picking in rec.picking_ids:
                picking.write({
                    'origin': '%s - [%s] %s - %s' % (
                        rec.name, default_code, product_name, units),
                    'origin_mo': origin_mo if origin_mo else False,
                    'production_id': rec.id,
                })

    @api.multi
    def _get_recursively_origin_mo(self, order):
        prefix = order.picking_type_id.sequence_id.prefix
        origin = order.origin if order.origin else ''
        if prefix in origin:
            parent_order = self.search([('name', '=', origin)])
            return self._get_recursively_origin_mo(parent_order)
        return order
