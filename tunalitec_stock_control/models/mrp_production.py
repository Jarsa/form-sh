from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _is_linked_to_sale_order(self):
        self.ensure_one()
        if "sale_line_id" in self._fields and self.sale_line_id:
            return True
        if "sale_id" in self._fields and self.sale_id:
            return True
        if "procurement_group_id" in self._fields and self.procurement_group_id:
            group = self.procurement_group_id
            if "sale_id" in group._fields and group.sale_id:
                return True
        return False

    def _check_raw_material_availability(self):
        self.ensure_one()
        if not self._is_linked_to_sale_order():
            return

        required = defaultdict(float)
        for move in self.move_raw_ids:
            if move.product_uom_qty <= 0:
                continue
            qty = move.product_uom._compute_quantity(
                move.product_uom_qty, move.product_id.uom_id
            )
            key = (
                move.product_id.id,
                move.location_id.id,
            )
            required[key] += qty

        if not required:
            return

        errors = []
        for key, qty_needed in required.items():
            product_id, location_id = key
            product = self.env["product.product"].browse(product_id)
            location = self.env["stock.location"].browse(location_id)
            ctx = dict(self.env.context)
            ctx.update(
                {
                    "location": location.id,
                    "compute_child": False,
                }
            )
            available = product.with_context(ctx).qty_available
            if float_compare(
                available, qty_needed, precision_rounding=product.uom_id.rounding
            ) < 0:
                errors.append(
                    _(
                        "- Producto: %(product)s | Ubicacion: %(location)s | Disponible: %(available).2f | Requerido: %(required).2f",
                        product=product.display_name,
                        location=location.display_name,
                        available=available,
                        required=qty_needed,
                    )
                )

        if errors:
            raise UserError(
                _(
                    "No hay disponibilidad suficiente para confirmar la orden de produccion:\n%(details)s",
                    details="\n".join(errors),
                )
            )

    def action_confirm(self):
        for production in self:
            production._check_raw_material_availability()
        return super().action_confirm()
