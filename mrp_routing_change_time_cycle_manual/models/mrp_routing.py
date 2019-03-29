# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    time_cycle_manual = fields.Float(
        'Manual Duration', default=60,
        help="""Time in minutes. Is the time used in manual
        mode, or the first time supposed in real time when
        there are not any work orders yet.""",
        digits=(3, 6))
    time_cycle = fields.Float(
        'Duration', compute="_compute_time_cycle",
        digits=(3, 6))
