# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    equivalent_quantity = fields.Float(
        string="Equivalent Quantity On Hand",
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_quantity',
        store=True,
        help='Quantity in the secondary UoM computed dividing '
        'quantity / product factor',
    )
    equivalent_reserved_quantity = fields.Float(
        string="Equivalent Quantity Reserved",
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_reserved_quantity',
        store=True,
        help='Reserved quantity in the secondary UoM computed dividing '
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
    @api.depends('quantity')
    def _compute_equivalent_quantity(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_quantity = (
                    rec.quantity / rec.product_id.equivalent_factor)

    @api.multi
    @api.depends('reserved_quantity')
    def _compute_equivalent_reserved_quantity(self):
        for rec in self:
            if rec.product_id:
                rec.equivalent_reserved_quantity = (
                    rec.reserved_quantity / rec.product_id.equivalent_factor)
