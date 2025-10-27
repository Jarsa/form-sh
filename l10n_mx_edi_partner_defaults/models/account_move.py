
from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_mx_edi_usage = fields.Selection(
        selection=[
            ("G01", "Adquisición de mercancías"),
            ("G02", "Devoluciones, descuentos o bonificaciones"),
            ("G03", "Gastos en general"),
            ("I01", "Construcciones"),
            ("I02", "Mobilario y equipo de oficina por inversiones"),
            ("I03", "Equipo de transporte"),
            ("I04", "Equipo de computo y accesorios"),
            ("I05", "Dados, troqueles, moldes, matrices y herramental"),
            ("I06", "Comunicaciones telefónicas"),
            ("I07", "Comunicaciones satelitales"),
            ("I08", "Otra maquinaria y equipo"),
            ("P01", "Por definir"),
            ("S01", "Sin efectos fiscales"),
        ],
        string="Fiscal Usage",
        store=True,
        default="S01",  # Valor permitido por la selección
        help="This usage will be used instead of the default one for invoices.",
    )

    l10n_mx_edi_payment_method_id = fields.Many2one(
        "l10n_mx_edi.payment.method", string="Payment Method", related="partner_id.commercial_partner_id.l10n_mx_edi_payment_method_id", store=True
    )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        commercial_partner = self.partner_id.commercial_partner_id
        if commercial_partner:
            self.l10n_mx_edi_payment_method_id = commercial_partner.l10n_mx_edi_payment_method_id
            usage_values = [
                "G01", "G02", "G03", "I01", "I02", "I03", "I04", "I05", "I06", "I07", "I08", "P01", "S01"
            ]
            if commercial_partner.l10n_mx_edi_usage in usage_values:
                self.l10n_mx_edi_usage = commercial_partner.l10n_mx_edi_usage
            else:
                self.l10n_mx_edi_usage = "S01"
        return res


     # --------------------------
    # BRIDGES PARA LA ADDENDA
    # --------------------------
    def _mx_get_cfdi_values(self):
        """
        Devuelve los cfdi_values usando el helper que exista en este build.
        Evita lógica en QWeb y unifica nombres nuevos/legacy.
        """
        self.ensure_one()
        if hasattr(self, "_get_l10n_mx_edi_cfdi_values"):
            return self._get_l10n_mx_edi_cfdi_values()
        if hasattr(self, "_l10n_mx_edi_get_invoice_cfdi_values"):
            return self._l10n_mx_edi_get_invoice_cfdi_values()
        return {}

    def _mx_get_serie_and_folio(self):
        """
        Devuelve {'serie': ..., 'folio_number': ...} si existe el helper del core.
        """
        self.ensure_one()
        if hasattr(self, "_l10n_mx_edi_get_serie_and_folio"):
            return self._l10n_mx_edi_get_serie_and_folio()
        return {}