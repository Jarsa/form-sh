# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    location_src_id = fields.Many2one(
        'stock.location', string='Raw Materials Location')
    location_dest_id = fields.Many2one(
        'stock.location', string='Finished Products Location')
