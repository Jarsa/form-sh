from odoo import _, models
from odoo.exceptions import ValidationError

from datetime import date


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
            if rec.state not in ['done', 'cancel']:
                raise ValidationError(
                    _('At least one picking is not in status'
                        ' Done or Cancelled, cannot cancel Sale Order.'))
        self.mapped('order_line')._validate_zero_qty_delivered()

        return super().action_cancel()

    def change_so_state(self):
        for rec in self:
            for line in rec.order_line:
                line.qty_invoiced = line.qty_delivered
                categ = line.product_id.categ_id
                goods_account = categ.property_stock_account_output_categ_id.id
                sale_cost_account = categ.property_account_expense_categ_id.id
                aml = line.move_ids.filtered(
                    lambda m: m.state == 'done').mapped(
                    'account_move_ids.line_ids').filtered(
                    lambda aml: aml.account_id.id == goods_account)
                aml.mapped('move_id').button_cancel()
                aml.mapped('move_id').write({'date': date.today()})
                aml.write({
                    'account_id': sale_cost_account,
                    'date': date.today()})
                aml.mapped('move_id').action_post()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _validate_zero_qty_delivered(self):
        for line in self:
            if line.qty_delivered != 0.0:
                raise ValidationError(
                    _('At least one "Quantity Delivered" from the Sale Order'
                        ' was not equal to 0, cannot cancel Sale Order'))
