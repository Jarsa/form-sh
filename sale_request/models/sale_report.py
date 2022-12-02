# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields as odoo_fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    master_sale_order = odoo_fields.Boolean('Master Sale Order', readonly=True)

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        if fields is None:
            fields = {}
        fields['master_sale_order'] = (
            ", s.master_sale_order as master_sale_order")
        return super()._query(with_clause, fields, groupby, from_clause)
