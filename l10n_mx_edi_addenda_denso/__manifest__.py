# -*- coding: utf-8 -*-
{
    'name': 'EDI Addenda DENSO (DNS)',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localizations/EDI',
    'summary': 'Addenda DENSO México (DNS) para CFDI 4.0',
    'description': """
Addenda DENSO (DNS)
===================
Genera la addenda requerida por DENSO México sobre el CFDI 4.0.

Estructura basada en el XSD DNS:
    - Invoice/@Reference  : Orden de compra del cliente (opcional, máx 20).
                            Si es DO solo se colocan los 8 dígitos.
    - Supplier            : SupplierSite, SupplierPortal, SupplierName
                            (se completa en el portal de proveedores).
    - Freight/@Reference  : Referencia de flete, solo cuando es fletero.
                            Patrón (IMAP|EXAP|IMSL|EXSL|IMIR|EXIR)-XX...

Namespace: https://www.densomex.com:4443/Addenda/DNS
""",
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': [
        'l10n_mx_edi',
    ],
    'data': [
        'data/cfdi_addenda_denso.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
