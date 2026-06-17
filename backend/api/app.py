"""API REST de FitAdapt AI.

Se implementa con la libreria estandar (`http.server`) para que el proyecto
siga funcionando sin instalar nada. La lógica de enrutado vive en `route()`,
una funcion pura y facil de testear sin abrir sockets.

Endpoints sin estado (no necesitan base de datos):
    GET  /health
    GET  /conditions
    GET  /exercises
    POST /recommendations      -> recomendacion semanal para un perfil (JSON)
    POST /hormonal             -> adaptacion por fase del ciclo
    POST /fatigue              -> fatiga y tope de intensidad
    POST /google-fit           -> ajustes segun datos de Google Fit
    POST /xp                   -> XP de un ejercicio (handicap por condicion)
    POST /substitute           -> alternativa de un ejercicio segun entorno
    POST /progress             -> informe de progreso entre dos medidas

Endpoints con persistencia (necesitan base de datos):
    POST   /profiles
    GET    /profiles
    GET    /profiles/{id}
    DELETE /profiles/{id}
    GET    /profiles/{id}/recommendation
    POST   /profiles/{id}/measurements
    GET    /profiles/{id}/progress
"""
from __future__ import annotations

import json
import mimetypes
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Tuple

from ..analytics.body_composition import estimate_body_fat
from ..analytics.photo_progress import (MeasurementSnapshot,
                                        generate_progress_report)
from ..data.condition_rules import CONDITIONS, get_condition, get_conditions
from ..data.exercises import EXERCISES, EXERCISES_BY_ID
from ..database.db import DEFAULT_DB, connect, init_db
from ..database.measurement_repository import MeasurementRepository
from ..database.profile_repository import ProfileRepository
from ..engine.condition_filter import is_safe
from ..engine.environment_adapter import substitute_exercise
from ..engine.hormonal_adapter import (hormonal_intensity_factor,
                                       hormonal_notes, phase_for_day)
from ..engine.intensity_adapter import WorkoutContext, max_allowed_intensity
from ..engine.recommendation_engine import generate_recommendations
from ..gamification.fair_scoring import exercise_xp
from ..integrations.google_fit import HealthData, recommend_adjustments
from ..models.body_goal import BodyGoal
from ..models.muscle_focus import MuscleFocus
from ..models.user_profile import UserProfile
from ..scheduling.shift_optimizer import (fatigue_adjusted_intensity_cap,
                                          fatigue_score, is_high_fatigue)


# ---------------------------------------------------------------------------
# Construccion y serializacion de objetos de dominio
# ---------------------------------------------------------------------------

def build_profile_from_dict(payload: dict) -> UserProfile:
    """Crea un UserProfile a partir de un cuerpo JSON. Lanza ValueError si algo falla."""
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    try:
        condiciones = get_conditions(payload.get("conditions", []))
    except KeyError as e:
        raise ValueError(f"Condicion desconocida: {e}")
    objetivo_raw = payload.get("goal", "maintain")
    try:
        objetivo = BodyGoal(objetivo_raw)
    except ValueError:
        raise ValueError(f"Objetivo desconocido: {objetivo_raw}")
    foco = payload.get("muscle_focus", {})
    muscle_focus = MuscleFocus.from_primary(
        foco.get("primary", []), foco.get("secondary", []))
    return UserProfile(
        name=payload.get("name", "Anonimo"),
        age=int(payload.get("age", 30)),
        conditions=condiciones,
        goal=objetivo,
        muscle_focus=muscle_focus,
        available_environments=payload.get("environments", ["home"]),
        available_equipment=payload.get("equipment", ["none"]),
    )


def serialize_recommendation(rec) -> dict:
    """Convierte una Recommendation en un diccionario JSON-serializable."""
    return {
        "cardio_sessions_per_week": list(rec.cardio_sessions_per_week),
        "strength_sessions_per_week": list(rec.strength_sessions_per_week),
        "weekly_hiit_limit": rec.weekly_hiit_limit,
        "max_intensity_today": rec.max_intensity_today,
        "safe_exercise_count": len(rec.safe_exercises),
        "safe_exercises": [e.id for e in rec.safe_exercises],
        "volume_allocation": rec.volume_allocation,
        "notes": rec.notes,
    }


def serialize_profile(profile: UserProfile, profile_id: int) -> dict:
    """Serializa un perfil (incluyendo su id de base de datos)."""
    return {
        "id": profile_id,
        "name": profile.name,
        "age": profile.age,
        "goal": profile.goal.value,
        "conditions": profile.condition_keys(),
        "muscle_levels": profile.muscle_focus.levels(),
        "environments": profile.available_environments,
        "equipment": profile.available_equipment,
    }


# ---------------------------------------------------------------------------
# Contexto con repositorios (persistencia)
# ---------------------------------------------------------------------------

@dataclass
class ApiContext:
    """Agrupa los repositorios que necesitan los endpoints con persistencia."""

    profiles: ProfileRepository
    measurements: MeasurementRepository


def make_context(conn) -> ApiContext:
    """Crea un contexto de API a partir de una conexion a la base de datos."""
    return ApiContext(ProfileRepository(conn), MeasurementRepository(conn))


# ---------------------------------------------------------------------------
# Handlers de los endpoints sin estado (por modulo)
# ---------------------------------------------------------------------------

def _recommendations(body: dict) -> Tuple[int, dict]:
    try:
        perfil = build_profile_from_dict(body)
    except ValueError as e:
        return 400, {"error": str(e)}
    return 200, serialize_recommendation(generate_recommendations(perfil))


def _hormonal(body: dict) -> Tuple[int, dict]:
    try:
        condiciones = get_conditions(body.get("conditions", []))
        perfil = UserProfile(name="x", age=30, conditions=condiciones)
        dia = int(body["cycle_day"])
        longitud = int(body.get("cycle_length", 28))
        fase = phase_for_day(dia, longitud)
        return 200, {
            "phase": fase.value,
            "intensity_factor": hormonal_intensity_factor(perfil, dia, longitud),
            "notes": hormonal_notes(perfil, dia, longitud),
        }
    except (KeyError, ValueError) as e:
        return 400, {"error": str(e)}


def _fatigue(body: dict) -> Tuple[int, dict]:
    try:
        score = fatigue_score(
            consecutive_work_days=int(body.get("consecutive_work_days", 0)),
            night_shifts_this_week=int(body.get("night_shifts_this_week", 0)),
            hours_slept_last_night=float(body.get("hours_slept_last_night", 8)),
            stress_level=int(body.get("stress_level", 1)),
        )
    except (TypeError, ValueError) as e:
        return 400, {"error": str(e)}
    return 200, {
        "score": score,
        "high_fatigue": is_high_fatigue(score),
        "intensity_cap": fatigue_adjusted_intensity_cap(score),
    }


def _google_fit(body: dict) -> Tuple[int, dict]:
    data = HealthData(
        steps_today=body.get("steps_today"),
        sleep_hours_last_night=body.get("sleep_hours_last_night"),
        resting_hr_trend=body.get("resting_hr_trend"),
    )
    adj = recommend_adjustments(data)
    return 200, {
        "intensity_cap": adj.intensity_cap,
        "reduce_cardio": adj.reduce_cardio,
        "suggest_deload": adj.suggest_deload,
        "notes": adj.notes,
    }


def _xp(body: dict) -> Tuple[int, dict]:
    ejercicio = EXERCISES_BY_ID.get(body.get("exercise_id", ""))
    if ejercicio is None:
        return 400, {"error": "exercise_id desconocido"}
    try:
        perfil = UserProfile(name="x", age=30,
                             conditions=get_conditions(body.get("conditions", [])))
        xp = exercise_xp(ejercicio, intensity=int(body.get("intensity", 5)),
                         streak_days=int(body.get("streak_days", 0)), profile=perfil)
    except (KeyError, ValueError) as e:
        return 400, {"error": str(e)}
    return 200, {"exercise": ejercicio.name, "xp": xp}


def _substitute(body: dict) -> Tuple[int, dict]:
    ejercicio = EXERCISES_BY_ID.get(body.get("exercise_id", ""))
    if ejercicio is None:
        return 400, {"error": "exercise_id desconocido"}
    try:
        perfil = build_profile_from_dict(body)
    except ValueError as e:
        return 400, {"error": str(e)}
    sub = substitute_exercise(ejercicio, perfil)
    return 200, {
        "original": {"id": ejercicio.id, "name": ejercicio.name,
                     "available": is_safe(ejercicio, perfil)},
        "resolved": None if sub is None else {"id": sub.id, "name": sub.name},
        "changed": sub is not None and sub.id != ejercicio.id,
    }


def _opt_float(value):
    """Convierte a float si hay valor; None en caso contrario."""
    return None if value is None else float(value)


def _body_fat(body: dict) -> Tuple[int, dict]:
    try:
        est = estimate_body_fat(
            sex=body.get("sex", "male"),
            height_cm=float(body["height_cm"]),
            neck_cm=_opt_float(body.get("neck_cm")),
            waist_cm=_opt_float(body.get("waist_cm")),
            hip_cm=_opt_float(body.get("hip_cm")),
            weight_kg=_opt_float(body.get("weight_kg")),
            age=None if body.get("age") is None else int(body["age"]),
        )
    except (KeyError, ValueError, TypeError) as e:
        return 400, {"error": str(e)}
    return 200, {
        "body_fat_pct": est.body_fat_pct,
        "method": est.method,
        "category": est.category,
        "confidence_note": est.confidence_note,
    }


def _body_fat_photo(body: dict) -> Tuple[int, dict]:
    import base64
    from ..vision import body_measure
    if not body_measure.is_available():
        return 501, {"error": "Modulo de vision no instalado "
                              "(pip install -r requirements-vision.txt)"}
    if not body_measure.model_available():
        return 501, {"error": "Modelo no descargado "
                              "(python -m backend.vision.download_model)"}
    try:
        front = base64.b64decode(body["front_image_b64"])
        side = base64.b64decode(body["side_image_b64"])
        height_cm = float(body["height_cm"])
        sex = body.get("sex", "male")
        result = body_measure.estimate_body_fat_from_photos(front, side, height_cm, sex)
    except KeyError as e:
        return 400, {"error": f"Falta el campo {e}"}
    except body_measure.NoPersonDetectedError as e:
        return 422, {"error": str(e)}
    except (ValueError, TypeError) as e:
        return 400, {"error": str(e)}
    return 200, result


def _measurement_from_dict(d: dict) -> MeasurementSnapshot:
    return MeasurementSnapshot(
        label=d.get("label", "medida"),
        weight_kg=float(d["weight_kg"]),
        waist_cm=float(d["waist_cm"]),
        body_fat_pct=d.get("body_fat_pct"),
    )


def serialize_progress(report) -> dict:
    return {
        "days_between": report.days_between,
        "weight_change_pct": report.weight_change_pct,
        "waist_change_cm": report.waist_change_cm,
        "body_fat_change": report.body_fat_change,
        "progress_score": report.progress_score,
        "weekly_weight_change_kg": report.weekly_weight_change_kg,
        "plausible": report.plausible,
        "commentary": report.commentary,
    }


def _progress(body: dict) -> Tuple[int, dict]:
    try:
        antes = _measurement_from_dict(body["before"])
        despues = _measurement_from_dict(body["after"])
        dias = int(body["days_between"])
        condicion = None
        if body.get("condition"):
            condicion = get_condition(body["condition"])
        report = generate_progress_report(antes, despues, dias, condicion)
    except (KeyError, ValueError) as e:
        return 400, {"error": str(e)}
    return 200, serialize_progress(report)


# ---------------------------------------------------------------------------
# Handlers de los endpoints con persistencia (/profiles)
# ---------------------------------------------------------------------------

def _profiles_route(method: str, segs: list, body: Optional[dict],
                    ctx: ApiContext) -> Tuple[int, dict]:
    # /profiles
    if len(segs) == 1:
        if method == "POST":
            try:
                perfil = build_profile_from_dict(body or {})
            except ValueError as e:
                return 400, {"error": str(e)}
            pid = ctx.profiles.create(perfil)
            return 201, {"id": pid}
        if method == "GET":
            return 200, {"profiles": ctx.profiles.list_all()}
        return 405, {"error": "Metodo no permitido"}

    # /profiles/{id}[/...]
    try:
        pid = int(segs[1])
    except ValueError:
        return 404, {"error": "id de perfil invalido"}

    perfil = ctx.profiles.get(pid)
    if perfil is None:
        return 404, {"error": "perfil no encontrado"}

    if len(segs) == 2:
        if method == "GET":
            return 200, serialize_profile(perfil, pid)
        if method == "DELETE":
            ctx.profiles.delete(pid)
            return 200, {"deleted": True}
        return 405, {"error": "Metodo no permitido"}

    accion = segs[2]
    if accion == "recommendation" and method == "GET":
        return 200, serialize_recommendation(generate_recommendations(perfil))

    if accion == "measurements" and method == "POST":
        try:
            snapshot = _measurement_from_dict(body or {})
            dia = int((body or {}).get("day_index", 0))
        except (KeyError, ValueError) as e:
            return 400, {"error": str(e)}
        mid = ctx.measurements.add(pid, snapshot, dia)
        return 201, {"id": mid}

    if accion == "progress" and method == "GET":
        historico = ctx.measurements.list_for(pid)
        if len(historico) < 2:
            return 400, {"error": "Se necesitan al menos 2 medidas"}
        primero, ultimo = historico[0], historico[-1]
        dias = ultimo["day_index"] - primero["day_index"]
        if dias <= 0:
            return 400, {"error": "Las medidas deben estar separadas en el tiempo"}
        condicion = perfil.conditions[0] if perfil.conditions else None
        report = generate_progress_report(
            primero["snapshot"], ultimo["snapshot"], dias, condicion)
        return 200, serialize_progress(report)

    return 404, {"error": "Ruta no encontrada"}


# ---------------------------------------------------------------------------
# Enrutado principal
# ---------------------------------------------------------------------------

def route(method: str, path: str, body: Optional[dict] = None,
          ctx: Optional[ApiContext] = None) -> Tuple[int, dict]:
    """Resuelve una peticion y devuelve (codigo_http, cuerpo_json)."""
    segs = [s for s in path.split("/") if s]

    if method == "GET" and path == "/health":
        return 200, {"status": "ok"}
    if method == "GET" and path == "/conditions":
        return 200, {"conditions": [{"key": c.key, "name": c.name}
                                    for c in CONDITIONS.values()]}
    if method == "GET" and path == "/exercises":
        return 200, {"exercises": [{"id": e.id, "name": e.name,
                                    "environments": e.environments}
                                   for e in EXERCISES]}

    if method == "POST":
        handlers = {
            "/recommendations": _recommendations,
            "/hormonal": _hormonal,
            "/fatigue": _fatigue,
            "/google-fit": _google_fit,
            "/xp": _xp,
            "/substitute": _substitute,
            "/progress": _progress,
            "/body-fat": _body_fat,
            "/body-fat/photo": _body_fat_photo,
        }
        if path in handlers:
            return handlers[path](body or {})

    if segs and segs[0] == "profiles":
        if ctx is None:
            return 503, {"error": "Persistencia no disponible"}
        return _profiles_route(method, segs, body, ctx)

    return 404, {"error": "Ruta no encontrada"}


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------

_CONTEXT: Optional[ApiContext] = None  # se inicializa en run()


def _strip_api_prefix(path: str) -> str:
    """Quita el prefijo /api si esta presente (para servir API y estaticos juntos)."""
    if path == "/api":
        return "/"
    if path.startswith("/api/"):
        return path[4:]
    return path


def _static_dir() -> Optional[str]:
    """Carpeta de ficheros estaticos del frontend, si esta configurada y existe."""
    base = os.environ.get("FITADAPT_STATIC")
    return base if base and os.path.isdir(base) else None


class _Handler(BaseHTTPRequestHandler):
    """Adaptador HTTP: lee la peticion, llama a route() y escribe la respuesta."""

    def _responder(self, status: int, payload: dict) -> None:
        cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_OPTIONS(self):  # noqa: N802 (preflight CORS)
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _serve_static(self, raw_path: str) -> None:
        """Sirve un fichero del frontend; si no existe, devuelve index.html (SPA)."""
        base = _static_dir()
        if base is None:
            self._responder(404, {"error": "Ruta no encontrada"})
            return
        rel = raw_path.split("?", 1)[0].lstrip("/") or "index.html"
        candidate = os.path.normpath(os.path.join(base, rel))
        # Proteccion contra path traversal: no salir de la carpeta base.
        if not candidate.startswith(os.path.normpath(base)) or not os.path.isfile(candidate):
            candidate = os.path.join(base, "index.html")
        if not os.path.isfile(candidate):
            self._responder(404, {"error": "Ruta no encontrada"})
            return
        ctype = mimetypes.guess_type(candidate)[0] or "application/octet-stream"
        with open(candidate, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        explicit_api = self.path == "/api" or self.path.startswith("/api/")
        status, body = route("GET", _strip_api_prefix(self.path), ctx=_CONTEXT)
        # Si no es una ruta de API conocida, intentamos servir el frontend.
        if status == 404 and not explicit_api and _static_dir() is not None:
            self._serve_static(self.path)
            return
        self._responder(status, body)

    def do_DELETE(self):  # noqa: N802
        self._responder(*route("DELETE", _strip_api_prefix(self.path), ctx=_CONTEXT))

    def do_POST(self):  # noqa: N802
        longitud = int(self.headers.get("Content-Length", 0))
        crudo = self.rfile.read(longitud) if longitud else b"{}"
        try:
            body = json.loads(crudo.decode("utf-8"))
        except json.JSONDecodeError:
            self._responder(400, {"error": "JSON invalido"})
            return
        self._responder(*route("POST", _strip_api_prefix(self.path), body, ctx=_CONTEXT))

    def log_message(self, *args):  # silencia el log por defecto
        pass


def run(port: Optional[int] = None, db_path: Optional[str] = None) -> None:
    """Arranca el servidor HTTP con persistencia en SQLite (Ctrl+C para parar).

    En despliegue lee el puerto de la variable PORT y escucha en 0.0.0.0. Si
    FITADAPT_STATIC apunta a una carpeta, sirve ademas el frontend compilado.
    """
    global _CONTEXT
    if port is None:
        port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    db_path = db_path or os.environ.get("FITADAPT_DB", DEFAULT_DB)
    conn = connect(db_path)
    init_db(conn)
    _CONTEXT = make_context(conn)
    servidor = HTTPServer((host, port), _Handler)
    estaticos = _static_dir()
    extra = f" | frontend: {estaticos}" if estaticos else ""
    print(f"FitAdapt AI API escuchando en http://{host}:{port} (BD: {db_path}){extra}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.server_close()
        conn.close()


if __name__ == "__main__":
    run()
