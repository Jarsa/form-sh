# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string="Payment Method",
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='This payment method will be defined in the invoices related to '
        'this order.',
        default=lambda self: self.env.ref('l10n_mx_edi.payment_method_otros',
                                          raise_if_not_found=False))

    def _get_usage_selection(self):
        return self.env['account.move'].fields_get().get(
            'l10n_mx_edi_usage').get('selection')

    l10n_mx_edi_usage = fields.Selection(
        _get_usage_selection, 'Usage', default='P01',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='This usage will be used in the invoices related to this order.'
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Set payment method and usage"""
        if self.partner_id.commercial_partner_id:
            self.l10n_mx_edi_payment_method_id = (
                self.partner_id.commercial_partner_id
                .l10n_mx_edi_payment_method_id)
            self.l10n_mx_edi_usage = (
                self.partner_id.commercial_partner_id.l10n_mx_edi_usage)

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({
            'l10n_mx_edi_payment_method_id': (
                self.l10n_mx_edi_payment_method_id.id),
            'l10n_mx_edi_usage': self.l10n_mx_edi_usage,
        })
        return res
