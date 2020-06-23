# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).

from odoo import api, models


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _prepare_move_lines(
        self, move_lines, target_currency=False, target_date=False, recs_count=0
    ):
        res = super()._prepare_move_lines(
            move_lines, target_currency, target_date, recs_count
        )
        new_res = []
        if res:
            account_tag_id = self.env.ref("form_instance.account_tag_no_concil_form").id
            account_ids = self.env['account.account'].search([('tag_ids', 'in', [account_tag_id])]).ids
            for rec in res:
                if rec["account_id"][0] not in account_ids:
                    new_res.append(rec)
        return new_res
