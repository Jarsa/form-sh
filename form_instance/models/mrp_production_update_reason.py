# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpProductionUpdateReason(models.Model):
    _name = 'mrp.production.update.reason'

    name = fields.Char(required=True)
