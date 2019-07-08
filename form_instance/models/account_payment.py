# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    ref = fields.Char(
        string='Reference',
        related='partner_id.ref',
    )
