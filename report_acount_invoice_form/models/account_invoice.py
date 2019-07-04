# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, models


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
        return val_tc

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
        import ipdb; ipdb.set_trace()
        return dict_taxes

