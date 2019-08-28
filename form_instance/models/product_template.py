# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        if self.user_has_groups(
                'form_instance.group_edit_product_mrp_user'):
            allowed_fields = ['cost_price', 'tracking']
            for key in vals.keys():
                if key not in allowed_fields:
                    raise ValidationError(
                        _('You are not allowed to modify products.'))
        return super().write(vals)

    @api.onchange('item_ids')
    def _onchange_items_ids(self):
        if self.item_ids:
            price = self.item_ids[0]
            self.write({'lst_price': price.fixed_price})


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(
            self, name, args=None, operator='=ilike',
            limit=100, name_get_uid=None):
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = (['|', '|', ('default_code', 'ilike', name),
                       ('description', 'ilike', name),
                       ('name', 'ilike', name)])
            product_ids = self._search(
                expression.AND([domain, args]),
                limit=limit, access_rights_uid=name_get_uid)
            return self.browse(product_ids).name_get()
        return super(ProductProduct, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)
