# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

{
    "name": "Cost Margin Utility Report",
    "summary": "Generate Cost Margin Utility Report",
    "version": "12.0.1.0.0",
    "category": "Report",
    "author": "Jarsa Sistemas",
    "website": "https://www.jarsa.com.mx",
    "license": "LGPL-3",
    "depends": ["stock", "mrp", "sale", "purchase", ],
    "installable": False,
    "data": [
        "views/cost_margin_utility_report_views.xml",
        "wizard/cost_margin_utility_report_wizard_view.xml",
        "security/ir.model.access.csv",
    ],
}
