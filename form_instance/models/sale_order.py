from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_cancel(self):
        # Override the original action_cancel for a Sale_Order
        #
        # This function validates the status of the order's related pickings
        # and returns an error if the state is not "done" or "canceled"
        #
        # Additionally,the function calls a custom method in
        # SaleOrderLine defined below
        # to validate that the quantity delivered per line is = to 0.0. If not,
        # the order cannot be cancelled.

        for rec in self.picking_ids:
            if rec.state not in ['done', 'cancelled']:
                raise ValidationError(
                    _('At least one picking is not in status'
                        ' Done or Cancelled, cannot cancel Sale Order.'))
        self.mapped('order_line')._validate_zero_qty_delivered()

        return super().action_cancel()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _validate_zero_qty_delivered(self):
        for line in self:
            if line.qty_delivered != 0.0:
                raise ValidationError(
                    _('At least one "Quantity Delivered" from the Sale Order'
                        ' was not equal to 0, cannot cancel Sale Order'))
