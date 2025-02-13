{
    "name": "Stock Card Report",
    "summary": "Add stock card report on Inventory Reporting.",
    "version": "17.0.1.0.0",  # Update to Odoo 17 version
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-reporting",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "base", "date_range", "report_xlsx"],  # Ensure dependencies are correct
    "data": [
        "security/ir.model.access.csv",
        "data/paper_format.xml",
        "data/report_data.xml",
        "reports/stock_card_report.xml",
        "wizard/stock_card_report_wizard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_card_report/static/src/css/report.css",
            "stock_card_report/static/src/js/stock_card_report_backend.esm.js",
        ]
    },
    "installable": True,
    "application": False,
}
