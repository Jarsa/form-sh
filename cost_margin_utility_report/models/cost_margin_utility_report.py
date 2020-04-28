# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CostMarginUtilityReport(models.Model):
    _name = 'cost.margin.utility.report'
    _description = 'This model creates a cost margin utility report'

    product_id = fields.Many2one('product.product', readonly=True)
    product_category_id = fields.Many2one(
        'product.category', readonly=True)
    product_description = fields.Text(readonly=True)
    sold_qty = fields.Float(readonly=True)
    total_sale = fields.Float(readonly=True)
    total_cost = fields.Float(readonly=True)
    unit_cost = fields.Float(readonly=True)
    contribution = fields.Float(readonly=True)
    margin = fields.Float(readonly=True)
    reference = fields.Char(readonly=True)
    default_code = fields.Char(readonly=True)
    form_id = fields.Char(readonly=True)
