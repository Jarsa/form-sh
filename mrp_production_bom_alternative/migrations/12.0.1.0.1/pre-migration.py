# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).


from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        products = env['product.template'].search(
            [('bom_ids', '!=', False)])
        for product in products:
            boms = product.bom_ids
            sequence = 1
            for bom in boms:
                bom.write({
                    'sequence': sequence,
                })
                sequence += 1
