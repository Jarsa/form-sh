# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    use_alternative_bom = fields.Boolean(
        string='Use Alternative BoM', readonly=True)
    has_multiple_boms = fields.Boolean(
        compute='_compute_has_multiple_boms',
        help='Technical field used to get if the product has multiple BoM')

    @api.depends('product_id')
    def _compute_has_multiple_boms(self):
        for rec in self:
            multiple_boms = False
            if len(rec.product_id.bom_ids) > 1:
                multiple_boms = True
            rec.has_multiple_boms = multiple_boms

    @api.model
    def create(self, vals):
        if (not vals.get('is_surplus', False) and not
                self._context.get('alternative_bom')):
            vals['bom_id'] = self._get_bom_id_with_stock(vals)
        return super().create(vals)

    @api.model
    def _get_bom_id_with_stock(self, vals):
        product = self.env['product.product'].browse(vals['product_id'])
        stock_location = self.env['stock.picking.type'].browse(
            vals['picking_type_id']).warehouse_id.lot_stock_id
        wip_location = self.env['stock.location'].browse(
            vals['location_src_id'])
        boms = self.env['mrp.bom'].search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)],
            order='sequence asc')
        for bom in boms:
            exploded_lines = bom.explode(product, vals['product_qty'])[1]
            components_available = self._is_all_components_available(
                exploded_lines, stock_location, wip_location)
            if components_available:
                return bom.id
            vals['use_alternative_bom'] = True
        vals['use_alternative_bom'] = False
        if not boms:
            raise UserError(
                _("The product %s don't have a BoM defined"))
        return boms[0].id

    @api.model
    def _is_all_components_available(
            self, exploded_lines, stock_location, wip_location):
        result = []
        for line in exploded_lines:
            product = line[0].product_id
            if product.bom_ids:
                result.append(True)
                continue
            stock_available = self.env['stock.quant']._get_available_quantity(
                product_id=product, location_id=stock_location)
            wip_available = self.env['stock.quant']._get_available_quantity(
                product_id=product, location_id=wip_location)
            total_available = stock_available + wip_available
            if line[1]['qty'] <= total_available:
                result.append(True)
            else:
                result.append(False)
        return all(result)
