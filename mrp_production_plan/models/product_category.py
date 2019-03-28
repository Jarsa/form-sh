# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    use_in_plan = fields.Boolean()
