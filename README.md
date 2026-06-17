# FitAdapt AI 🏋️‍♀️🧠

**Sistema inteligente de recomendación de ejercicio que se adapta a la salud de cada persona.**

La idea central: el ejercicio "seguro y efectivo" no es igual para todo el mundo.
Depende de las **condiciones de salud** (SOP, hipotiroidismo, diabetes tipo 2,
enfermedad cardiovascular, osteoporosis, fibromialgia, asma, artrosis…), del
**objetivo** (perder peso / mantener / ganar músculo), del **enfoque muscular**, de
la **fase del ciclo hormonal**, de los **turnos de trabajo** y del **entorno**
disponible (gimnasio, casa, exterior) y su equipamiento.

> ⚕️ **Aviso médico:** este proyecto es educativo y **no sustituye el consejo de un
> profesional sanitario**. Consulta [MEDICAL_DISCLAIMER.md](MEDICAL_DISCLAIMER.md).

---

## ✨ Qué hace (backend real y ejecutable, solo librería estándar)

**88 pruebas unitarias, todas pasan.** Sin dependencias externas.

- **Filtro de seguridad por condición** — descarta ejercicios contraindicados
  (sin alto impacto en osteoporosis/artrosis; sin flexión de columna en
  osteoporosis; sin isométricos largos en enfermedad cardiovascular…).
- **Adaptación de intensidad** — tope del día según salud y contexto (dormir
  poco, turnos de noche).
- **Adaptación hormonal** — calcula la fase del ciclo y ajusta la intensidad
  (regla especial del SOP en fase lútea).
- **Turnos y horarios** — puntuación de fatiga, tope de intensidad por fatiga,
  disponibilidad del gimnasio por franja y mejor ventana tras despertar.
- **Sustitución entre entornos** — si un ejercicio no es viable en casa/exterior,
  busca la mejor alternativa segura y disponible.
- **Límite de HIIT y volumen** — combina objetivo y salud; reparte series por
  músculo según el enfoque.
- **Analítica de progreso** — media móvil, tendencia y puntuación ajustada a la
  condición; informe de progreso entre medidas con aviso de cambios poco plausibles.
- **Gamificación 1v1 opcional** — XP con hándicap justo por condición y retos
  que solo cuentan si se aceptan.
- **Influencia de Google Fit** — sueño, pasos y FC en reposo ajustan el plan.
- **API REST** — recomendación y endpoints para todos los módulos.
- **Persistencia (SQLite)** — guarda perfiles y su histórico de medidas; calcula
  recomendación y progreso de perfiles almacenados.
- **Composición corporal** — % de grasa por **fórmula Navy** (circunferencias) o
  por IMC; y un pipeline **experimental por foto** (MediaPipe, opcional).
- **Frontend React** — interfaz con pestañas que usa **todos** los módulos.

> 🔍 **Fronteras honestas:** la estimación de grasa por **foto** (visión por
> computador) y la **conexión OAuth real** con Google Fit quedan como puntos de
> integración marcados (lanzan `NotImplementedError`): no se inventan datos ni se
> simula la red.

## 🗂️ Estructura

```
fitadapt-ai/
├── backend/
│   ├── models/        # Condiciones, ejercicios, perfil, objetivo, enfoque muscular
│   ├── engine/        # Filtro, intensidad, hormonal, entornos, recomendación
│   ├── scheduling/    # Turnos, horarios de gym y fatiga
│   ├── gamification/  # Puntuación justa y retos 1v1
│   ├── integrations/  # Google Fit (influencia + cliente OAuth pendiente)
│   ├── analytics/     # Estadística y informe de progreso corporal
│   ├── api/           # API REST (http.server)
│   ├── database/      # Persistencia SQLite (perfiles y medidas)
│   └── data/          # Catálogo de ejercicios y reglas de condiciones
├── frontend/          # App React + Vite + TypeScript (ver frontend/README.md)
├── tests/             # 88 pruebas unitarias (unittest)
└── demo.py            # Demostración por consola
```

## 🚀 Cómo ejecutarlo

Requiere **Python 3.10+**. No hace falta instalar nada.

```bash
# Demostración por consola
python demo.py

# Arrancar la API REST (http://127.0.0.1:8000)
python -m backend.api.app

# Ejemplo de petición
curl -X POST http://127.0.0.1:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"name":"Ana","goal":"lose","conditions":["pcos"],
       "muscle_focus":{"primary":["glutes"]},"environments":["home"],
       "equipment":["dumbbell","mat"]}'

# Pruebas
python -m unittest discover -s tests -t . -v
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 (necesita la API en marcha)
```
Más detalles en [frontend/README.md](frontend/README.md).

### Estimación por foto (opcional, experimental)

La fórmula Navy (por medidas) funciona sin nada extra. La estimación **por foto**
necesita dependencias adicionales y descargar un modelo:

```bash
pip install -r requirements-vision.txt
python -m backend.vision.download_model        # --insecure si tu red intercepta TLS
```
Es una estimación **orientativa** (~±5-8%), no una medición. Si no instalas esto,
el endpoint `POST /body-fat/photo` responde `501` con instrucciones; el resto del
proyecto sigue funcionando igual.

## 🧭 Hoja de ruta

Implementado ✅:

- [x] Filtrado de seguridad por condición de salud
- [x] Adaptación de intensidad por salud y contexto
- [x] Adaptación hormonal por fase del ciclo
- [x] Optimización por turnos de trabajo y horarios de gimnasio
- [x] Sustitución de ejercicios entre entornos
- [x] Analítica e informe de progreso corporal
- [x] Gamificación 1v1 con hándicap justo
- [x] Lógica de influencia de Google Fit
- [x] API REST (con endpoints para todos los módulos)
- [x] Frontend (React + Vite + TypeScript) conectado a todos los módulos
- [x] Persistencia en base de datos (SQLite)

- [x] Composición corporal: fórmula Navy/IMC + estimación **por foto** (experimental, opcional)

Pendiente (requiere servicios/ML externos):

- [ ] Conexión **OAuth real** con Google Fit
- [ ] Validar la precisión del pipeline de foto contra un método de referencia

## 📄 Licencia

[MIT](LICENSE)
