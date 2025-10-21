# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpProductionPlanLine(models.Model):
    _inherit = 'mrp.production.plan.line'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')
