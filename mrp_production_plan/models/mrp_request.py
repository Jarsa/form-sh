# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


class MrpRequest(models.Model):
    _inherit = 'mrp.request'

    plan_line_id = fields.Many2one(
        'mrp.production.plan.line',
        string="Production Plan Line",
        copy=False,
    )
    plan_id = fields.Many2one(
        'mrp.production.plan', string="Production Plan",
        related="plan_line_id.plan_id",
        store=True,
    )
