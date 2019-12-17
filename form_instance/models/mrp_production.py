# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_supplier_name = fields.Text(
        related='product_id.description_purchase')

    @api.multi
    @api.depends(
        'move_raw_ids.state', 'workorder_ids.move_raw_ids',
        'bom_id.ready_to_produce')
    def _compute_availability(self):
        for order in self:
            if not order.move_raw_ids:
                order.availability = 'none'
                continue
            if order.bom_id.ready_to_produce == 'all_available':
                order.availability = any(
                    move.state not in (
                        'assigned', 'done'
                    ) for move in order.move_raw_ids
                    ) and 'waiting' or 'assigned'
            else:
                move_raw_ids = order.move_raw_ids.filtered(
                    lambda m: m.product_qty)
                partial_list = [
                    x.state in (
                        'partially_available', 'assigned'
                    ) for x in move_raw_ids]
                assigned_list = [
                    x.state in (
                        'assigned', 'done') for x in move_raw_ids]
                order.availability = (
                    all(assigned_list) and 'assigned') or (
                    any(partial_list) and 'partially_available') or 'waiting'
