from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockTransfer(models.Model):
    _inherit = "stock.transfer"

    def _check_transfer_availability(self):
        self.ensure_one()
        if not self.line_ids or not self.location_id:
            return

        required = defaultdict(float)
        for line in self.line_ids:
            if line.qty <= 0:
                continue
            qty = line.product_uom_id._compute_quantity(
                line.qty, line.product_id.uom_id
            )
            required[line.product_id.id] += qty

        if not required:
            return

        errors = []
        for product_id, qty_needed in required.items():
            product = self.env["product.product"].browse(product_id)
            ctx = dict(self.env.context)
            ctx.update(
                {
                    "location": self.location_id.id,
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
                        location=self.location_id.display_name,
                        available=available,
                        required=qty_needed,
                    )
                )

        if errors:
            raise UserError(
                _(
                    "No hay disponibilidad suficiente para procesar esta transferencia:\n%(details)s",
                    details="\n".join(errors),
                )
            )

    def action_process(self):
        for transfer in self:
            transfer._check_transfer_availability()
        return super().action_process()
