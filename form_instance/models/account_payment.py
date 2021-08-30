# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    partner_ref = fields.Char(
        string='Partner Reference',
        related='partner_id.ref',
    )

    @api.model
    def create(self, vals):
        if vals['partner_type']:
            sequence_code = ''
            if vals['partner_type'] == 'customer':
                if vals['payment_type'] == 'inbound':
                    sequence_code = 'account.payment.customer.invoice'
                if vals['payment_type'] == 'outbound':
                    sequence_code = 'account.payment.customer.refund'
            elif vals['partner_type'] == 'supplier':
                if vals['payment_type'] == 'inbound':
                    sequence_code = 'account.payment.supplier.refund'
                if vals['payment_type'] == 'outbound':
                    sequence_code = 'account.payment.supplier.invoice'
        else:
            sequence_code = 'account.payment.internal.move'
        vals['name'] = self.env['ir.sequence'].with_context(
            ir_sequence_date=vals['payment_date']).next_by_code(
            sequence_code)
        return super().create(vals)
