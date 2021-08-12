# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _prepare_manufacturing_order(self):
        self.ensure_one()
        res = super()._prepare_manufacturing_order()
        res['plan_line_id'] = self.mrp_production_request_id.plan_line_id.id
        res['plan_id'] = self.mrp_production_request_id.plan_line_id.plan_id.id
        return res
