"""Optimizacion del entrenamiento segun turnos, horarios de gimnasio y fatiga.

Pensado para personas con turnos de noche o rotativos, que ademas pueden tener
acceso limitado al gimnasio por horario. Calcula:
  - una puntuacion de fatiga acumulada,
  - el tope de intensidad recomendado segun esa fatiga,
  - si el gimnasio esta disponible en la franja del usuario (y si no, avisa),
  - la mejor franja para entrenar tras un turno.
"""
from __future__ import annotations

from enum import Enum
from typing import Tuple


class ShiftType(Enum):
    """Tipos de turno de trabajo."""

    DAY = "day"
    NIGHT = "night"
    ROTATING = "rotating"
    OFF = "off"


def fatigue_score(consecutive_work_days: int, night_shifts_this_week: int,
                  hours_slept_last_night: float, stress_level: int = 1) -> int:
    """Puntuacion de fatiga acumulada (0-100). >70 = fatiga alta.

    Combina dias trabajados seguidos, turnos de noche de la semana, deficit de
    sueno respecto a 7 h y el estres reportado (1-10).
    """
    bruto = (
        consecutive_work_days * 8
        + night_shifts_this_week * 15
        + (7 - hours_slept_last_night) * 10
        + stress_level * 5
    )
    # Acotamos al rango 0-100.
    return int(max(0, min(100, round(bruto))))


def is_high_fatigue(score: int) -> bool:
    """True si la fatiga es alta (conviene reducir intensidad)."""
    return score > 70


def fatigue_adjusted_intensity_cap(score: int, base_cap: int = 10) -> int:
    """Tope de intensidad recomendado segun la fatiga.

    - Fatiga alta (>70): se limita al 60% de la escala.
    - Fatiga moderada (>60): se reduce un 25%.
    - Resto: sin cambios.
    """
    if score > 70:
        return min(base_cap, 6)
    if score > 60:
        return min(base_cap, round(base_cap * 0.75))
    return base_cap


def gym_available_for_slot(slot_start: float, slot_end: float,
                           open_hour: float, close_hour: float) -> bool:
    """True si la franja [slot_start, slot_end] cabe dentro del horario del gym.

    Las horas van en formato 24 h (p. ej. 21.5 = 21:30). Un gimnasio 24 h se
    indica con open_hour=0 y close_hour=24.
    """
    if slot_start > slot_end:
        raise ValueError("La franja no puede empezar despues de terminar")
    return open_hour <= slot_start and slot_end <= close_hour


def closing_soon(slot_end: float, close_hour: float, margin_minutes: int = 45) -> bool:
    """True si el gym cierra dentro del margen tras el fin de la franja.

    Sirve para avisar de acortar el entreno y priorizar ejercicios compuestos.
    """
    return 0 <= (close_hour - slot_end) * 60 <= margin_minutes


def optimal_workout_window(wake_hour: float) -> Tuple[float, float]:
    """Mejor franja para entrenar: 4-6 h despues de despertar (formato 24 h)."""
    inicio = (wake_hour + 4) % 24
    fin = (wake_hour + 6) % 24
    return (inicio, fin)
