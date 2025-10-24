from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # override eliminado para no bloquear la confirmación real

    def action_cancel(self):
        return {
            'name':       'Cancellation Reason',
            'type':       'ir.actions.act_window',
            'res_model':  'sale.reason.wizard',
            'view_mode':  'form',
            'target':     'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_next_state':    'cancel',
            }
        }
