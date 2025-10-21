# Copyright 2021 Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_mx_edi_get_advance_aml_domain(self):
        res = super()._l10n_mx_edi_get_advance_aml_domain()
        if self._context.get('active_model', False) != 'sale.order':
            res.extend([
                '|',
                ('sale_line_ids', '=', False),
                ('sale_line_ids.order_id', 'in',
                    self.invoice_line_ids.sale_line_ids.order_id.ids)
            ])
        return res
