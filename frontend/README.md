# FitAdapt AI — Frontend (React + Vite + TypeScript)

Interfaz web que consume la API del backend y muestra una recomendación de
ejercicio adaptada: el usuario elige condiciones de salud, objetivo, músculos
prioritarios, entornos y equipamiento, y recibe su plan.

## Requisitos
- Node 18+ y npm

## Puesta en marcha (desarrollo)

Necesitas el **backend en marcha** en otra terminal:

```bash
# En la raíz del repo
python -m backend.api.app        # API en http://127.0.0.1:8000
```

Y el frontend:

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

En desarrollo, Vite redirige automáticamente las llamadas a `/api` hacia el
backend (ver `vite.config.ts`), así que no hay problemas de CORS.

> Si tu red intercepta HTTPS y `npm install` falla con
> `UNABLE_TO_VERIFY_LEAF_SIGNATURE`, instala el certificado raíz de tu red, o
> como solución puntual: `npm install --strict-ssl=false`.

## Build de producción

```bash
npm run build      # genera dist/ (type-check con tsc + bundle con Vite)
npm run preview    # sirve el build
```

## Estructura

```
frontend/
├── index.html
├── vite.config.ts          # incluye el proxy /api -> backend
└── src/
    ├── main.tsx
    ├── App.tsx             # formulario + estado
    ├── api.ts             # cliente de la API y tipos
    ├── constants.ts       # opciones del formulario
    ├── styles.css
    └── components/
        └── RecommendationView.tsx
```
