# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    # This field will take of value from a MO related
    # and it will going to show or hide the workorders on base
    # its value
    mo_products_is_reserved = fields.Boolean(
        related='production_id.is_already_reserved',
        store=True,
    )
