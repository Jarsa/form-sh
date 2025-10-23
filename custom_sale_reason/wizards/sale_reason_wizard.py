from odoo import models, fields, api, _

class SaleReasonWizard(models.TransientModel):
    _name = 'sale.reason.wizard'
    _description = 'Reason for State Change'

    sale_order_id = fields.Many2one('sale.order', required=True)
    next_state    = fields.Selection([
        ('draft',     'Cotización'),
        ('sent',      'Cotización enviada'),
        ('confirmed', 'Cotización confirmada'),
        ('sale',      'Orden de venta'),
        ('cancel',    'Cancelado'),
    ], required=True, readonly=True)

    # Ahora es Many2one a nuestro catálogo
    specific_reason_id = fields.Many2one(
        'sale.reason.option',
        string='Motivo específico',
        domain="[('state','=', next_state)]"
    )

    reason = fields.Text('Descripción adicional', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # traemos el estado destino desde contexto
        if self.env.context.get('default_next_state'):
            res['next_state'] = self.env.context['default_next_state']
        return res

    def apply_reason(self):
        self.ensure_one()
        label = dict(self._fields['next_state'].selection)[self.next_state]
        # si hay motivo específico, lo mostramos; si no, 'N/A'
        specific = self.specific_reason_id.name if self.specific_reason_id else 'N/A'
        self.sale_order_id.write({'state': self.next_state})
        body = _(
            "🔁 Estado cambiado a %s\n | "
            "Motivo específico: %s\n\n | "
            "Descripción: %s"
        ) % (label, specific, self.reason)
        self.sale_order_id.message_post(body=body)
        return {'type': 'ir.actions.act_window_close'}
