# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import models
from odoo.exceptions import UserError
from odoo.addons.sale.models.account_move import AccountMove as MOVE


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Use odoo native method with mapped in sale_line_ids
        res = super(MOVE, self).action_post()

        sale_line_ids = self.mapped('line_ids.sale_line_ids').filtered(
            lambda line: line.is_downpayment)
        line_ids = self.mapped('line_ids').filtered(
            lambda line: line.sale_line_ids in sale_line_ids)
        for line in line_ids:
            try:
                line.mapped('sale_line_ids').tax_id = line.tax_ids
                if all(line.tax_ids.mapped('price_include')):
                    line.sale_line_ids.write({
                        'price_unit': line.price_unit,
                    })
                else:
                    line.sale_line_ids.write({
                        'price_unit': -line.sale_line_ids.untaxed_amount_to_invoice,
                    }) 
            except UserError:
                pass
        return res
