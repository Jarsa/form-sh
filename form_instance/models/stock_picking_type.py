# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockPickingType(models.Model):
    _inherit = ['stock.picking.type', 'mail.thread']
    _name = 'stock.picking.type'
