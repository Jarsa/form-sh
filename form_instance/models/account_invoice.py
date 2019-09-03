# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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

    @api.multi
    def copy(self, default=None):
        raise UserError(
            _('The user can not duplicate the invoices'))
        return super().copy(default)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def write(self, values):
        name_user = self.env.user.name
        fields_blocked = ['quantity', 'price_unit', 'invoice_line_tax_ids']
        if self.user_has_groups(
                'form_instance.group_allow_edit_invoices'):
            for rec in fields_blocked:
                if rec in values:
                    raise UserError(
                        _(
                            '%s is not allowed to edit price'
                            'unit, quantity or taxes'
                        ) % name_user
                    )
        return super().write(values)
