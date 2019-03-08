# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

import logging
from odoo import models

_logger = logging.getLogger(__name__)
try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _amount_to_text(
            self, amount, currency, partner_lang='es_MX'):
        total = str(float(amount)).split('.')[0]
        decimals = str(float(amount)).split('.')[1]
        currency_type = 'M.N.'
        if partner_lang != 'es_MX':
            total = num2words(float(amount)).upper()
        else:
            total = num2words(float(total), lang='es').upper()
        if currency != 'MXN':
            currency_type = 'M.E.'
        else:
            currency = 'PESOS'
        return '%s %s %s/100 %s' % (
            total, currency, decimals or 0.0, currency_type)
