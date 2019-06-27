# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MrpProductionRequest(models.Model):
    _inherit = 'mrp.production.request'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.categ_id.location_src_id:
            self.location_src_id = self.product_id.categ_id.location_src_id
        if self.product_id and self.product_id.categ_id.location_dest_id:
            self.location_dest_id = self.product_id.categ_id.location_dest_id
        return super()._onchange_product_id()
