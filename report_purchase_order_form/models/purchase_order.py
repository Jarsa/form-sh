# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)
try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
