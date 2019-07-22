# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_picking(self):
        if self.origin:
            so = self.env['sale.order'].search(
                [('name', '=', self.origin)])
            return so.warehouse_id.name

    @api.multi
    def get_rate(self):
        for rec in self:
            val_tc = 0.0
            val_tc += rec.currency_id.with_context(
                date=rec.date_invoice).rate
        return 1/val_tc

    @api.multi
    def get_tax(self):
        for rec in self:
            dict_taxes = {}
            taxes_names = {}
            for line in rec.invoice_line_ids:
                for tax in line.invoice_line_tax_ids:
                    value = line.price_subtotal * (tax.amount / 100)
                    if tax.description not in taxes_names.keys():
                        taxes_names[tax.description] = [value]
                    else:
                        taxes_names[tax.description].append(value)
            for k, v in taxes_names.items():
                dict_taxes[k] = sum(v)
        return dict_taxes

    @api.multi
    def _amount_to_text(self):
        self.ensure_one()
        currency_name = self.currency_id.name.upper()
        currency_type = 'M.N' if currency_name == 'MXN' else 'M.E.'
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
