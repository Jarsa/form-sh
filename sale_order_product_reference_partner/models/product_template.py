# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partner_ids = fields.Many2many(
        'res.partner',
        string='Clientes permitidos',
    )
    bypass_partner_validation = fields.Boolean(
        string='Ignorar validación de cliente',
        copy=False,
        help='Al activar esta opción, este producto podrá usarse en '
             'pedidos y requisiciones de cualquier cliente, '
             'sin importar la lista de clientes permitidos.',
    )
