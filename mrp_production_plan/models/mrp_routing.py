# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    product_id = fields.Many2one(
        'product.product', required=True, domain=[('bom_ids', '!=', False)])
