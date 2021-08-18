# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import models


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
