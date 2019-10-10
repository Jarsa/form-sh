# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError
from odoo import api, models


class ProductCategory(models.Model):
    _inherit = 'product.template'

    @api.onchange('categ_id')
    def _set_user_defaults(self):
        for rec in self.categ_id.validation_ids:
            name = rec.field_id.name
            if rec.field_id.ttype == 'many2one':
                self.update({
                    name: int(rec.value)
                })
            else:
                self.update({
                    name: rec.value
                })

    def _verify_defaults_set(self):
        for rec in self.categ_id.validation_ids:
            if rec.field_id.ttype == 'many2one':
                value = int(rec.value)
            else:
                value = rec.value
            se = getattr(self, rec.field_id.name)
            search_field = ('self.%s' % rec.field_id.name)
            if (se != value) and value:
                raise UserError(rec.error_msg)
            if rec.make_required and not search_field:
                raise UserError(
                    rec.field_id.name + ' must have a value assigned ')

    @api.multi
    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        self._verify_defaults_set()
        return res
