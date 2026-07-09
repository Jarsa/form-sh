# -*- coding: utf-8 -*-
import re

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

DNS_NS = 'https://www.densomex.com:4443/Addenda/DNS'
FREIGHT_PATTERN = re.compile(r'^(IMAP|EXAP|IMSL|EXSL|IMIR|EXIR)-.{2,}$')


class AccountMove(models.Model):
    _inherit = 'account.move'

    denso_addenda = fields.Boolean(
        string='Addenda DENSO',
        compute='_compute_denso_addenda',
        store=True,
        readonly=False,
        help='Genera la addenda DENSO (DNS) sobre el CFDI.',
    )
    denso_reference = fields.Char(
        string='Referencia / Orden de Compra',
        size=20,
        help='Orden de compra del cliente. Si es DO solo se colocan los 8 dígitos. '
             'Para las PO revisar las instrucciones en la parte inferior.',
    )
    denso_is_freight = fields.Boolean(
        string='Es Fletero',
        help='Si aplica, se enviará el nodo Freight en la addenda.',
    )
    denso_freight_reference = fields.Char(
        string='Referencia de Flete',
        size=15,
        help='Formato (IMAP|EXAP|IMSL|EXSL|IMIR|EXIR)-XX... (6 a 15 caracteres).',
    )

    @api.depends('partner_id')
    def _compute_denso_addenda(self):
        for move in self:
            move.denso_addenda = bool(move.partner_id.denso_addenda)

    @api.onchange('partner_id')
    def _onchange_partner_denso(self):
        for move in self:
            if move.partner_id:
                move.denso_is_freight = move.partner_id.denso_is_freight

    def _denso_validate(self):
        self.ensure_one()
        if self.denso_reference and len(self.denso_reference) > 20:
            raise UserError(_(
                'La Referencia (Orden de Compra) no puede exceder 20 caracteres.'
            ))
        if self.denso_is_freight:
            ref = self.denso_freight_reference or ''
            if not (6 <= len(ref) <= 15) or not FREIGHT_PATTERN.match(ref):
                raise UserError(_(
                    'La Referencia de Flete debe tener entre 6 y 15 caracteres y '
                    'cumplir el formato (IMAP|EXAP|IMSL|EXSL|IMIR|EXIR)-XX...'
                ))
        portal = self.partner_id.denso_supplier_portal
        if portal and not (3 <= len(portal) <= 10):
            raise UserError(_(
                'El Supplier Portal debe tener entre 3 y 10 caracteres.'
            ))

    def _denso_build_addenda_node(self):
        """Construye el nodo <DNS:Invoice> de la addenda."""
        self.ensure_one()
        self._denso_validate()

        nsmap = {'DNS': DNS_NS}
        invoice = etree.Element('{%s}Invoice' % DNS_NS, nsmap=nsmap)

        # Reference (opcional, solo proveedor nacional)
        if self.denso_reference:
            invoice.set('Reference', self.denso_reference)

        # Supplier (opcional, normalmente se completa en el portal)
        partner = self.partner_id
        if partner.denso_supplier_site or partner.denso_supplier_portal or partner.denso_supplier_name:
            supplier = etree.SubElement(invoice, '{%s}Supplier' % DNS_NS)
            supplier.set('SupplierSite', partner.denso_supplier_site or '')
            supplier.set('SupplierPortal', partner.denso_supplier_portal or '')
            supplier.set('SupplierName', partner.denso_supplier_name or partner.name or '')

        # Freight (opcional, solo fleteros)
        if self.denso_is_freight and self.denso_freight_reference:
            freight = etree.SubElement(invoice, '{%s}Freight' % DNS_NS)
            freight.set('Reference', self.denso_freight_reference)

        return invoice

    def _l10n_mx_edi_get_extra_common_report_values(self):
        # Punto de extensión disponible si se desea inyectar por reporte.
        return super()._l10n_mx_edi_get_extra_common_report_values()
