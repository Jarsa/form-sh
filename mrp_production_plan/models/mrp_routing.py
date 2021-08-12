# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'
    _order = 'sequence asc'

    product_id = fields.Many2one(
        'product.product', domain=[('bom_ids', '!=', False)])
    sequence = fields.Integer(
        help='Gives the sequence order when displaying a list of routings.',
        default=1)

    _sql_constraints = [
        ('sequence_uniq', 'unique(product_id, sequence)',
            _('The sequence must be unique !')),
    ]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            count = self.search_count(
                [('product_id', '=', self.product_id.id)])
            self.sequence = count + 1

    def copy(self, default=None):
        if not default:
            default = {}
        sequences = self.env['mrp.routing'].with_context(
            active_test=False).search([
                ('product_id', '=', self.product_id.id)],
                order='sequence asc').mapped('sequence')
        sequence = sequences[-1] + 1 if sequences else 1
        default['sequence'] = sequence
        return super().copy(default)

    @api.constrains('sequence')
    def _constraint_sequence(self):
        for rec in self:
            if rec.sequence <= 0:
                raise UserError(_('The sequence cannot be less than 1'))
