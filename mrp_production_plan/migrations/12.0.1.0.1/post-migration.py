# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).


from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        rountigs = env['mrp.routing'].with_context(
            active_test=False).search([
                ('product_id', '!=', False)])
        for product in rountigs.mapped('product_id'):
            routes = rountigs.filtered(
                lambda r: r.product_id.id == product.id)
            sequence = 1
            for route in routes:
                route.write({
                    'sequence': sequence,
                })
                sequence += 1
