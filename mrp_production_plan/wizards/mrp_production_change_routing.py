# Copyright 2020, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProductionChangeRouting(models.TransientModel):
    _name = 'mrp.production.change.routing'
    _description = 'Wizard to change routing of the current production'

    production_id = fields.Many2one('mrp.production')
    routing_id = fields.Many2one('mrp.routing', 'New Routing')
    current_routing_id = fields.Many2one(
        'mrp.routing', string='Current Routing')
    product_id = fields.Many2one('product.product')

    @api.model
    def default_get(self, fields_name):
        res = super().default_get(fields_name)
        production_id = self._context.get('active_id')
        production = self.env['mrp.production'].browse(production_id)
        res['current_routing_id'] = production.routing_id.id
        res['production_id'] = production.id
        res['product_id'] = production.product_id.id
        return res

    def _prepare_manufacturing_order(self):
        return {
            'name': self.production_id.name,
            'product_id': self.production_id.product_id.id,
            'product_qty': self.production_id.product_qty,
            'product_uom_id': self.production_id.product_uom_id.id,
            'bom_id': self.production_id.bom_id.id,
            'date_planned_start': self.production_id.date_planned_start,
            'user_id': self.production_id.user_id.id,
            'origin': self.production_id.origin,
            'picking_type_id': self.production_id.picking_type_id.id,
            'location_src_id': self.production_id.location_src_id.id,
            'location_dest_id': self.production_id.location_dest_id.id,
            'mrp_production_request_id':
                self.production_id.mrp_production_request_id.id,
            'plan_id': self.production_id.plan_id.id,
            'plan_line_id': self.production_id.plan_line_id.id,
            'use_alternative_bom': True,
            'move_dest_ids': [(6, 0, self.production_id.move_dest_ids.ids)],
        }

    def change_routing(self):
        self.ensure_one()
        if self.production_id.routing_id == self.routing_id:
            raise UserError(_('You are selecting the current Routing.'))
        message = _(
            'Change Routing:<br/>'
            '%s → %s') % (
            self.current_routing_id.display_name, self.routing_id.display_name)
        data = self._prepare_manufacturing_order()
        plan_line = self.production_id.plan_line_id
        bom = self.production_id.bom_id
        self.production_id.action_cancel()
        if self.production_id.picking_ids:
            self.production_id.picking_ids.sudo().unlink()
        self.env['change.production.qty'].search(
            [('mo_id', '=', self.production_id.id)]).sudo().unlink()
        self.production_id.sudo().unlink()
        bom.write({
            'routing_id': self.routing_id.id,
        })
        production = self.env['mrp.production'].create(data)
        plan_line.write({
            'production_id': production.id,
            'routing_id': self.routing_id.id,
        })
        production.message_post(body=message)
        production.button_plan()
        if production.plan_id:
            production.plan_id._link_workorders()
            production.plan_id._sort_workorders_by_sequence()
        return {
            'name': production.name,
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'res_id': production.id,
            'target': 'main',
            'view_mode': 'form',
        }
