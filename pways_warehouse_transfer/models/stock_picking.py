# -*- coding: utf-8 -*-
from odoo import fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer_id = fields.Many2one('stock.transfer')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            if all([picking.state == 'done' for picking in picking.transfer_id.picking_ids]):
                picking.transfer_id.state = 'done'
                # print('transfer_id******************************',picking.transfer_id)
                picking.sudo().transfer_id.sudo().write({'state': 'done'})
        return res
