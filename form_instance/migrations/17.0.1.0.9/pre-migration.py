# Copyright 2025, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Global migration script to completely remove problematic modules from the system
    """
    
    modules_to_remove = [
        'mrp_production_plan',
        'mrp_production_surplus'
    ]
    
    for module_name in modules_to_remove:
        _logger.info(f"Processing module: {module_name}")
        
        # 1. Check if module exists in ir_module_module
        cr.execute("""
            SELECT id, state 
            FROM ir_module_module 
            WHERE name = %s
        """, (module_name,))
        
        module_result = cr.fetchone()
        if not module_result:
            _logger.info(f"Module {module_name} not found in ir_module_module")
            continue
            
        module_id, state = module_result
        _logger.info(f"Found module {module_name} with ID {module_id} and state '{state}'")
        
        # 2. Remove problematic picking types first
        cr.execute("""
            SELECT res_id, name 
            FROM ir_model_data 
            WHERE module = %s 
            AND model = 'stock.picking.type'
        """, (module_name,))
        
        picking_types = cr.fetchall()
        
        for picking_type_id, picking_type_name in picking_types:
            _logger.info(f"Processing picking type: {picking_type_name} (ID: {picking_type_id})")
            
            # Clean references in stock_picking
            cr.execute("""
                SELECT COUNT(*) 
                FROM stock_picking 
                WHERE picking_type_id = %s
            """, (picking_type_id,))
            
            picking_count = cr.fetchone()[0]
            if picking_count > 0:
                _logger.info(f"Found {picking_count} stock_picking records using picking type {picking_type_id}")
                
                # Find replacement
                cr.execute("""
                    SELECT id 
                    FROM stock_picking_type 
                    WHERE code = 'internal' 
                    AND id != %s
                    LIMIT 1
                """, (picking_type_id,))
                
                replacement = cr.fetchone()
                if replacement:
                    cr.execute("""
                        UPDATE stock_picking 
                        SET picking_type_id = %s 
                        WHERE picking_type_id = %s
                    """, (replacement[0], picking_type_id))
                    _logger.info(f"Updated {picking_count} stock_picking records to use picking type {replacement[0]}")
                else:
                    cr.execute("""
                        DELETE FROM stock_picking 
                        WHERE picking_type_id = %s
                    """, (picking_type_id,))
                    _logger.info(f"Deleted {picking_count} stock_picking records")
            
            # Clean references in mrp_production
            cr.execute("""
                SELECT COUNT(*) 
                FROM mrp_production 
                WHERE picking_type_id = %s
            """, (picking_type_id,))
            
            mrp_count = cr.fetchone()[0]
            if mrp_count > 0:
                _logger.info(f"Found {mrp_count} mrp_production records using picking type {picking_type_id}")
                
                # Find a suitable replacement picking type (manufacturing first)
                cr.execute("""
                    SELECT id 
                    FROM stock_picking_type 
                    WHERE code = 'mrp_operation' 
                    AND id != %s
                    LIMIT 1
                """, (picking_type_id,))
                
                mrp_replacement = cr.fetchone()
                
                if not mrp_replacement:
                    # If no mrp_operation, try internal
                    cr.execute("""
                        SELECT id 
                        FROM stock_picking_type 
                        WHERE code = 'internal' 
                        AND id != %s
                        LIMIT 1
                    """, (picking_type_id,))
                    mrp_replacement = cr.fetchone()
                
                if not mrp_replacement:
                    # Last resort: find ANY picking type
                    cr.execute("""
                        SELECT id 
                        FROM stock_picking_type 
                        WHERE id != %s
                        LIMIT 1
                    """, (picking_type_id,))
                    mrp_replacement = cr.fetchone()
                
                if mrp_replacement:
                    replacement_id = mrp_replacement[0]
                    cr.execute("""
                        UPDATE mrp_production 
                        SET picking_type_id = %s 
                        WHERE picking_type_id = %s
                    """, (replacement_id, picking_type_id))
                    _logger.info(f"Updated {mrp_count} mrp_production records to use picking type {replacement_id}")
                else:
                    # If absolutely no picking type exists, create a basic one
                    cr.execute("""
                        SELECT id 
                        FROM stock_warehouse 
                        LIMIT 1
                    """)
                    warehouse_result = cr.fetchone()
                    
                    if warehouse_result:
                        warehouse_id = warehouse_result[0]
                        
                        # Create a new basic picking type
                        cr.execute("""
                            INSERT INTO stock_picking_type 
                            (name, code, sequence_code, warehouse_id, create_date, write_date, create_uid, write_uid)
                            VALUES ('Manufacturing (Migration)', 'mrp_operation', 'MRP', %s, NOW(), NOW(), 1, 1)
                            RETURNING id
                        """, (warehouse_id,))
                        
                        new_picking_type_id = cr.fetchone()[0]
                        
                        cr.execute("""
                            UPDATE mrp_production 
                            SET picking_type_id = %s 
                            WHERE picking_type_id = %s
                        """, (new_picking_type_id, picking_type_id))
                        _logger.info(f"Created new picking type ID {new_picking_type_id} and updated {mrp_count} mrp_production records")
                    else:
                        _logger.error(f"Cannot update {mrp_count} mrp_production records - no warehouse found to create picking type")
                        raise Exception("Cannot migrate mrp_production records - no warehouse available")
        
        # 3. Remove all ir_model_data entries for this module
        cr.execute("""
            SELECT COUNT(*) 
            FROM ir_model_data 
            WHERE module = %s
        """, (module_name,))
        
        data_count = cr.fetchone()[0]
        if data_count > 0:
            cr.execute("""
                DELETE FROM ir_model_data 
                WHERE module = %s
            """, (module_name,))
            _logger.info(f"Deleted {data_count} ir_model_data entries for {module_name}")
        
        # 4. Mark module as uninstalled
        if state in ('installed', 'to upgrade', 'to remove'):
            cr.execute("""
                UPDATE ir_module_module 
                SET state = 'uninstalled' 
                WHERE name = %s
            """, (module_name,))
            _logger.info(f"Marked module {module_name} as uninstalled")
        
        # 5. Remove module dependencies
        cr.execute("""
            DELETE FROM ir_module_module_dependency 
            WHERE name = %s
        """, (module_name,))
        
        cr.execute("""
            SELECT COUNT(*) 
            FROM ir_module_module_dependency 
            WHERE module_id = %s
        """, (module_id,))
        
        dep_count = cr.fetchone()[0]
        if dep_count > 0:
            cr.execute("""
                DELETE FROM ir_module_module_dependency 
                WHERE module_id = %s
            """, (module_id,))
            _logger.info(f"Removed {dep_count} dependencies for {module_name}")
    
    _logger.info("Completed cleanup of problematic modules")