# Copyright 2019, Jarsa Sistemas S.A de C.V
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re

from odoo import _, api, models
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def create(self, values):
        product = self.env['product.product'].browse(values['product_id'])
        raw_material = product.purchase_ok
        pattern = (
            '^[AN][A-Z]{3}([0-2][0-9]|(3)[0-1])(((0)[0-9])'
            '|((1)[0-2]))\\d{5}$')
        if not raw_material:
            pattern = (
                '^[A-Z]{3}\\d([0-2][0-9]|(3)[0-1])(((0)[0-9])|((1)[0-2]))'
                '\\d{2}[CR]([C][A]|[C][H]|[C][E]|[E][S]|[R][E]|[T][A])\\d{3}$')
        regex = re.compile(pattern)
        if not regex.match(values['name']):
            definition = _(
                '1 Letter A for American or N for National.\n'
                '3 Letters for supplier code.\n'
                '6 Digits for the date in format ddmmyy.\n'
                '3 Digits for consecutive number.\n\n'
                'Example: ABCD311219001')
            if not raw_material:
                definition = _(
                    '3 Letters for customer code.\n'
                    '1 Digit for customer plant number.\n'
                    '6 Digits for the date in format ddmmyy.\n'
                    '1 Letter C for carton R for retornable.\n'
                    '2 Letters CA for Caja CH for Charola CE for Celdas '
                    'ES for Esquinero RE for Rejilla TA for Tapas.\n'
                    '3 Digits for consecutive number.\n\n'
                    'Example: STB1021119CCA001')
            raise UserError(_(
                'The name of the lot does not meet the defined standard\n\n%s'
                % definition))
        return super().create(values)
