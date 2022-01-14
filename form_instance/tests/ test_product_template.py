# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, Form


class TestProductTemplate(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_12')
        self.partner.ref = '10'
        self.partner.partner_code = '11'

    def test_form_id(self):
        with Form(self.env['product.template']) as product:
            product.name = "test"
            product.partner_ids.add(self.partner)
        self.assertEqual(product.id_form, '11-010-%s' % product.id)
