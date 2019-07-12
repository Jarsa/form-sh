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

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super().purchase_order_change()
        lines = self.invoice_line_ids.filtered(lambda l: l.quantity == 0.0)
        self.invoice_line_ids -= lines
        return res
