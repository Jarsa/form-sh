# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        self._check_qty_to_produce()
        return super().record_production()

    def _check_qty_to_produce(self):
        self.ensure_one()
        quantity = self.qty_production
        qty_produced = self.qty_produced
        self._calcule_limit_production_work_order(quantity, qty_produced)

    def _calcule_limit_production_work_order(self, quantity, qty_produced):
        for rec in self:
            # qty_limit = var used by store 10% from
            # quantity to produce plus quantity
            qty_limit = quantity + 3
            qty_limit = qty_limit - qty_produced
            if rec.qty_producing <= qty_limit:
                return True
            template = self.env.ref(
                'mrp_production_limit.send_mail_alert_production')
            template.send_mail(rec.production_id.id, True)
            raise ValidationError(
                _('You can not produce more than %s %s')
                % (qty_limit, rec.product_uom_id.name))

    # I over this function because to produce a normal MO
    # Odoo read qty to produce from other field than
    # It does not use in a workorder
    @api.model
    def _calcule_limit_production_manufacture_order(
        self, quantity, qty_produced,
        qty_producing, order
            ):
        # qty_limit = var used by store 10% from
        # quantity to produce plus quantity
        qty_limit = quantity + 3
        qty_limit = qty_limit - qty_produced
        if qty_producing <= qty_limit:
            return True
        template = self.env.ref(
            'mrp_production_limit.send_mail_alert_production')
        template.send_mail(order.id, True)
        raise ValidationError(
            _('You can not produce more than %s %s')
            % (qty_limit, order.product_uom_id.name))
