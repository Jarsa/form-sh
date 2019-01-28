# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class SaleOrderToECO(models.TransientModel):
    _name = 'sale.order.eco.wizard'
    _description = 'Create ECO from sale order'

    name = fields.Char(string='Description',)
    line_ids = fields.One2many(
        'sale.order.eco.wizard.line', 'wiz_id', string='Lines')

    @api.model
    def _prepare_eco_line(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'product_qty': line.qty,
        }

    @api.multi
    def create_eco(self):
        self.ensure_one()
        ids = []
        for line in self.line_ids:
            eco = self.env['mrp.eco'].create({
                'name': line.name,
                'type_id': line.type_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'order_id': self._context.get('active_id'),
                'bom_id': line.bom_id.id,
            })
        ids.append(eco.id)
        return {
            'name': _('PLM'),
            'view_mode': 'tree,form',
            'res_model': 'mrp.eco',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)],
        }

    @api.model
    def _prepare_item(self, line):
        return {
            'product_id': line.product_id.id,
            'product_uom_qty': line.product_uom_qty,
            'uom_id': line.product_uom.id,
            'bom_ids': [(6, 0, line.product_id.product_tmpl_id.bom_ids.ids)],
        }

    @api.model
    def default_get(self, field):
        res = super().default_get(field)
        so = self.env['sale.order'].browse(
            self._context.get('active_ids')).order_line
        lines = []
        for line in so:
            lines.append([0, 0, self._prepare_item(line)])
        res.update({
            'line_ids': lines,
        })
        return res


class SaleOrdeECOLine(models.TransientModel):
    _name = 'sale.order.eco.wizard.line'
    _description = 'Wizard line'

    wiz_id = fields.Many2one('sale.order.eco.wizard')
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        readonly=True,)
    name = fields.Char(required=True, string='ECO Description')
    product_id = fields.Many2one('product.product', required=True)
    product_uom_qty = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', required=True)
    type_id = fields.Many2one('mrp.eco.type', required=True)
    bom_id = fields.Many2one(
        'mrp.bom',
        string='Bill of Materials',
    )
    bom_ids = fields.Many2many(
        'mrp.bom',
        string='Bill of Materials',
    )
