# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican POS Management System",
    "version": "14.0.1.0.1",
    "author": "Vauxoo",
    "category": "Point of Sale",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "point_of_sale",
        "l10n_mx_edi",
        "l10n_mx_edi_partner_defaults",
    ],
    "demo": [],
    "data": [
        "data/3.3/cfdi.xml",
        "views/assets.xml",
        "views/pos_order_views.xml",
        "views/account_view.xml",
        "views/point_of_sale_view.xml",
        "views/pos_config_view.xml",
        "views/pos_payment_method_views.xml",
        "views/report_xml_session.xml",
    ],
    "external_dependencies": {
        "python": [
            "zeep",
            "zeep.transports",
        ],
    },
    "installable": True,
    "auto_install": False,
    "qweb": [
        "static/src/xml/CFDIUsageLine.xml",
        "static/src/xml/CFDIUsageScreen.xml",
        "static/src/xml/PaymentScreen.xml",
    ],
    "images": ["images/main_screenshot.png"],
}
