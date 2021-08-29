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

    def authorize_cancelation(self):
        self.authorized = True

    def cancel_cancelation(self):
        self.authorized = False

    def copy(self, default=None):
        for rec in self:
            if rec.move_type != 'entry':
                raise UserError(
                    _('You cannot duplicate invoices'))
        return super().copy(default)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        related='product_id.categ_id')

    def write(self, values):
        fields_blocked = ['quantity', 'price_unit', 'tax_ids']
        allow_write = not self._context.get('allow_write', False)
        if self.user_has_groups(
                'form_instance.group_allow_edit_invoices') and allow_write:
            for rec in fields_blocked:
                if rec in values:
                    raise UserError(_(
                        'You are not allowed to edit price, quantity or taxes')
                    )
        return super().write(values)
