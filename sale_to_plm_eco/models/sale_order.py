# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    eco_ids = fields.One2many(
        'mrp.eco', 'order_id', string='Engineering Change Order')

    def show_mrp_eco(self):
        return {
            'name': _('MRP ECO'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.eco',
            'domain': [('order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }
