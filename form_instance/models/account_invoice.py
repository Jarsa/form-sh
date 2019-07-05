# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    authorized = fields.Boolean(default=False)

    @api.multi
    def authorize_cancelation(self):
        self.authorized = True

    @api.multi
    def cancel_cancelation(self):
        self.authorized = False
