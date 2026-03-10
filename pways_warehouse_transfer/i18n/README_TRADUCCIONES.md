# Traducciones del Módulo pways_warehouse_transfer

Este módulo ha sido extendido con soporte completo para traducciones al español.

## Archivos de Traducción Añadidos

- `i18n/es.po` - Traducción general al español
- `i18n/es_ES.po` - Traducción específica para España
- `i18n/pways_warehouse_transfer.pot` - Plantilla de traducción

## Elementos Traducidos

### Modelo stock.transfer
- **Warehouse Stock Transfer** → **Transferencia de Stock de Almacén**
- **State** → **Estado**
- **Type** → **Tipo**
- **From** → **Desde**
- **To** → **Hacia**
- **Schedule Date** → **Fecha Programada**
- **Requested from** → **Solicitado desde**
- **To** (campo to_warehouse_id) → **Hacia**

### Estados del Proceso
- **Draft** → **Borrador**
- **Processing** → **Procesando**
- **Done** → **Completado**

### Tipos de Transferencia
- **Send** → **Enviar**
- **Receive** → **Recibir**

### Modelo stock.transfer.line
- **Warehouse Stock Transfer Line** → **Línea de Transferencia de Stock de Almacén**
- **Product** → **Producto**
- **Quantity** → **Cantidad**
- **Unit of Measure** → **Unidad de Medida**

### Elementos de Interfaz
- **Stock Transfer** → **Transferencia de Stock**
- **Process** → **Procesar**
- **Pickings** → **Albaranes**
- **Operations** → **Operaciones**
- **Requested From** → **Solicitado Desde**

### Menús y Acciones
- **Warehouse Transfer** → **Transferencia de Almacén**

### Mensajes del Sistema
- **Please add items to transfer.** → **Por favor añada artículos para transferir.**
- **Stock Picking** → **Albarán de Stock**
- **Create a new New Transfer** → **Crear una nueva Transferencia**

### Datos Maestros
- **warehouse.transfer** → **transferencia.almacén**
- **Warehouse Transfer** (ubicación) → **Transferencia de Almacén**

### Permisos de Acceso
- **access_stock_transfer** → **acceso_transferencia_stock**
- **access_stock_transfer_line** → **acceso_línea_transferencia_stock**

## Notas Técnicas

- Los archivos Python ya tenían la importación `_` correcta para traducciones
- El funcionamiento del módulo se mantiene intacto
- Las traducciones se cargan automáticamente según el idioma del usuario
- Los archivos .po pueden ser editados para personalizar las traducciones

## Funcionalidades del Módulo

Este módulo permite:
- Transferencias internas de productos entre almacenes
- Dos tipos de operación: Envío y Recepción
- Gestión de ubicaciones de origen y destino
- Seguimiento de estados (Borrador → Procesando → Completado)
- Integración con el sistema de albaranes de Odoo
- Ubicación de tránsito temporal para las transferencias

## Instalación

Después de actualizar el módulo, las traducciones estarán disponibles automáticamente para los usuarios que tengan el español configurado como idioma.
