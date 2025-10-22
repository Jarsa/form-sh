# Copyright 2021 Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False, date=None):
        context = self._context.copy()
        context.update({
            'final': final,
        })
        self = self.with_context(context)
        moves = super(SaleOrder, self)._create_invoices(grouped, final, date)
        if not final:
            return moves
        advance_product = self.company_id.l10n_mx_edi_product_advance_id
        advance_lines = {}
        processed_ids = []
        for line in moves.invoice_line_ids.filtered(
                lambda l: l.product_id == advance_product):
            domain = line.move_id._l10n_mx_edi_get_advance_aml_domain()
            domain.extend([
                ('move_id.payment_state', 'in', [
                    'paid', 'in_payment', 'partial']),
                ('sale_line_ids', 'in', self.order_line.ids),
                ('id', 'not in', processed_ids),
            ])
            adv_lines = self.env['account.move.line'].search(domain)
            if adv_lines and len(adv_lines) > 1:
                adv_lines = adv_lines[0]
                processed_ids.append(adv_lines.id)
            move = line.move_id
            lines_to_remove = [(2, line.id, 0)]
            section_line = move.invoice_line_ids.filtered(
                lambda l: l.display_type == 'line_section' and
                l.name == _('Down Payments'))
            if section_line:
                lines_to_remove.append((2, section_line.id, 0))
            move.write({
                'invoice_line_ids': lines_to_remove,
            })
            if adv_lines:
                advance_lines.setdefault(move, []).append(adv_lines.id)
        for move, line_ids in advance_lines.items():
            for line_id in line_ids:
                move.js_assign_outstanding_line(line_id)
        return moves


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        """ Change price unit and quantity to 0 when Odoo is creating the final invoice
        to prevent negative total (this makes odoo to convert it in credit note) when there
        is a partial invoice for the order.
        That line will be deleted later by this module.
        """
        res = super()._prepare_invoice_line(**optional_values)
        advance_product = self.company_id.l10n_mx_edi_product_advance_id
        if res.get('product_id') == advance_product.id and self._context.get('final'):
            res.update({
                'price_unit': 0,
                'quantity': 0,
            })
        return res
