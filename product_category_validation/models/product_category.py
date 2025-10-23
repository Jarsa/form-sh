# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    validation_ids = fields.One2many('product.category.validation', 'categ_id')
    is_kit = fields.Boolean()
