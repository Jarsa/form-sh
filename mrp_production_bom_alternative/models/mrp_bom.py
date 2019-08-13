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
        ('sequence_uniq', 'unique(sequence, product_tmpl_id)',
            _('The sequence must be unique !')),
    ]

    @api.constrains('sequence')
    @api.multi
    def _constraint_sequence(self):
        for rec in self:
            if rec.sequence <= 0:
                raise UserError(_('The sequence cannot be less than 1'))
