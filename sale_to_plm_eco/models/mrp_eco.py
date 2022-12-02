# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    order_id = fields.Many2one(
        'sale.order',
        string='Order Reference',
        copy=False,
        readonly=True)

    def show_sale_order(self):
        self.ensure_one()
        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', '=', self.order_id.id)],
            'type': 'ir.actions.act_window',
        }
