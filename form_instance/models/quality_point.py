# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class QualityPoint(models.Model):
    _inherit = 'quality.point'

    routing2_id = fields.Many2one('mrp.routing', 'Routing')
