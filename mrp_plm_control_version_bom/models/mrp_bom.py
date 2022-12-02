# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    version = fields.Integer(default=0)
