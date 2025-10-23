# models/sale_order.py
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft',     'Cotización'),
        ('sent',      'Cotización enviada'),
        ('confirmed', 'Cotización confirmada'),
        ('sale',      'Orden de venta'),
        ('cancel',    'Cancelado'),
    ], string='Estado',
       readonly=True, copy=False, index=True,
       default='draft',
       help="Gasto del flujo de la orden de venta")
