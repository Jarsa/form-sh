# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        for rec in self:
            models_to_val = ['product.product', 'product.template']
            has_group = self.user_has_groups(
                'form_instance.group_allow_delete_prod_attachment')
            if rec.res_model in models_to_val and not has_group:
                raise UserError(
                    _('You are not allowed to delete product attachments'))
        return super().unlink()
