# Copyright 2018, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
        SET module = 'form_instance'
        WHERE module = 'form
    '""")
    cr.execute("""
        UPDATE ir_model_data
        SET name = 'module_form_instance'
        WHERE name = 'module_form'
        AND module = 'base'
        AND model = 'ir.module.module'
    """)
    cr.execute("""
        UPDATE ir_module_module_dependency
        SET name = 'module_form_instance'
        WHERE name = 'module_form'
    """)
    cr.execute("""
        UPDATE ir_translation
        SET module = 'module_form_instance'
        WHERE module = 'module_form';""")
