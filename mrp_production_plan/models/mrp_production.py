# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).
# pylint: disable=R1729

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    plan_line_id = fields.Many2one(
        'mrp.production.plan.line',
        string="Production Plan Line",
        copy=False,
    )
    plan_id = fields.Many2one(
        'mrp.production.plan',
        string="Production Plan",
        copy=False,
    )
    raw_material_full_reserved = fields.Boolean(
        compute="_compute_raw_material_full_reserved",
        help="Technical field used to know if all the raw materials are reserved in a MO.",
    )

    @api.depends("move_raw_ids.state")
    def _compute_raw_material_full_reserved(self):
        for rec in self:
            rec.raw_material_full_reserved = all(
                [state == "assigned" for state in rec.move_raw_ids.mapped("state")])
