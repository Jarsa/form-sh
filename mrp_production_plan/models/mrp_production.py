# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    plan_line_id = fields.Many2one(
        'mrp.production.plan.line', string="Production Plan Line")
    plan_id = fields.Many2one(
        'mrp.production.plan', string="Production Plan",
    )
    has_multiple_routing = fields.Boolean(
        compute='_compute_has_multiple_routing',
        help='Technical field used to validate if the product have multiple'
             ' routings.'
    )

    @api.depends('product_id')
    def _compute_has_multiple_routing(self):
        for rec in self:
            multiple_routing = False
            if len(rec.product_id.routing_ids) > 1:
                multiple_routing = True
            rec.has_multiple_routing = multiple_routing
