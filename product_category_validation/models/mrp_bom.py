# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id.categ_id.is_kit:
            self.type = 'phantom'
        else:
            self.type = 'normal'

    @api.multi
    @api.constrains('type')
    def _check_product_category_kit(self):
        for rec in self:
            if rec.product_tmpl_id.categ_id.is_kit and rec.type == 'normal':
                raise ValidationError(
                    _('The main product of this BoM is a Kit.'))
            if (not rec.product_tmpl_id.categ_id.is_kit and
                    rec.type == 'phantom'):
                raise ValidationError(
                    _('The main product of this Bom is not a Kit'))
