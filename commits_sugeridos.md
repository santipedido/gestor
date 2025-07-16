
# ✅ Commits sugeridos por módulo funcional

Usa esta guía para hacer commits limpios y ordenados a medida que vayas integrando funcionalidades.

---

## 1. 🧾 Clientes
Endpoints:
- /clientes
- /clientes/{id}
- /clientes/crear
- /clientes/editar
- /clientes/eliminar

**Commit sugerido:**
```
feat: agregar CRUD de clientes
```

---

## 2. 📦 Productos
Endpoints:
- /productos
- /productos/{id}
- /productos/crear
- /productos/editar
- /productos/eliminar

**Commit sugerido:**
```
feat: agregar CRUD de productos
```

---

## 3. 📑 Pedidos
Endpoints:
- /pedidos
- /pedidos/{id}
- /pedidos/crear
- /pedidos/actualizar
- /pedidos/eliminar

**Commit sugerido:**
```
feat: endpoints para pedidos
```

---

## 4. 🔐 Autenticación y roles
Endpoints:
- /login
- /registro
- /auth/verify

Funcionalidad:
- Middleware para roles (vendedor y superusuario)

**Commit sugerido:**
```
feat: autenticación y control de roles (vendedor y superusuario)
```

---

## 5. 📤 WhatsApp
Endpoints:
- /whatsapp/enviar
- /whatsapp/promocion-masiva

**Commit sugerido:**
```
feat: generación de mensajes de WhatsApp
```

---

## 6. 🧾 PDF / Facturas
Endpoints:
- /facturas/generar

**Commit sugerido:**
```
feat: generación de factura PDF por pedido
```

---

## 7. 📊 Reportes
Endpoints:
- /reportes/por-cliente
- /reportes/top-clientes
- /reportes/pedidos-por-fecha

**Commit sugerido:**
```
feat: agregar reportes básicos
```

---

## 8. 🔧 Configuración inicial
Tareas:
- Conexión a Supabase
- Variables de entorno
- Seeders de prueba

**Commit sugerido:**
```
chore: configuración inicial de entorno y base de datos
```
