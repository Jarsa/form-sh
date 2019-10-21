# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from psycopg2 import Error
import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info('Remove product category validations')
    cr.execute('DELETE FROM product_category_validation')
    _logger.info('Merging quants')
    query = """WITH
    dupes AS (
        SELECT min(id) as to_update_quant_id,
            (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)]
            as to_delete_quant_ids,
            SUM(reserved_quantity) as reserved_quantity,
            SUM(quantity) as quantity
        FROM stock_quant
        GROUP BY product_id, location_id
        HAVING count(id) > 1
    ),
    _up AS (
        UPDATE stock_quant q
            SET quantity = d.quantity,
                reserved_quantity = d.reserved_quantity
        FROM dupes d
        WHERE d.to_update_quant_id = q.id
    )
    DELETE FROM stock_quant
    WHERE id in (SELECT unnest(to_delete_quant_ids) from dupes)
    """
    try:
        with cr.savepoint():
            cr.execute(query)
    except Error as e:
        _logger.info('an error occured while merging quants: %s', e.pgerror)
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('Unlink zero quants')
    env['stock.quant']._unlink_zero_quants()
    _logger.info('Remove lot from quants')
    env['stock.quant'].search([]).write({'lot_id': False})
    _logger.info('Change products tracking to none')
    env['product.template'].search([]).write({
        'tracking': 'none',
    })
    _logger.info('Remove lots from stock move lines')
    cr.execute('''
        UPDATE stock_move_line
        SET lot_id = NULL, lot_name = NULL, lot_produced_id = NULL
    ''')
    _logger.info('Remove all lots')
    env['stock.production.lot'].search([]).unlink()
