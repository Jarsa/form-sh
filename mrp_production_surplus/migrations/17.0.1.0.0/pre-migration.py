# Copyright 2025, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration script to handle the removal of mrp_production_surplus.mrp_production_surplus_type_operation
    picking type that is referenced by existing mrp.production records.
    """
    
    # Find the problematic picking type ID from ir_model_data
    cr.execute("""
        SELECT res_id 
        FROM ir_model_data 
        WHERE module = 'mrp_production_surplus' 
        AND name = 'mrp_production_surplus_type_operation' 
        AND model = 'stock.picking.type'
    """)
    
    result = cr.fetchone()
    if not result:
        _logger.info("mrp_production_surplus_type_operation picking type not found in ir_model_data")
        return
        
    picking_type_id = result[0]
    _logger.info(f"Found mrp_production_surplus_type_operation picking type with ID: {picking_type_id}")
    
    # Check if there are mrp.production records using this picking type
    cr.execute("""
        SELECT COUNT(*) 
        FROM mrp_production 
        WHERE picking_type_id = %s
    """, (picking_type_id,))
    
    count = cr.fetchone()[0]
    _logger.info(f"Found {count} mrp.production records using mrp_production_surplus_type_operation picking type")
    
    if count > 0:
        # Find a suitable replacement picking type (manufacturing)
        cr.execute("""
            SELECT id 
            FROM stock_picking_type 
            WHERE code = 'mrp_operation' 
            AND id != %s
            LIMIT 1
        """, (picking_type_id,))
        
        replacement_result = cr.fetchone()
        
        if not replacement_result:
            # If no mrp_operation, try internal
            cr.execute("""
                SELECT id 
                FROM stock_picking_type 
                WHERE code = 'internal' 
                AND id != %s
                LIMIT 1
            """, (picking_type_id,))
            replacement_result = cr.fetchone()
        
        if replacement_result:
            replacement_id = replacement_result[0]
            # Update all mrp.production records to use the replacement picking type
            cr.execute("""
                UPDATE mrp_production 
                SET picking_type_id = %s 
                WHERE picking_type_id = %s
            """, (replacement_id, picking_type_id))
            _logger.info(f"Updated {count} mrp.production records to use picking type ID: {replacement_id}")
        else:
            # Set picking_type_id to NULL if no suitable replacement
            _logger.warning(f"No suitable replacement found, setting picking_type_id to NULL for {count} mrp.production records")
            cr.execute("""
                UPDATE mrp_production 
                SET picking_type_id = NULL 
                WHERE picking_type_id = %s
            """, (picking_type_id,))
    
    # Check for stock.picking records also using this picking type
    cr.execute("""
        SELECT COUNT(*) 
        FROM stock_picking 
        WHERE picking_type_id = %s
    """, (picking_type_id,))
    
    picking_count = cr.fetchone()[0]
    if picking_count > 0:
        _logger.info(f"Found {picking_count} stock.picking records using this picking type")
        
        # Find internal picking type for stock.picking
        cr.execute("""
            SELECT id 
            FROM stock_picking_type 
            WHERE code = 'internal' 
            AND id != %s
            LIMIT 1
        """, (picking_type_id,))
        
        internal_result = cr.fetchone()
        if internal_result:
            internal_id = internal_result[0]
            cr.execute("""
                UPDATE stock_picking 
                SET picking_type_id = %s 
                WHERE picking_type_id = %s
            """, (internal_id, picking_type_id))
            _logger.info(f"Updated {picking_count} stock.picking records to use internal picking type ID: {internal_id}")
        else:
            _logger.warning(f"No internal picking type found, deleting {picking_count} stock.picking records")
            cr.execute("""
                DELETE FROM stock_picking 
                WHERE picking_type_id = %s
            """, (picking_type_id,))
    
    # Now it's safe to remove the ir_model_data entry
    cr.execute("""
        DELETE FROM ir_model_data 
        WHERE module = 'mrp_production_surplus' 
        AND name = 'mrp_production_surplus_type_operation' 
        AND model = 'stock.picking.type'
    """)
    
    _logger.info("Successfully cleaned up mrp_production_surplus_type_operation picking type references")