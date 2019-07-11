# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models


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
        self.production_id.bom_id = self.bom_id.id
        old_mo = self._prepare_manufacturing_order(self.production_id)
        pickings = self.production_id.move_raw_ids.mapped(
            'move_orig_ids.picking_id').filtered(
                lambda p: p.state not in ['done', 'cancel'])
        if pickings:
            pickings.action_cancel()
            pickings.unlink()
        self.production_id.action_cancel()
        self.production_id.unlink()
        mo_obj = self.env['mrp.production']
        mo = mo_obj.create(old_mo)
        if mo.plan_id:
            mo.button_plan()
            mo.plan_id._sort_workorders_by_sequence()
        else:
            mo.button_plan()
        return {
            'name': _('Manufacturing Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': mo.id,
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
