# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    sample_selectable = fields.Boolean(
        help='If you select this checkbox this route'
        ' will appear on the stock sample wizard of sale orders.',
    )
