# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import models

try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_picking(self):
        warehouse = ''
        if self.invoice_origin:
            order = self.env['sale.order'].search([
                ('name', '=', self.invoice_origin),
            ])
            warehouse = order.warehouse_id.name
        return warehouse

    def get_rate(self):
        for rec in self:
            val_tc = 0.0
            val_tc += rec.currency_id.with_context(
                date=rec.invoice_date).rate
        return 1 / val_tc

    def _amount_to_text(self):
        self.ensure_one()
        currency_name = self.currency_id.name.upper()
        currency_type = 'M.N' if currency_name == 'MXN' else 'USD'
        currency = 'PESOS' if currency_name == 'MXN' else 'DOLARES'
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = (
            num2words(
                float(amount_i), lang=self.partner_id.lang or 'es_ES').upper())
        invoice_words = (
            '%(words)s %(currency)s  %(amount_d)02d/100 %(curr_t)s' %
            dict(
                words=words, currency=currency,
                amount_d=amount_d, curr_t=currency_type))
        return invoice_words
