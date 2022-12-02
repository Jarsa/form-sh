# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def write(self, values):
        name_user = self.env.user.name
        fields_blocked = ['quantity', 'price_unit', 'tax_ids']
        if not self.user_has_groups(
                'sale_request.group_edit_account_invoice_line_price'):
            for rec in fields_blocked:
                if rec in values:
                    raise UserError(
                        _('The user %s can not permission to edit the price'
                            'unit, quantity and taxes') % name_user)
        return super().write(values)
