# gestor_pedidos

## Flujo de trabajo profesional con ramas

- **main**: Rama para desarrollo y pruebas locales. Aquí puedes hacer cambios, pruebas y ajustes sin preocuparte por el entorno de producción.
- **deploy/seeno**: Rama exclusiva para producción y deploy en Seeno. Solo fusiona aquí lo que esté listo para desplegar.

### ¿Cómo trabajar?

1. Trabaja y prueba localmente en la rama `main`.
2. Cuando una funcionalidad esté lista para producción:
   - Cambia a la rama de deploy:
     ```bash
     git checkout deploy/seeno
     ```
   - Fusiona los cambios de `main`:
```bash
     git merge main
     ```
   - Ajusta archivos de configuración para producción si es necesario (Procfile, variables de entorno, etc.).
   - Haz commit y push:
```bash
     git add .
     git commit -m "deploy: actualizar para producción"
     git push origin deploy/seeno
     ```
3. Realiza el deploy desde Seeno usando la rama `deploy/seeno`.

**Nota:** Nunca subas archivos sensibles como `.env` al repositorio. Configura las variables de entorno desde el panel de Seeno.
