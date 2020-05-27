# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProductionBomAlternativeWizard(models.TransientModel):
    _name = 'mrp.production.bom.alternative.wizard'
    _description = 'Change Bill of Materials in Manufacturing Order'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        readonly=True,
    )
    bom_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Bill of Materials',
        required=True,
    )
    current_bom_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Current Bill of Materials',
        readonly=True,
    )
    production_id = fields.Many2one(
        comodel_name='mrp.production',
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name='mrp.production.bom.alternative.wizard.line',
        inverse_name='wiz_id',
        string='Lines',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_name):
        res = super().default_get(fields_name)
        production_id = self._context.get('active_id')
        production = self.env['mrp.production'].browse(production_id)
        res['product_tmpl_id'] = production.product_tmpl_id.id
        res['production_id'] = production.id
        res['current_bom_id'] = production.bom_id.id
        return res

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        self.line_ids = False
        if self.bom_id:
            lines = []
            for line in self.bom_id.bom_line_ids:
                lines.append((0, 0, {
                    'wiz_id': self.id,
                    'product_id': line.product_id.id,
                    'uom_id': line.product_uom_id.id,
                    'product_qty': line.product_qty,
                }))
            self.line_ids = lines

    @api.multi
    def _prepare_manufacturing_order(self):
        return {
            'name': self.production_id.name,
            'product_id': self.production_id.product_id.id,
            'product_qty': self.production_id.product_qty,
            'product_uom_id': self.production_id.product_uom_id.id,
            'bom_id': self.bom_id.id,
            'routing_id': self.production_id.routing_id.id,
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
            'move_dest_ids': [(6, 0, self.production_id.move_dest_ids.ids)]
        }

    @api.multi
    def change_bom(self):
        self.ensure_one()
        if self.production_id.bom_id == self.bom_id:
            raise UserError(_('You are selecting the current BoM.'))
        message = _(
            'Change to Alternative BoM:<br/>'
            '%s → %s') % (
            self.production_id.bom_id.display_name, self.bom_id.display_name)
        data = self._prepare_manufacturing_order()
        plan_line = self.production_id.plan_line_id
        self.production_id.action_cancel()
        if self.production_id.picking_ids:
            self.production_id.picking_ids.sudo().unlink()
        self.env['change.production.qty'].search(
            [('mo_id', '=', self.production_id.id)]).sudo().unlink()
        self.production_id.sudo().unlink()
        self.bom_id.write({'routing_id': self.current_bom_id.routing_id.id})
        production = self.env['mrp.production'].with_context(
            alternative_bom=True).create(data)
        production.routing_id = data['routing_id']
        plan_line.write({
            'production_id': production.id,
            'bom_id': production.bom_id.id,
        })
        production.message_post(body=message)
        if production.routing_id:
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


class ProductAlternativeWizardLine(models.TransientModel):
    _name = 'mrp.production.bom.alternative.wizard.line'
    _description = ('Lines to Change MO Without Stock For'
                    ' Alternative BoM')

    wiz_id = fields.Many2one(
        comodel_name='mrp.production.bom.alternative.wizard',
        string='Wizard',
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        readonly=True,
    )
    product_qty = fields.Float(
        string='Qty',
        readonly=True,
    )
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        readonly=True,
    )
