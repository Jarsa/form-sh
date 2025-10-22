# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class RepairOrder(models.Model):
    _inherit = "repair.order"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string="Payment Method",
        readonly=True,
        states={'draft': [('readonly', False)]},
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

    @api.onchange('partner_id', 'invoice_method', 'partner_invoice_id')
    def _onchange_partner_id_invoice_method(self):
        """Set payment method and usage"""
        l10n_mx_edi_payment_method_id = False
        l10n_mx_edi_usage = False
        partner = self.partner_invoice_id.commercial_partner_id
        if not self.partner_invoice_id:
            partner = self.partner_id.commercial_partner_id
        if partner and self.invoice_method != 'none':
            l10n_mx_edi_payment_method_id = (
                partner.commercial_partner_id.l10n_mx_edi_payment_method_id
            )
            l10n_mx_edi_usage = partner.commercial_partner_id.l10n_mx_edi_usage
        self.l10n_mx_edi_payment_method_id = l10n_mx_edi_payment_method_id
        self.l10n_mx_edi_usage = l10n_mx_edi_usage

    def _create_invoices(self, group=False):
        res = super()._create_invoices(group)
        for repair_id, invoice_id in res.items():
            repair = self.env['repair.order'].browse(repair_id)
            invoice = self.env['account.move'].browse(invoice_id)
            invoice.write({
                'l10n_mx_edi_usage': repair.l10n_mx_edi_usage,
                'l10n_mx_edi_payment_method_id': (
                    repair.l10n_mx_edi_payment_method_id),
            })
        return res
