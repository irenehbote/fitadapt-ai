"""Integracion con Google Fit.

Dos partes:
  1. Lógica REAL y testeable de como los datos importados (sueno, pasos,
     frecuencia cardiaca en reposo) ajustan la recomendacion del dia.
  2. Un cliente `GoogleFitClient` que representa el punto de integracion con la
     API real. La conexion OAuth y las llamadas de red NO estan implementadas y
     lanzan NotImplementedError a proposito: no se simulan datos de red.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Permisos (scopes) que pediria la integracion real con Google Fit.
OAUTH_SCOPES = (
    "fitness.activity.read",
    "fitness.body.read",
    "fitness.heart_rate.read",
    "fitness.sleep.read",
)


@dataclass
class HealthData:
    """Datos de salud importados de una app (p. ej. Google Fit)."""

    steps_today: Optional[int] = None
    sleep_hours_last_night: Optional[float] = None
    resting_hr_trend: Optional[str] = None   # "increasing"/"stable"/"decreasing"
    active_minutes_week: Optional[int] = None
    weight_kg: Optional[float] = None


@dataclass
class Adjustments:
    """Ajustes recomendados a partir de los datos de salud."""

    intensity_cap: int = 10
    reduce_cardio: bool = False
    suggest_deload: bool = False
    notes: List[str] = field(default_factory=list)


def recommend_adjustments(data: HealthData, base_intensity_cap: int = 10) -> Adjustments:
    """Traduce los datos importados en ajustes concretos del plan del dia.

    Reglas:
      - Dormir menos de 6 h: limitar la intensidad al 60% (=6).
      - Mas de 10.000 pasos hoy: reducir el volumen de cardio.
      - Tendencia de frecuencia cardiaca en reposo al alza: posible
        sobreentrenamiento -> sugerir semana de descarga (deload).
    """
    adj = Adjustments(intensity_cap=base_intensity_cap)

    if data.sleep_hours_last_night is not None and data.sleep_hours_last_night < 6:
        adj.intensity_cap = min(adj.intensity_cap, 6)
        adj.notes.append("Has dormido poco: hoy limitamos la intensidad al 60%.")

    if data.steps_today is not None and data.steps_today > 10000:
        adj.reduce_cardio = True
        adj.notes.append("Ya llevas muchos pasos hoy: reducimos el cardio del plan.")

    if data.resting_hr_trend == "increasing":
        adj.suggest_deload = True
        adj.notes.append("Tu frecuencia cardiaca en reposo sube: considera una "
                         "semana de descarga para recuperar.")

    return adj


class GoogleFitClient:
    """Punto de integracion con la API de Google Fit (no implementado)."""

    def __init__(self, scopes=OAUTH_SCOPES):
        self.scopes = tuple(scopes)
        self.connected = False

    def connect(self) -> None:
        """Iniciaria el flujo OAuth2. No implementado (requiere credenciales reales)."""
        raise NotImplementedError(
            "La conexion OAuth con Google Fit requiere credenciales y un flujo de "
            "autorizacion reales; aun no esta integrada.")

    def fetch_recent(self):
        """Descargaria los datos recientes. No implementado."""
        raise NotImplementedError("Pendiente de la conexion real con Google Fit.")

    @staticmethod
    def normalize(raw: dict) -> HealthData:
        """Convierte un payload crudo en un HealthData (parte pura y testeable).

        Acepta minutos de sueno o horas, y nombres habituales de campos.
        """
        sueno_horas = raw.get("sleep_hours")
        if sueno_horas is None and raw.get("sleep_minutes") is not None:
            sueno_horas = round(raw["sleep_minutes"] / 60, 2)
        return HealthData(
            steps_today=raw.get("steps"),
            sleep_hours_last_night=sueno_horas,
            resting_hr_trend=raw.get("resting_hr_trend"),
            active_minutes_week=raw.get("active_minutes_week"),
            weight_kg=raw.get("weight_kg"),
        )
