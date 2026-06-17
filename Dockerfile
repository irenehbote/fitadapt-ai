# --- Etapa 1: compilar el frontend ---
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# base '/' y VITE_API_BASE '/api' (mismo origen que el backend).
RUN npm run build

# --- Etapa 2: backend Python que sirve API + frontend ---
FROM python:3.12-slim
WORKDIR /app
# El backend solo usa la libreria estandar: no hay dependencias que instalar.
COPY backend/ ./backend/
COPY --from=frontend /app/frontend/dist ./static
ENV FITADAPT_STATIC=/app/static
ENV PORT=8000
EXPOSE 8000
CMD ["python", "-m", "backend.api.app"]
