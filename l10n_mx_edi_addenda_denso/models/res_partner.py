# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    denso_addenda = fields.Boolean(
        string='Requiere Addenda DENSO',
        help='Marca a este cliente para generar la addenda DENSO (DNS) en sus facturas.',
    )

    def write(self, vals):
        res = super().write(vals)
        if 'denso_addenda' in vals:
            addenda = self.env.ref(
                'l10n_mx_edi_addenda_denso.denso_addenda_view',
                raise_if_not_found=False,
            )
            if addenda and 'l10n_mx_edi_addenda' in self._fields:
                for partner in self:
                    partner.l10n_mx_edi_addenda = addenda.id if vals['denso_addenda'] else False
        return res
    denso_is_freight = fields.Boolean(
        string='Es Fletero (Freight)',
        help='Si el proveedor es un fletero, se enviará el nodo Freight en la addenda.',
    )
    # Valores por defecto del nodo Supplier (normalmente se completa en el portal,
    # se dejan disponibles por si se desean enviar).
    denso_supplier_site = fields.Char(
        string='Supplier Site',
        size=20,
        help='SupplierSite. Estará disponible después del 6 de julio (se completa en el portal).',
    )
    denso_supplier_portal = fields.Char(
        string='Supplier Portal',
        size=10,
        help='SupplierPortal (3-10 caracteres). Portal Proveedores.',
    )
    denso_supplier_name = fields.Char(
        string='Supplier Name',
        help='SupplierName tal como aparece en el portal de proveedores.',
    )
