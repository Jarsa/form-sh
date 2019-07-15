# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')

    type_operation = fields.Selection(
        related='picking_id.picking_type_id.code',
        store=True)
    subtotal = fields.Float(compute='_compute_subtotal', store=True)

    @api.multi
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity_done * rec.price_unit


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    type_operation_line = fields.Selection(
        related='move_id.type_operation',
        store=True)
    price_unit = fields.Float(related='move_id.price_unit')
    subtotal = fields.Float(compute='_compute_subtotal')

    @api.multi
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty_done * rec.price_unit
