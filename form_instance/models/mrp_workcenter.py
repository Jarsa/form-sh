# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpWorkcenter(models.Model):
    _name = 'mrp.workcenter'
    _inherit = ['mrp.workcenter', 'mail.thread']

    allow_start_production = fields.Boolean(string="Start Production")
