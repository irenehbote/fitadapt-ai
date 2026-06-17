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

**69 pruebas unitarias, todas pasan.** Sin dependencias externas.

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
- **API REST** — `/health`, `/conditions`, `/exercises`, `POST /recommendations`.

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
│   └── data/          # Catálogo de ejercicios y reglas de condiciones
├── tests/             # 69 pruebas unitarias (unittest)
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
- [x] API REST

Pendiente (requiere servicios/ML externos o un frontend completo):

- [ ] Estimación de composición corporal por **foto** (visión por computador)
- [ ] Conexión **OAuth real** con Google Fit
- [ ] **Frontend** (React)
- [ ] Persistencia en base de datos

## 📄 Licencia

[MIT](LICENSE)
