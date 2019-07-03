# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def get_tax(self):
        for rec in self:
            dict_taxes = {}
            taxes_names = {}
            for line in rec.order_line:
                for tax in line.tax_id:
                    value = line.price_subtotal * (tax.amount / 100)
                    if tax.description not in taxes_names.keys():
                        taxes_names[tax.description] = [value]
                    else:
                        taxes_names[tax.description].append(value)
            for k, v in taxes_names.items():
                dict_taxes[k] = sum(v)
        return dict_taxes
