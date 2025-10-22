from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_mx_edi_voucher_nss = fields.Char(
        "NSS", help="Optional attribute to express the Employee Social Security Number"
    )
