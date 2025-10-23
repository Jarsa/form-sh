from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def _l10n_mx_get_invoiced_lot_values(self):
        """Returns the lots from the invoice where the product is the same that the invoice line"""
        self.ensure_one()
        smls = self.sale_line_ids.move_ids.move_line_ids
        if not smls.lot_id:
            return []
        lots_line = []
        for sml in smls:
            if not sml.lot_id:
                continue
            lots_line.append(
                {
                    "product_name": sml.product_id.display_name,
                    "quantity": sml.qty_done,
                    "uom_name": sml.product_uom_id.name,
                    "lot_name": sml.lot_id.name,
                    "lot_id": sml.lot_id.id,
                }
            )
        return lots_line
