# -*- coding: utf-8 -*-
# Bridge module to correctly emit CFDI Carta Porte 3.1 on Odoo 17.
# Fixes the broken l10n_mx_edi_stock_extended_31 template, which declared
# Version="3.1" while keeping the deprecated CartaPorte20 namespace (rejected by SAT/PAC).
{
    "name": "Mexico - Carta Porte 3.1 Fix (namespace CartaPorte31)",
    'countries': ['mx'],
    'version': '17.0.1.2.0',
    'category': 'Accounting/Localizations/EDI',
    'description': """
Corrige la emisión de Carta Porte 3.1 en Odoo 17.

El módulo estándar l10n_mx_edi_stock_extended_31 declaraba Version="3.1"
pero mantenía el namespace obsoleto http://www.sat.gob.mx/CartaPorte20, por lo
que el PAC/SAT rechazaba el CFDI. Este puente reemplaza por completo la
plantilla QWeb con una versión limpia en el namespace CartaPorte31
(http://www.sat.gob.mx/CartaPorte31) reutilizando todos los campos y datos
que ya arma la cadena l10n_mx_edi_stock -> _stock_30 -> _extended -> _extended_30 -> _extended_31.

Cubre: traslado nacional (autotransporte), comercio exterior (COMEX) y material peligroso.
""",
    'depends': [
        'l10n_mx_edi_stock_extended_31',
    ],
    'data': [
        'data/cfdi_cartaporte_31.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
