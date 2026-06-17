# FitAdapt AI 🏋️‍♀️🧠

**Sistema inteligente de recomendación de ejercicio que se adapta a la salud de cada persona.**

La idea central: el ejercicio "seguro y efectivo" no es igual para todo el mundo.
Depende de las **condiciones de salud** (SOP, hipotiroidismo, diabetes tipo 2,
enfermedad cardiovascular, osteoporosis, fibromialgia, asma, artrosis…), del
**objetivo** (perder peso / mantener / ganar músculo), del **enfoque muscular** y
del **entorno** disponible (gimnasio, casa, exterior) y su equipamiento.

> ⚕️ **Aviso médico:** este proyecto es educativo y **no sustituye el consejo de un
> profesional sanitario**. Consulta [MEDICAL_DISCLAIMER.md](MEDICAL_DISCLAIMER.md).

---

## ✨ Qué hace ahora mismo (núcleo funcional)

Este repositorio contiene un **backend en Python real y ejecutable**, sin
dependencias externas (solo la librería estándar), con pruebas que pasan:

- **Filtro de seguridad por condición** — descarta ejercicios contraindicados
  (p. ej. nada de alto impacto en osteoporosis o artrosis de rodilla; nada de
  flexión de columna en osteoporosis; nada de isométricos largos en enfermedad
  cardiovascular).
- **Adaptación de intensidad** — calcula el tope de intensidad del día según la
  salud y el contexto (sueño, turnos de noche).
- **Límite de HIIT** — combina objetivo y salud (p. ej. SOP ≤ 3/semana,
  enfermedad cardiovascular = 0).
- **Reparto de volumen** — asigna series por grupo muscular según el enfoque del
  usuario (primario / secundario / mantenimiento).
- **Parámetros por objetivo** — sesiones de cardio/fuerza, rangos de repeticiones
  y descansos según se quiera perder, mantener o ganar.
- **Analítica de progreso** — media móvil, tendencia (ritmo de cambio) y una
  puntuación de progreso **ajustada a la condición** (un avance lento por
  hipotiroidismo no se penaliza).

## 🗂️ Estructura

```
fitadapt-ai/
├── backend/
│   ├── models/      # Condiciones, ejercicios, perfil, objetivo, enfoque muscular
│   ├── engine/      # Filtro por condiciones, intensidad, motor de recomendación
│   ├── analytics/   # Estadística de progreso corporal
│   └── data/        # Catálogo de ejercicios y reglas de condiciones
├── tests/           # Pruebas unitarias (unittest)
├── demo.py          # Demostración por consola
└── requirements.txt
```

## 🚀 Cómo ejecutarlo

Requiere **Python 3.10+**. No hace falta instalar nada.

```bash
# Ver una demostración
python demo.py

# Ejecutar las pruebas
python -m unittest discover -s tests -t . -v
```

## 🧭 Estado y hoja de ruta

Este es el **núcleo del backend** (la parte "inteligente" del sistema). La
especificación completa de FitAdapt AI incluye además módulos que aún **no** están
implementados y se irán añadiendo de forma incremental:

- [ ] Adaptación hormonal por fase del ciclo (SOP, tiroides, menopausia)
- [ ] Optimización por turnos de trabajo y horarios de gimnasio
- [ ] Sustitución de ejercicios entre entornos (gym ↔ casa ↔ exterior)
- [ ] Análisis de fotos de progreso (visión por computador)
- [ ] Gamificación 1v1 con hándicap justo por condición
- [ ] Integración con Google Fit
- [ ] API REST (FastAPI) y frontend (React)

## 📄 Licencia

[MIT](LICENSE)
