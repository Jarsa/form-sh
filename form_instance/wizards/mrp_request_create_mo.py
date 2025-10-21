# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.request.create.mo"

    def _prepare_manufacturing_order(self):
        res = super()._prepare_manufacturing_order()
        res.pop("procurement_group_id")
        return res
