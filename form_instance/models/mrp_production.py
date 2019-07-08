# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
    is_already_reserved = fields.Boolean()

    @api.onchange('move_raw_ids.reserved_availability')
    def _onchange_move_raw_ids(self):
        # This detect if already is reserved the materials
        self._check_is_already_reserved()

    @api.multi
    def action_assign(self):
        res = super().action_assign()
        self._check_is_already_reserved()
        return res

    @api.multi
    def _check_is_already_reserved(self):
        for rec in self:
            is_reserved = rec._get_reserved_quantity_products()
            rec.write({
                'is_already_reserved': is_reserved,
            })

    @api.multi
    def _get_reserved_quantity_products(self):
        for rec in self:
            if rec.move_raw_ids.filtered(
                lambda l: l.product_uom_qty == l.reserved_availability
            ) == self.move_raw_ids:
                return True
            return False
