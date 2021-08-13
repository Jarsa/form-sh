# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class IrActionsReport(TransactionCase):

    def setUp(self):
        super().setUp()
        self.report = self.env.ref('purchase.action_report_purchase_order')
        self.purchase_order = self.env.ref('purchase.purchase_order_6')

    def test_10_print_report(self):
        report = self.report.report_action(self.purchase_order.ids)
        self.assertIsInstance(report, dict)
