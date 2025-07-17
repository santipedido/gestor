# Gestor de Pedidos

Sistema completo de gestión de pedidos con frontend en Vue.js y backend en FastAPI.

## 🌐 Enlaces de Producción

- **Frontend**: https://pedidosq.netlify.app/
- **Backend**: https://web-6o0qnvuq257-de-fra1-k8s-1pps.run-on-seenode.com

## 🚀 Despliegue Automático

### Frontend (Netlify)
- **Repositorio**: Conectado a GitHub
- **Deploy**: Automático con cada `git push`
- **Variables de entorno**: Configuradas en Netlify

### Backend (Seeno)
- **Repositorio**: Conectado a GitHub
- **Deploy**: Automático con cada `git push`
- **CORS**: Configurado para permitir peticiones desde Netlify

## 🛠️ Desarrollo

### Flujo de trabajo recomendado:
1. **Edita el código** en tu editor2*Haz commit y push** a GitHub
3**Prueba automáticamente** en producción4*No necesitas servidores locales**

### Comandos útiles:
```bash
# Ver estado del repositorio
git status

# Hacer cambios y desplegar
git add .
git commit -m "Descripción de cambios"
git push origin main
```

## 📁 Estructura del Proyecto

```
gestor_pedidos/
├── backend/          # API FastAPI (Seeno)
├── frontend/         # Vue.js (Netlify)
└── README.md
```

## 🔧 Configuración

### Variables de entorno (Netlify):
- `VITE_API_URL`: URL del backend en Seeno

### CORS (Backend):
- Permite peticiones desde: https://pedidosq.netlify.app/
