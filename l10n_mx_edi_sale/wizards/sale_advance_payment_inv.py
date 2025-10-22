# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super()._prepare_invoice_values(order, name, amount, so_line)
        res.update({
            'l10n_mx_edi_payment_method_id': (
                order.l10n_mx_edi_payment_method_id.id),
            'l10n_mx_edi_usage': order.l10n_mx_edi_usage,
        })
        return res
