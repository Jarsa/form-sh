# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import models


class MrpProductionBackorder(models.TransientModel):
    _inherit = 'mrp.production.backorder'

    def action_backorder(self):
        res = super().action_backorder()
        new_prod = self.env['mrp.production'].browse(res['res_id'])
        old_prod = self.mrp_production_backorder_line_ids.mrp_production_id
        new_prod.write({
            'plan_id': old_prod.plan_id.id,
            'plan_line_id': old_prod.plan_line_id.id,
            'mrp_request_id': old_prod.mrp_request_id.id,
        })
        return res
