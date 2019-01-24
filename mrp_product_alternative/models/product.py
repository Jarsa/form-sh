# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    alternative_ids = fields.One2many(
        comodel_name='product.alternative',
        inverse_name='product_id',
        string='Alternative Products',
        copy=False,
        help='Alternative Products compatible with this product.',
    )

    @api.constrains('alternative_ids')
    @api.multi
    def _check_product_integrity(self):
        for rec in self:
            if rec in rec.alternative_ids.mapped('alternative_id'):
                raise UserError(
                    _('Error! You cannot set the same product'
                        ' as alternative.'))


class ProductAlternative(models.Model):
    _name = 'product.alternative'
    _order = 'sequence'
    _description = 'Alternative Products'

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        ondelete='cascade',
        required=True,
    )
    alternative_id = fields.Many2one(
        comodel_name='product.template',
        string='Alternative Product',
        required=True,
    )
    sequence = fields.Integer(
        default=10,
    )
