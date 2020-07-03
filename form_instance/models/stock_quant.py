# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    quantity = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Quantity of products in this quant, in the default unit of measure of the product',
        readonly=True, required=True, oldname='qty')
    reserved_quantity = fields.Float(
        'Reserved Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=0.0,
        help='Quantity of reserved products in this quant, in the default unit of measure of the product',
        readonly=True, required=True)
    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    categ_id = fields.Many2one(
        'product.category', related='product_id.categ_id', store=True)

    @api.model
    def _update_quants_and_reserve_all(self):
        for rec in self:
            domain = [
                ('product_id', '=', rec.product_id.id), '|',
                ('location_id', '=', rec.location_id.id),
                ('location_dest_id', '=', rec.location_id.id),
                ('lot_id', '=', rec.lot_id.id), '|',
                ('package_id', '=', rec.package_id.id),
                ('result_package_id', '=', rec.package_id.id)]
            lines = self.env['stock.move.line'].search(domain)
            output = 0
            inputl = 0
            reserved_quantity = 0
            for line in lines:
                if line.location_id == rec.location_id and (
                        line.state == 'done'):
                    output += line.qty_done
                if line.location_dest_id == rec.location_id and (
                        line.state == 'done'):
                    inputl += line.qty_done
                if line.location_id == rec.location_id and (
                        line.product_uom_qty > 0.0):
                    reserved_quantity += line.product_uom_qty
            rec.write({
                'quantity': inputl - output,
                'reserved_quantity': reserved_quantity,
            })
