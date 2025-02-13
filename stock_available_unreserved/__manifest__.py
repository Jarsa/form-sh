{
    "name": "Stock Available Unreserved",
    "summary": "Quantity of stock available for immediate use",
    "version": "17.0.1.0.0",  # Updated version
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "development_status": "Production/Stable",
    "maintainers": ["LoisRForgeFlow"],
    "website": "https://github.com/OCA/stock-logistics-availability",
    "category": "Warehouse Availability",
    "depends": ["stock"],  # Ensure stock dependency is still valid
    "data": ["views/stock_quant_view.xml", "views/product_view.xml"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
