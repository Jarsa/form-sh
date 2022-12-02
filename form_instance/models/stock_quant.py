# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    quantity = fields.Float(
        digits='Product Unit of Measure',
        help='Quantity of products in this quant, in the default unit of measure of the product',
        readonly=True,
    )
    reserved_quantity = fields.Float(
        digits='Product Unit of Measure',
        default=0.0,
        help='Quantity of reserved products in this quant, in the default unit of measure of the product',
        readonly=True,
    )

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    categ_id = fields.Many2one(
        'product.category', related='product_id.categ_id', store=True)
