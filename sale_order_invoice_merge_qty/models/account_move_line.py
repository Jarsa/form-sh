# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sibling_invoice_id = fields.Many2one('account.move')
