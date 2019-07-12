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
    def _prepare_manufacturing_order(self, prod):
        return {
            'name': prod.name,
            'product_id': prod.product_id.id,
            'prouct_qty': prod.product_qty,
            'product_uom_id': prod.product_uom_id.id,
            'origin': prod.origin,
            'picking_type_id': prod.picking_type_id.id,
            'location_src_id': prod.location_src_id.id,
            'location_dest_id': prod.location_dest_id.id,
            'bom_id': self.bom_id.id,
            'mrp_production_request_id': prod.mrp_production_request_id.id,
            'plan_line_id': (
                prod.plan_line_id.id if prod.plan_line_id else False),
            'plan_id': prod.plan_id.id if prod.plan_id else False
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
        self.production_id.message_post(body=message)
        self.production_id.bom_id = self.bom_id.id
        # Get stock picking type of to pre-production
        pbm_id = self.production_id.picking_type_id.warehouse_id.pbm_type_id.id
        # Filter only pickings of type pre-production
        pickings = self.production_id.picking_ids.with_context(
            pbm_id=pbm_id).filtered(
                lambda p: p.picking_type_id.id == p._context.get('pbm_id'))
        if pickings:
            pickings.mapped('move_lines').write({'propagate': False})
            pickings.unlink()
        self.production_id.move_raw_ids.write({'propagate': False})
        self.production_id.move_raw_ids._action_cancel()
        self.production_id.move_raw_ids.unlink()
        self.production_id.move_finished_ids.write({'propagate': False})
        self.production_id.move_finished_ids._action_cancel()
        self.production_id.move_finished_ids.unlink()
        self.production_id._generate_moves()
        self.production_id._process_picking_origin()
        if self.production_id.workorder_ids:
            self.production_id.workorder_ids.time_ids.unlink()
            self.production_id.workorder_ids.unlink()
        self.production_id.state = 'confirmed'
        if self.procution_id.routing_id:
            self.production_id.button_plan()
            if self.production_id.plan_id:
                self.production_id.plan_id._sort_workorders_by_sequence()


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
