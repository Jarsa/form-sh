# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
