# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        "UPDATE stock_move SET product_uom = 8 WHERE product_uom = 24")
    cr.execute(
        "UPDATE product_template SET uom_id = 8 WHERE uom_id = 24")
    cr.execute(
        "UPDATE product_template SET equivalent_uom_id = 8"
        "WHERE equivalent_uom_id = 24")
    cr.execute(
        "UPDATE product_template SET uom_po_id = 8 WHERE uom_po_id = 24")
    cr.execute(
        "UPDATE mrp_bom_line  SET product_uom_id = 8"
        "WHERE product_uom_id = 24")
    cr.execute(
        "UPDATE purchase_order_line SET product_uom = 8"
        "WHERE product_uom = 24")
    cr.execute(
        "UPDATE stock_move_line SET product_uom_id = 8"
        "WHERE product_uom_id = 24")
    cr.execute(
        "DELETE FROM uom_uom WHERE id=24")
    cr.execute("UPDATE uom_uom SET name='M.L' WHERE id=8")
