# Copyright 2021 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# List of modules to remove (uninstall)
to_remove = [
    'stock_uom_equivalence',
]


def process_equivalence(env):
    products = env['product.template'].search([
        ('equivalent_factor', '!=', False),
        ('equivalent_uom_id', '!=', False),
    ])
    count = 1
    for product in products:
        _logger.warning('Products processed %s of %s' % (count, len(products)))
        count += 1
        secondary_unit = env['product.secondary.unit'].create({
            'name': product.equivalent_uom_id.name,
            'code': product.equivalent_uom_id.name,
            'product_tmpl_id': product.id,
            'uom_id': product.equivalent_uom_id.id,
            'factor': product.equivalent_factor,
        })
        product.with_context(migration=True).write({
            'purchase_secondary_uom_id': secondary_unit.id,
            'stock_secondary_uom_id': secondary_unit.id,
        })
        order_lines = env['purchase.order.line'].search([
            ('product_id.product_tmpl_id', '=', product.id),
        ])
        order_lines.write({
            'secondary_uom_id': secondary_unit.id,
        })
        po_count = 1
        for line in order_lines:
            _logger.warning('Order lines processed %s of %s' % (po_count, len(order_lines)))
            po_count += 1
            line._onchange_product_qty_purchase_order_secondary_unit()
        # move_lines = env['stock.move.line'].search([
        #     ('product_id.product_tmpl_id', '=', product.id),
        # ])
        # _logger.warning('Processing %s stock move lines' % (len(move_lines)))
        # move_lines.with_context(do_not_unreserve=True).write({
        #     'secondary_uom_id': secondary_unit.id,
        # })
        # move_lines.with_context(do_not_unreserve=True)._compute_qty_done()
        # moves = env['stock.move'].search([
        #     ('product_id.product_tmpl_id', '=', product.id),
        # ])
        # _logger.warning('Processing %s stock move lines' % (len(moves)))
        # moves.with_context(do_not_unreserve=True).write({
        #     'secondary_uom_id': secondary_unit.id,
        # })
        # moves.with_context(do_not_unreserve=True)._compute_product_uom_qty()


@openupgrade.migrate()
def migrate(env, installed_version):
    process_equivalence(env)
    modules_to_remove = env['ir.module.module'].search([
        ('name', 'in', to_remove)])
    modules_to_remove += modules_to_remove.downstream_dependencies()
    modules_to_remove.module_uninstall()
