# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    authorized = fields.Boolean(
        default=False,
        tracking=True,
    )
    invoice_origin = fields.Char(
        string='Origin',
        tracking=True,
        help="The document(s) that generated the invoice.",
    )

    def authorize_cancelation(self):
        """Authorize the cancellation of an invoice"""
        if not self.user_has_groups('account.group_account_manager'):
            raise UserError(_("You don't have permission to authorize cancellation."))
        self.write({'authorized': True})

    def cancel_cancelation(self):
        """Cancel the authorization of cancellation"""
        if not self.user_has_groups('account.group_account_manager'):
            raise UserError(_("You don't have permission to cancel the cancellation."))
        self.write({'authorized': False})

    def copy(self, default=None):
        """Restrict invoice duplication unless it is a journal entry"""
        if self.move_type != 'entry':
            raise UserError(_('You cannot duplicate invoices.'))
        return super().copy(default)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        related='product_id.categ_id',
        store=True,
    )

    def write(self, values):
        """Restrict editing of certain fields unless user has the required permissions"""
        restricted_fields = ['quantity', 'price_unit', 'tax_ids']
        allow_edit = self._context.get('allow_write', False)

        if not allow_edit and self.user_has_groups('form_instance.group_allow_edit_invoices'):
            for field in restricted_fields:
                if field in values:
                    raise UserError(
                        _('You are not allowed to edit price, quantity, or taxes.')
                    )
        return super().write(values)
