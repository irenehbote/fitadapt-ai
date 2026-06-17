"""API REST mínima de FitAdapt AI.

Se implementa con la libreria estandar (`http.server`) para que el proyecto
siga funcionando sin instalar nada. La lógica de enrutado vive en `route()`,
una funcion pura y facil de testear sin abrir sockets; el servidor HTTP solo
la envuelve.

Migrar a FastAPI mas adelante seria directo: las mismas funciones de dominio
(build_profile_from_dict / serialize_recommendation) se reutilizarian.

Endpoints:
    GET  /health            -> estado del servicio
    GET  /conditions        -> condiciones de salud soportadas
    GET  /exercises         -> catalogo de ejercicios
    POST /recommendations   -> recomendacion semanal para un perfil (JSON)
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Tuple

from ..data.condition_rules import CONDITIONS, get_conditions
from ..data.exercises import EXERCISES
from ..engine.recommendation_engine import generate_recommendations
from ..models.body_goal import BodyGoal
from ..models.muscle_focus import MuscleFocus
from ..models.user_profile import UserProfile


def build_profile_from_dict(payload: dict) -> UserProfile:
    """Crea un UserProfile a partir del cuerpo JSON de la peticion.

    Lanza ValueError si algun dato no es valido (clave de condicion u objetivo
    desconocidos), para responder con 400.
    """
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


def route(method: str, path: str, body: Optional[dict] = None) -> Tuple[int, dict]:
    """Resuelve una peticion y devuelve (codigo_http, cuerpo_json)."""
    if method == "GET" and path == "/health":
        return 200, {"status": "ok"}

    if method == "GET" and path == "/conditions":
        return 200, {"conditions": [{"key": c.key, "name": c.name}
                                    for c in CONDITIONS.values()]}

    if method == "GET" and path == "/exercises":
        return 200, {"exercises": [{"id": e.id, "name": e.name,
                                    "environments": e.environments}
                                   for e in EXERCISES]}

    if method == "POST" and path == "/recommendations":
        try:
            perfil = build_profile_from_dict(body or {})
        except ValueError as e:
            return 400, {"error": str(e)}
        rec = generate_recommendations(perfil)
        return 200, serialize_recommendation(rec)

    return 404, {"error": "Ruta no encontrada"}


class _Handler(BaseHTTPRequestHandler):
    """Adaptador HTTP: lee la peticion, llama a route() y escribe la respuesta."""

    def _responder(self, status: int, payload: dict) -> None:
        cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        # CORS: permite que el frontend (otro puerto) consuma la API.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_OPTIONS(self):  # noqa: N802 (preflight CORS)
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):  # noqa: N802 (nombre exigido por la libreria)
        status, payload = route("GET", self.path)
        self._responder(status, payload)

    def do_POST(self):  # noqa: N802
        longitud = int(self.headers.get("Content-Length", 0))
        crudo = self.rfile.read(longitud) if longitud else b"{}"
        try:
            body = json.loads(crudo.decode("utf-8"))
        except json.JSONDecodeError:
            self._responder(400, {"error": "JSON invalido"})
            return
        status, payload = route("POST", self.path, body)
        self._responder(status, payload)

    def log_message(self, *args):  # silencia el log por defecto
        pass


def run(port: int = 8000) -> None:
    """Arranca el servidor HTTP (Ctrl+C para parar)."""
    servidor = HTTPServer(("127.0.0.1", port), _Handler)
    print(f"FitAdapt AI API escuchando en http://127.0.0.1:{port}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.server_close()


if __name__ == "__main__":
    run()
