# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_surplus = fields.Boolean()

    @api.onchange('is_surplus')
    def _onchange_is_surplus(self):
        if self.is_surplus:
            self.picking_type_id = self.env.ref(
                'mrp_production_surplus.mrp_production_surplus_type_operation')
        return {
            'domain': {
                'product_id': [
                    ('bom_ids', '!=', False),
                    ('bom_ids.active', '=', True),
                    ('bom_ids.type', '=', 'normal'),
                    ('bom_ids.is_surplus', '=', self.is_surplus),
                ],
            }
        }
