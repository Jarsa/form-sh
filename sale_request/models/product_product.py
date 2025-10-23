# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api, fields
import re


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Campo computado para mostrar información de búsqueda
    search_info = fields.Char(
        string='Search Info',
        compute='_compute_search_info',
        store=False,
        help='Information to help with product search including IDs'
    )

    @api.depends('name', 'default_code', 'product_tmpl_id')
    def _compute_search_info(self):
        for product in self:
            info_parts = []
            if product.default_code:
                info_parts.append(f"Code: {product.default_code}")
            info_parts.append(f"Template ID: {product.product_tmpl_id.id}")
            info_parts.append(f"Variant ID: {product.id}")
            if product.barcode:
                info_parts.append(f"Barcode: {product.barcode}")
            product.search_info = " | ".join(info_parts)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Extended name_search to allow searching products by:
        1. Product template ID (exact match)
        2. Product variant ID (exact match)
        3. Barcode (exact match)
        4. Default code
        5. Product name
        6. Alternative codes (if available)
        """
        args = args or []
        
        if not name:
            return super().name_search(name, args, operator, limit)

        # Check if the search term is numeric (potential ID)
        if name.isdigit():
            product_id = int(name)
            
            # 1. Try to find by product template ID
            products_by_template = self.search([
                ('product_tmpl_id', '=', product_id)
            ] + args, limit=limit)
            
            if products_by_template:
                return products_by_template.name_get()
            
            # 2. Try to find by product variant ID
            products_by_id = self.search([
                ('id', '=', product_id)
            ] + args, limit=limit)
            
            if products_by_id:
                return products_by_id.name_get()

        # 3. Try exact barcode match first (highest priority for non-numeric)
        products = self.search([('barcode', '=', name)] + args, limit=limit)
        if products:
            return products.name_get()

        # 4. Search by alternative codes if the model exists
        if hasattr(self.env['product.template'], 'alternative_codes'):
            matching_products = self.search([
                ('product_tmpl_id.alternative_codes.code', operator, name)
            ] + args, limit=limit)
            
            if matching_products:
                return matching_products.name_get()

        # 5. Fallback to default_code and name search
        matching_products = self.search([
            '|', 
            ('default_code', operator, name), 
            ('name', operator, name)
        ] + args, limit=limit)

        return matching_products.name_get()

    @api.model
    def name_get(self):
        """
        Enhanced name_get to show more information including template ID
        """
        result = []
        for product in self:
            # Include template ID in the display name for easier identification
            name_parts = []
            
            if product.default_code:
                name_parts.append(f"[{product.default_code}]")
            
            name_parts.append(product.name)
            
            # Add template ID at the end for reference
            name_parts.append(f"(T:{product.product_tmpl_id.id})")
            
            name = " ".join(name_parts)
            result.append((product.id, name))
            
        return result


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Campo computado para mostrar información de búsqueda
    template_search_info = fields.Char(
        string='Template Search Info',
        compute='_compute_template_search_info',
        store=False,
        help='Information to help with template search including ID'
    )

    @api.depends('name', 'default_code')
    def _compute_template_search_info(self):
        for template in self:
            info_parts = []
            if template.default_code:
                info_parts.append(f"Code: {template.default_code}")
            info_parts.append(f"Template ID: {template.id}")
            template.template_search_info = " | ".join(info_parts)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Extended name_search for product templates to allow searching by ID
        """
        args = args or []
        
        if not name:
            return super().name_search(name, args, operator, limit)

        # Check if the search term is numeric (potential template ID)
        if name.isdigit():
            template_id = int(name)
            
            # Try to find by template ID
            templates = self.search([
                ('id', '=', template_id)
            ] + args, limit=limit)
            
            if templates:
                return templates.name_get()

        # Search by alternative codes if available
        if hasattr(self, 'alternative_codes'):
            matching_templates = self.search([
                ('alternative_codes.code', operator, name)
            ] + args, limit=limit)

            if matching_templates:
                return matching_templates.name_get()

        # Fallback to default_code and name search
        matching_templates = self.search([
            '|', 
            ('default_code', operator, name), 
            ('name', operator, name)
        ] + args, limit=limit)

        return matching_templates.name_get()

    @api.model
    def name_get(self):
        """
        Enhanced name_get to show template ID for easier identification
        """
        result = []
        for template in self:
            name_parts = []
            
            if template.default_code:
                name_parts.append(f"[{template.default_code}]")
            
            name_parts.append(template.name)
            
            # Add template ID for reference
            name_parts.append(f"(ID:{template.id})")
            
            name = " ".join(name_parts)
            result.append((template.id, name))
            
        return result