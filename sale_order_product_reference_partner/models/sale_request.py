
# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleRequest(models.Model):
    _inherit = 'sale.request'

    @api.constrains('line_ids')
    def _check_customer_product_to_save(self):
        self._check_customer_of_product()

    @api.onchange('line_ids')
    def _onchange_order_line(self):
        self._check_customer_of_product()

    @api.model
    def _check_customer_of_product(self):
        for rec in self.line_ids:
            rec._check_customer_product()


class SaleRequestLine(models.Model):
    _inherit = 'sale.request.line'

    @api.model
    def _check_customer_product(self):
        # if self.product_id:
        #     if not self.request_id.partner_id:
        #         raise ValidationError(
        #             _('You has not selected a Customer to Sale Order'))
        #     if not self.product_id.partner_ids:
        #         raise ValidationError(
        #             _('The product %s have not asiggned any customer')
        #             % self.product_id.name)
        #     if self.request_id.partner_id not in self.product_id.partner_ids:
        #         raise ValidationError(
        #             _('The Customer %s is different to have'
        #                 ' the product %s')
        #             % (
        #                 self.request_id.partner_id.name,
        #                 self.product_id.name)
        #             )
        return True
