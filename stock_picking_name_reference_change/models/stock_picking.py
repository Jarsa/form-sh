# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    origin_mo = fields.Char(string='Origin MO', readonly=True)
    production_id = fields.Many2one(
        'mrp.production',
    )

    @api.multi
    def action_view_production_id(self):
        self.ensure_one()
        action = {
            'name': _('Mrp Orders'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.production_id.id)],
        }
        return action
