# models/sale_order.py
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # COMENTADO: En Odoo 17 no se debe redefinir selection completa
    # Usar traducciones en .po en su lugar
    # state = fields.Selection([
    #     ('draft',     'Cotización'),
    #     ('sent',      'Cotización enviada'),
    #     ('confirmed', 'Cotización confirmada'),
    #     ('sale',      'Orden de venta'),
    #     ('cancel',    'Cancelado'),
    # ], string='Estado',
    #    readonly=True, copy=False, index=True,
    #    default='draft',
    #    help="Gasto del flujo de la orden de venta")

    # En su lugar, puedes usar selection_add si necesitas agregar nuevos estados:
    # state = fields.Selection(selection_add=[
    #     ('new_state', 'Nuevo Estado'),
    # ])
