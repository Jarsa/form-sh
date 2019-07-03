# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models


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
    def change_bom(self):
        self.ensure_one()
        self.production_id.bom_id = self.bom_id.id
        move_orig_ids = self.production_id.move_raw_ids.mapped('move_orig_ids')
        if move_orig_ids:
            move_orig_ids._action_cancel()
            move_orig_ids.unlink()
        self.production_id.move_raw_ids._action_cancel()
        self.production_id.move_raw_ids.unlink()
        self.production_id._generate_moves()


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
