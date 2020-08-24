# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ChangeAccountExpense(models.TransientModel):
    _name = 'change.account.expense'

    def _default_invoices(self):
        return self.env['account.invoice'].browse(
            self._context.get('active_ids'))

    account_id = fields.Many2one(
        'account.account',
    )
    invoice_ids = fields.Many2many(
        'account.invoice',
        default=_default_invoices,
    )

    def change_account_id(self):
        accounts = self.invoice_ids.mapped('invoice_line_ids.account_id')
        moves = self.invoice_ids.mapped('move_id')
        moves.button_cancel()
        self.invoice_ids.mapped('invoice_line_ids').write({
            'account_id': self.account_id.id,
        })
        self.invoice_ids.mapped('move_id.line_ids').filtered(
            lambda l: l.account_id in accounts).write({
                'account_id': self.account_id.id,
            })
        moves.post()
