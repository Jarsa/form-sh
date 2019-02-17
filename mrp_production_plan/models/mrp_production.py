# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    plan_id = fields.Many2one('mrp.production.plan', string="Production Plan")
