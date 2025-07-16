// El contenido ya es ESM, solo se requiere renombrar el archivo a vite.config.mjs
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173
  }
})
