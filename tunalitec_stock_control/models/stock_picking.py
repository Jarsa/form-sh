from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_internal_picking_required_qty(self):
        required = defaultdict(float)
        for move in self.move_ids:
            qty_done = move.quantity
            qty = qty_done if qty_done > 0 else move.product_uom_qty
            if qty <= 0:
                continue
            qty = move.product_uom._compute_quantity(qty, move.product_id.uom_id)
            key = (
                move.product_id.id,
                move.location_id.id,
                False,
                False,
                False,
            )
            required[key] += qty
        return required

    def _check_internal_availability(self):
        self.ensure_one()
        if self.picking_type_id.code != "internal":
            return

        required = self._get_internal_picking_required_qty()
        if not required:
            return

        errors = []
        for key, qty_needed in required.items():
            product_id, location_id, lot_id, package_id, owner_id = key
            product = self.env["product.product"].browse(product_id)
            location = self.env["stock.location"].browse(location_id)
            ctx = dict(self.env.context)
            ctx.update(
                {
                    "location": location.id,
                    "lot_id": lot_id or None,
                    "package_id": package_id or None,
                    "owner_id": owner_id or None,
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
                    "No hay disponibilidad suficiente para validar este traslado interno:\n%(details)s",
                    details="\n".join(errors),
                )
            )

    def button_validate(self):
        for picking in self:
            picking._check_internal_availability()
        return super().button_validate()
