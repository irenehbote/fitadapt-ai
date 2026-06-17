import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo, las llamadas a /api se redirigen al backend en el puerto 8000.
// Asi el frontend no necesita preocuparse de CORS ni de la URL del backend.
export default defineConfig({
  // En GitHub Pages el sitio cuelga de /fitadapt-ai/; en Render/local, de la raiz.
  // Se controla con la variable VITE_BASE (por defecto '/').
  base: process.env.VITE_BASE || '/',
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
