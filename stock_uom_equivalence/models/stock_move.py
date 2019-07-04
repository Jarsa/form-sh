# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    equivalent_product_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_product_qty',
        store=True,
        help='Quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_product_uom_qty = fields.Float(
        string='Equivalent Initial Demand',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_product_uom_qty',
        store=True,
        help='Quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_reserved_availability = fields.Float(
        string='Equivalent Reserved',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_reserved_availability',
        store=True,
        help='Reserved quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_quantity_done = fields.Float(
        string='Equivalent Done',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_quantity_done',
        store=True,
        help='Done quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Equivalent Unit of Measure',
        related='product_id.equivalent_uom_id',
        store=True,
        help='Secondary Unit of Measure used to show the inventory'
        ' on stock reports.'
    )

    @api.multi
    @api.depends('product_qty')
    def _compute_equivalent_product_qty(self):
        for rec in self:
            if rec.product_id:
                rec.product_qty = (
                    rec.product_qty / rec.product_id.equivalent_factor)

    @api.multi
    @api.depends('product_uom_qty')
    def _compute_equivalent_product_uom_qty(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_product_uom_qty = (
                    rec.product_uom_qty / rec.product_id.equivalent_factor)

    @api.multi
    @api.depends('reserved_availability')
    def _compute_equivalent_reserved_availability(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_reserved_availability = (
                    rec.reserved_availability / rec.product_id.equivalent_factor)

    @api.multi
    @api.depends('quantity_done')
    def _compute_equivalent_quantity_done(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_quantity_done = (
                    rec.quantity_done / rec.product_id.equivalent_factor)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    equivalent_product_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_product_qty',
        store=True,
        help='Quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_product_uom_qty = fields.Float(
        string='Equivalent Reserved',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_product_uom_qty',
        store=True,
        help='Quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_qty_done = fields.Float(
        string='Equivalent Done',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_qty_done',
        store=True,
        help='Done quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Equivalent Unit of Measure',
        related='product_id.equivalent_uom_id',
        store=True,
        help='Secondary Unit of Measure used to show the inventory'
        ' on stock reports.'
    )

    @api.multi
    @api.depends('product_qty')
    def _compute_equivalent_product_qty(self):
        for rec in self:
            if rec.product_id:
                rec.product_qty = (
                    rec.product_qty / rec.product_id.equivalent_factor)

    @api.multi
    @api.depends('product_uom_qty')
    def _compute_equivalent_product_uom_qty(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_product_uom_qty = (
                    rec.product_uom_qty / rec.product_id.equivalent_factor)

    @api.multi
    @api.depends('qty_done')
    def _compute_equivalent_qty_done(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_qty_done = (
                    rec.qty_done / rec.product_id.equivalent_factor)
