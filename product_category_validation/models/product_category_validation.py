# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError
from odoo import _, api, fields, models


class ProductCategoryValidation(models.Model):
    _name = 'product.category.validation'
    _description = """Module that validates fields
    in relation to the chosen category"""

    field_id = fields.Many2one('ir.model.fields', domain=[
        ('model_id.model', '=', 'product.template'), ('readonly', '=', False)])
    value = fields.Char()
    categ_id = fields.Many2one(
        comodel_name='product.category',
    )
    error_msg = fields.Char('Error Message', translate=True)
    make_required = fields.Boolean()
    hide_field = fields.Boolean()

    _sql_constraints = [(
        'prod_categ_val',
        'unique (field_id,categ_id)',
        'Make sure field ids are not duplicated!')
    ]

    @api.onchange('field_id')
    def _set_default_value(self):
        if self.field_id.ttype == 'many2many' or self.field_id.ttype == 'char':
            self.hide_field = True

    @api.onchange('value')
    def _check_many_to_one(self):
        if self.field_id.ttype == 'many2one':
            try:
                int(self.value)
            except ValueError:
                raise UserError(_(
                    'Field_id is many2one must provide id in value!'))
