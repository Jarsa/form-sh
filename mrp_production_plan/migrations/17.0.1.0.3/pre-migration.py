# Copyright 2025, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration script to handle the removal of mrp_production_plan.return_raw_material_form
    picking type that is referenced by existing stock.picking records.
    """
    
    # Find the problematic picking type ID from ir_model_data
    cr.execute("""
        SELECT res_id 
        FROM ir_model_data 
        WHERE module = 'mrp_production_plan' 
        AND name = 'return_raw_material_form' 
        AND model = 'stock.picking.type'
    """)
    
    result = cr.fetchone()
    if not result:
        _logger.info("return_raw_material_form picking type not found in ir_model_data")
        return
        
    picking_type_id = result[0]
    _logger.info(f"Found return_raw_material_form picking type with ID: {picking_type_id}")
    
    # Check if there are pickings using this picking type
    cr.execute("""
        SELECT COUNT(*) 
        FROM stock_picking 
        WHERE picking_type_id = %s
    """, (picking_type_id,))
    
    count = cr.fetchone()[0]
    _logger.info(f"Found {count} pickings using return_raw_material_form picking type")
    
    if count > 0:
        # Find a suitable replacement picking type (internal transfer)
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
            # Update all pickings to use the replacement picking type
            cr.execute("""
                UPDATE stock_picking 
                SET picking_type_id = %s 
                WHERE picking_type_id = %s
            """, (replacement_id, picking_type_id))
            _logger.info(f"Updated {count} pickings to use picking type ID: {replacement_id}")
        else:
            # If no suitable replacement, create a basic internal picking type
            cr.execute("""
                SELECT id 
                FROM stock_warehouse 
                LIMIT 1
            """)
            warehouse_result = cr.fetchone()
            
            if warehouse_result:
                warehouse_id = warehouse_result[0]
                
                # Create a new internal picking type
                cr.execute("""
                    INSERT INTO stock_picking_type 
                    (name, code, sequence_code, warehouse_id, create_date, write_date, create_uid, write_uid)
                    VALUES ('Internal Transfers (Migration)', 'internal', 'INT', %s, NOW(), NOW(), 1, 1)
                    RETURNING id
                """, (warehouse_id,))
                
                new_picking_type_id = cr.fetchone()[0]
                
                # Update all pickings to use the new picking type
                cr.execute("""
                    UPDATE stock_picking 
                    SET picking_type_id = %s 
                    WHERE picking_type_id = %s
                """, (new_picking_type_id, picking_type_id))
                _logger.info(f"Created new picking type ID {new_picking_type_id} and updated {count} pickings")
            else:
                # Last resort: delete the pickings
                _logger.warning(f"No suitable replacement found, deleting {count} pickings")
                cr.execute("""
                    DELETE FROM stock_picking 
                    WHERE picking_type_id = %s
                """, (picking_type_id,))
    
    # Now it's safe to remove the ir_model_data entry
    cr.execute("""
        DELETE FROM ir_model_data 
        WHERE module = 'mrp_production_plan' 
        AND name = 'return_raw_material_form' 
        AND model = 'stock.picking.type'
    """)
    
    _logger.info("Successfully cleaned up return_raw_material_form picking type references")