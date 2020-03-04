# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    update_reason = fields.Many2one('mrp.production.update.reason')

    def change_prod_qty(self):
        res = super(ChangeProductionQty, self).change_prod_qty()
        for wizard in self:
            quality = self.env['quality.alert']
            msg = "Product %s Qty Updated - Reason: %s" % (
                wizard.mo_id.product_id.display_name, wizard.update_reason.name
            )
            quality.create({
                'title': msg,
                'product_tmpl_id': wizard.mo_id.product_id.product_tmpl_id.id,
                'update_reason': wizard.update_reason.id,
                'production_id': wizard.mo_id.id,
                })
        return res
