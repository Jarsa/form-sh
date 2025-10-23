# Sale Request Product Search Enhancement

## Funcionalidad Agregada

Este módulo extiende la funcionalidad de búsqueda de productos en las líneas de cotizaciones y pedidos de venta para permitir buscar por:

### 1. ID de Product Template
- Puedes escribir directamente el ID numérico del template (ej: "123") 
- El sistema buscará todos los productos que pertenezcan a ese template

### 2. ID de Product Variant  
- Puedes escribir el ID específico de la variante del producto
- Útil cuando conoces el ID exacto del producto

### 3. Código de Barras
- Búsqueda exacta por código de barras del producto
- Tiene alta prioridad en la búsqueda

### 4. Códigos Alternativos
- Si tienes configurados códigos alternativos en el modelo `product.alternative.code`
- Busca automáticamente en estos códigos

### 5. Código por Defecto y Nombre
- Funcionalidad estándar de Odoo mejorada
- Búsqueda en default_code y nombre del producto

## Información Adicional Mostrada

### En name_get():
- **Product.product**: `[CODE] Product Name (T:123)` donde T:123 es el Template ID
- **Product.template**: `[CODE] Product Name (ID:123)` donde ID:123 es el Template ID

### Campos Computados:
- **search_info**: Información completa para búsqueda (Code, Template ID, Variant ID, Barcode)
- **template_search_info**: Información de búsqueda para templates

## Ejemplos de Uso

1. **Buscar por Template ID**: Escribe "123" para encontrar todos los productos del template 123
2. **Buscar por código**: Escribe "PROD001" para buscar por código por defecto
3. **Buscar por nombre**: Escribe "Producto" para buscar en nombres
4. **Buscar por barcode**: Escribe el código de barras exacto

## Archivos Modificados

- `models/product_product.py`: Lógica de búsqueda extendida
- `views/product_search_view.xml`: Vistas mejoradas para mostrar información de búsqueda
- `models/__init__.py`: Inclusión del nuevo modelo

## Compatibilidad

- Compatible con el módulo de códigos alternativos si está instalado
- Retrocompatible con funcionalidad estándar de Odoo
- Funciona en cotizaciones, pedidos de venta y requisiciones