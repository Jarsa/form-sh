# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    update_reason = fields.Many2one('mrp.production.update.reason')
