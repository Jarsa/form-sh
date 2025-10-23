# GUÍA PARA VERIFICAR PERMISOS EN ODOO

## 🔍 Dónde verificar permisos en la interfaz de Odoo:

### 1. **Grupos de Usuarios** (Recomendado)
- Ve a: **Configuración > Usuarios y Empresas > Grupos**
- Busca: "Sale Request" 
- Verifica que todos los usuarios estén en el grupo "Sale Request User"

### 2. **Usuarios Individuales**
- Ve a: **Configuración > Usuarios y Empresas > Usuarios**
- Haz clic en cualquier usuario
- Ve a la pestaña **"Derechos de Acceso"**
- Busca la sección **"Sale Request"** 
- Asegúrate que tenga marcado "User"

### 3. **Reglas de Registro (Avanzado)**
- Ve a: **Configuración > Técnico > Seguridad > Reglas de Registro**
- Busca: "Sale Request"
- Deberías ver solo la regla "Sale Request All Users Access"

### 4. **Acceso a Modelos (Avanzado)**
- Ve a: **Configuración > Técnico > Seguridad > Listas de Control de Acceso**
- Busca: "sale.request"
- Verifica que aparezcan las líneas con "base.group_user"

### 5. **Verificar el Menú**
- Ve al menú principal de **Ventas**
- Busca el submenú **"Sale Request"**
- Si no aparece, el usuario no tiene permisos

## 🚨 Si siguen apareciendo alertas:

### Opción 1: Forzar actualización de permisos
1. Ve a **Configuración > Técnico > Base de Datos > Estructura > Modelos**
2. Busca "sale.request"
3. Haz clic en "Actualizar Lista de Modelos"
4. Ve a **Aplicaciones** y busca "Sale Request"
5. Haz clic en "Actualizar"

### Opción 2: Desde terminal/shell de Odoo
```python
# Ejecutar en el shell de Odoo
env['res.groups'].search([('name', 'like', 'Sale Request')]).write({
    'users': [(4, user.id) for user in env['res.users'].search([('active', '=', True)])]
})
```

### Opción 3: SQL directo (¡Cuidado!)
```sql
-- Solo si eres admin de base de datos
INSERT INTO res_groups_users_rel (gid, uid) 
SELECT g.id, u.id 
FROM res_groups g, res_users u 
WHERE g.name LIKE '%Sale Request%' 
AND u.active = true
ON CONFLICT DO NOTHING;
```

## 📋 Checklist de verificación:

- [ ] Todos los usuarios están en grupo "Sale Request User"
- [ ] El menú "Sale Request" aparece en Ventas
- [ ] Los usuarios pueden crear nuevos Sale Requests
- [ ] Los usuarios pueden ver todos los Sale Requests
- [ ] No aparecen mensajes de "Acceso denegado"

## 🔧 Lo que hice en el código:

1. **Eliminé reglas restrictivas** que limitaban acceso por usuario
2. **Dejé solo una regla permisiva** que da acceso completo a todos los usuarios
3. **Agregué código para añadir automáticamente** todos los usuarios a los grupos necesarios
4. **Simplifiqué el sistema de permisos** para evitar conflictos

## ⚡ Si NADA funciona:

Como última opción, podemos **desactivar completamente la seguridad** comentando todas las reglas en `sale_request_security.xml`, pero esto NO es recomendado en producción.