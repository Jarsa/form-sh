# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo.tests.common import TransactionCase


class TestMrpProductionPlan(TransactionCase):

    def setUp(self):
        super(TestMrpProductionPlan, self).setUp()
        self.product = self.env.ref('product.product_product_27')
        self.bom = self.env.ref('mrp.mrp_bom_laptop_cust')
        self.route_one = self.env.ref('mrp.mrp_routing_0')
        self.route_two = self.env.ref('mrp.mrp_routing_1')
        self.route_one.write({
            'product_id': self.product.id,
            'sequence': 1,
        })
        self.route_two.write({
            'product_id': self.product.id,
            'sequence': 2,
        })

    def create_manufacturing_request(self):
        request = self.env['mrp.production.request'].create({
            'name': '/manufacturing_request',
            'product_qty': 300.0,
            'product_id': self.product.id,
            'bom_id': self.bom.id,
            'product_uom_id': self.product.uom_id.id,
        })
        request.button_to_approve()
        request.button_approved()
        return request

    def create_production_plan(self):
        plan = self.env['mrp.production.plan'].create({
            'category_id': self.product.categ_id.id,
        })
        plan.get_mrp_production_requests()
        line = plan.line_ids
        self.assertEqual(line.routing_id, self.route_one)
        line.update({
            'routing_id': self.route_two.id,
            'requested_kit_qty': 20.0,
        })
        return plan

    def test_01_purchase_plan_routing(self):
        self.create_manufacturing_request()
        plan = self.create_production_plan()
        plan.run_plan()
        production = plan.production_ids
        self.assertEqual(production.routing_id, self.route_two)
        self.assertEqual(
            len(self.route_two.operation_ids), production.workorder_count)
