# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    sequence = fields.Integer(
        help='Gives the sequence order when displaying a list of bills of '
        'material.', default=1, )

    _sql_constraints = [
        ('sequence_uniq', 'unique(product_tmpl_id, sequence)',
            _('The sequence must be unique !')),
    ]

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        sequences = self.env['mrp.bom'].with_context(
            active_test=False).search([
                ('product_tmpl_id', '=', self.product_tmpl_id.id)],
                order='sequence asc').mapped('sequence')
        sequence = sequences[-1] + 1 if sequences else 1
        default['sequence'] = sequence
        return super().copy(default)

    @api.constrains('sequence')
    @api.multi
    def _constraint_sequence(self):
        for rec in self:
            if rec.sequence <= 0:
                raise UserError(_('The sequence cannot be less than 1'))
