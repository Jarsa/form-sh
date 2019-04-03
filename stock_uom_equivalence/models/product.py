# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_default_equivalent_uom(self):
        return self.uom_id or self.env.ref('uom.product_uom_unit')

    equivalent_factor = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0,
        help='Factor to compute the product quantities in the secondary UoM.'
        ' To compute that quantity the quantity in the original UoM will be'
        ' multiplied by the value of this field.',
    )
    equivalent_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Equivalent Unit of Measure',
        default=_get_default_equivalent_uom,
        help='Secondary Unit of Measure used to show the inventory'
        ' on stock reports.'
    )

    @api.constrains('equivalent_factor')
    def _validate_equivalent_factor(self):
        for rec in self:
            if rec.equivalent_factor <= 0:
                raise UserError(
                    _('Error. The factor to compute the secondary quantities'
                        ' must be greather than zero.'))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    equivalent_qty_at_date = fields.Float(
        string='Equivalent Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_equivalent_qty_at_date',
    )

    @api.multi
    @api.depends('qty_at_date')
    def _compute_equivalent_qty_at_date(self):
        for rec in self:
            rec.equivalent_qty_at_date = (
                rec.qty_at_date / rec.equivalent_factor)
