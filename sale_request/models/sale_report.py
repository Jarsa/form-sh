# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields as odoo_fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    master_sale_order = odoo_fields.Boolean('Master Sale Order', readonly=True)

    def _query(self, *args, **kwargs):
        """ Override _query to add the master_sale_order field dynamically """
        if 'fields' in kwargs and isinstance(kwargs['fields'], list):
            kwargs['fields'].append("s.master_sale_order as master_sale_order")
        return super()._query(*args, **kwargs)
