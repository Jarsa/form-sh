# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpRequest(models.Model):
    _inherit = 'mrp.request'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    product_category_id = fields.Many2one(
        'product.category', related='product_id.categ_id')
