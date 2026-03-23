# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_customer_product_to_save(self):
        self._check_customer_of_product()

    @api.onchange('order_line')
    def _onchange_order_line(self):
        self._check_customer_of_product()

    def _check_customer_of_product(self):
        for rec in self.order_line:
            rec._check_customer_product()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _check_customer_product(self):
        self.ensure_one()
        parameter = self.env['ir.config_parameter'].sudo().get_param(
            'sale_order_product_reference_partner.validate_product_partner')
        if not (self.product_id and parameter):
            return True
        if self.product_id.bypass_partner_validation:
            return True
        if not self.order_id.partner_id:
            raise ValidationError(
                _('No se ha definido un cliente en el pedido de venta.'))
        if not self.product_id.partner_ids:
            raise ValidationError(
                _('El producto "%s" no tiene clientes permitidos definidos.')
                % self.product_id.name)
        if self.order_id.partner_id not in self.product_id.partner_ids:
            raise ValidationError(
                _('El cliente "%s" no está permitido para el producto "%s".')
                % (self.order_id.partner_id.name, self.product_id.name))
        return True
