/// <reference types="vite/client" />

interface ImportMetaEnv {
  // Base de la API. En dev se usa el proxy ('/api'); en produccion se puede
  // apuntar al backend desplegado (p. ej. https://fitadapt-ai.onrender.com/api).
  readonly VITE_API_BASE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
