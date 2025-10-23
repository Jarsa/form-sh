from odoo import api, models, fields
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_mx_edi_usage = fields.Char(string="Fiscal Usage", related="partner_id.commercial_partner_id.l10n_mx_edi_usage", store=True)
    l10n_mx_edi_payment_method_id = fields.Many2one("l10n_mx_edi.payment.method", string="Payment Method", related="partner_id.commercial_partner_id.l10n_mx_edi_payment_method_id", store=True)

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        """Set payment method and usage"""
        res = super()._onchange_partner_id()
        if self.move_type in ("in_invoice", "in_refund") or not self.partner_id.commercial_partner_id:
            return res
        
        # Obtener el partner comercial
        commercial_partner = self.partner_id.commercial_partner_id

        # Validación para asegurarse de que l10n_mx_edi_usage sea un valor válido
        valid_usage_values = ["P01", "P02", "P03", "P04"]  # Lista de valores válidos, ajusta según corresponda.
        if commercial_partner.l10n_mx_edi_usage not in valid_usage_values:
            raise ValidationError(
                f"El valor '{commercial_partner.l10n_mx_edi_usage}' no es válido para el campo 'l10n_mx_edi_usage'. Los valores válidos son: {', '.join(valid_usage_values)}."
            )

        # Asignar los valores correctamente
        self.l10n_mx_edi_payment_method_id = commercial_partner.l10n_mx_edi_payment_method_id
        self.l10n_mx_edi_usage = commercial_partner.l10n_mx_edi_usage

        return res

    @api.model_create_multi
    def create(self, vals_list):
        onchanges = {
            "_onchange_partner_id": ["l10n_mx_edi_payment_method_id", "l10n_mx_edi_usage", "partner_bank_id"],
        }
        for onchange_method, changed_fields in onchanges.items():
            for vals in vals_list:
                if any(f not in vals for f in changed_fields):
                    invoice = self.new(vals)
                    getattr(invoice, onchange_method)()
                    for field in changed_fields:
                        if field not in vals and invoice[field]:
                            vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)
        return super().create(vals_list)
