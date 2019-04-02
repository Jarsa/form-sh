# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _merge_line_qty(self, invoice):
        for line in invoice.invoice_line_ids:
            if line.invoice_id:
                sibling_lines = line.search([
                    ('product_id', '=', line.product_id.id),
                    ('invoice_id', '=', invoice.id),
                    ('id', '!=', line.id)])
                if sibling_lines:
                    total_qty = sum(sibling_lines.mapped('quantity'))
                    line.quantity = line.quantity + total_qty
                    sibling_lines.write({
                        'invoice_id': False,
                        'sibling_invoice_id': invoice.id})
            line._set_additional_fields(invoice)

    @api.multi
    def _generate_lines_to_invoice(
            self, invoices, references, invoices_origin, invoices_name,
            final, grouped):
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for order in self:
            group_key = order.id if grouped else (
                order.partner_invoice_id.id, order.currency_id.id)
            # We only want to create sections that have at least one
            # invoiceable line
            pending_section = None

            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(
                        line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and (
                       order.client_order_ref not in invoices_name[group_key]):
                        invoices_name[group_key].append(order.client_order_ref)
                if line.qty_to_invoice > 0 or (
                   line.qty_to_invoice < 0 and final):
                    if pending_section:
                        pending_section.invoice_line_create(
                            invoices[group_key].id,
                            pending_section.qty_to_invoice)
                        pending_section = None
                    line.invoice_line_create(
                        invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        self._generate_lines_to_invoice(
            invoices, references, invoices_origin, invoices_name,
            final, grouped)
        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(
                invoices_name[group_key]), 'origin': ', '.join(
                invoices_origin[group_key])})
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(_(
                'There is no invoiceable line. If a product has'
                ' a Delivered quantities invoicing policy, please make sure'
                ' that a quantity has been delivered.'))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(
                    _('There is no invoiceable line. If a product has a '
                        'Delivered quantities invoicing policy, please make'
                        ' sure that a quantity has been delivered.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            self._merge_line_qty(invoice)
            # Necessary to force computation of taxes. In account_invoice,
            # they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            # Idem for partner
            so_payment_term_id = invoice.payment_term_id.id
            invoice._onchange_partner_id()
            # To keep the payment terms set on the SO
            invoice.payment_term_id = so_payment_term_id
            invoice.message_post_with_view(
                'mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
