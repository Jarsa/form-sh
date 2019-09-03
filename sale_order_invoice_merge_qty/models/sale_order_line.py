# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity',
                 'invoice_lines.sibling_invoice_id.state')
    def _get_invoice_qty(self):
        return super()._get_invoice_qty()
