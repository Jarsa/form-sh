# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        external_product = False
        default_code = vals.get('default_code') or ''
        if 'CMP-D' in default_code:
            external_product = self.env[
                'product.template'].search(
                    [('default_code', '=', 'CMP-SD-0144')], limit=1)
        elif 'CMP-C' in default_code:
            external_product = self.env[
                'product.template'].search(
                    [('default_code', '=', 'CMP-SC-0145')], limit=1)
        if external_product:
            sequences = self.env['mrp.bom'].with_context(
                active_test=False).search([
                    ('product_tmpl_id', '=', external_product.id),
                ], order='sequence asc').mapped('sequence')
            sequence = sequences[-1] + 1 if sequences else 1
            self.env['mrp.bom'].sudo().create({
                'product_tmpl_id': external_product.id,
                'is_surplus': True,
                'type': 'normal',
                'product_qty': 1.0,
                'product_uom_id': external_product.uom_id.id,
                'code': '[%s] %s' % (
                    res.product_variant_id.default_code,
                    res.product_variant_id.name),
                'sequence': sequence,
                'bom_line_ids': [(0, 0, {
                    'product_id': res.product_variant_id.id,
                    'product_qty': 1.0,
                    'product_uom': res.product_variant_id.uom_id.id,
                })],
            })
        return res
