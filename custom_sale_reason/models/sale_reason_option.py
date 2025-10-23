# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleReasonOption(models.Model):
    _name = 'sale.reason.option'
    _description = 'Opciones de motivo de cambio de estado'

    name = fields.Char(string='Motivo', required=True)
    code = fields.Char(string='Código interno', required=True)
    state = fields.Selection([
        ('confirmed', 'Cotización confirmada'),
        ('cancel',    'Cancelado'),
    ], string='Para estado', required=True,
       help="Indica a qué transición aplica este motivo")