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
        readonly=False,
        tracking=True,
        help="The document(s) that generated the invoice.",
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

    def _collect_tax_cash_basis_values(self):
        """ Replace the original Odoo method in order to fix an issue related with DIOT
        task#10684 opw#2790754.
        The onluy change is the line below:
            elif not line.tax_exigible and not line.reconciled:
        Changed to:
            elif not line.tax_exigible and (not line.reconciled or line.account_id.id == 18):
        """
        self.ensure_one()
        values = {
            'move': self,
            'to_process_lines': self.env['account.move.line'],
            'total_balance': 0.0,
            'total_residual': 0.0,
            'total_amount_currency': 0.0,
            'total_residual_currency': 0.0,
        }

        currencies = set()
        has_term_lines = False
        for line in self.line_ids:
            if line.account_internal_type in ('receivable', 'payable'):
                sign = 1 if line.balance > 0.0 else -1

                currencies.add(line.currency_id or line.company_currency_id)
                has_term_lines = True
                values['total_balance'] += sign * line.balance
                values['total_residual'] += sign * line.amount_residual
                values['total_amount_currency'] += sign * line.amount_currency
                values['total_residual_currency'] += sign * line.amount_residual_currency

            elif not line.tax_exigible and (not line.reconciled or line.account_id.id == 18):

                values['to_process_lines'] += line
                currencies.add(line.currency_id or line.company_currency_id)

        if not values['to_process_lines'] or not has_term_lines:
            return None

        # Compute the currency on which made the percentage.
        if len(currencies) == 1:
            values['currency'] = list(currencies)[0]
        else:
            # Don't support the case where there is multiple involved currencies.
            return None

        # Determine is the move is now fully paid.
        values['is_fully_paid'] = self.company_id.currency_id.is_zero(values['total_residual']) \
            or values['currency'].is_zero(values['total_residual_currency'])

        return values


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
