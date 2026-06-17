"""Adaptacion de la intensidad y del HIIT segun salud, fatiga y contexto.

La intensidad recomendada nunca debe superar lo que es seguro para la persona.
Aqui combinamos los topes por condicion de salud con el contexto del dia
(sueno, turnos de noche, estres).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..models.user_profile import UserProfile

# Intensidad maxima absoluta de la escala (1-10).
MAX_SCALE = 10


@dataclass
class WorkoutContext:
    """Contexto del dia que afecta a la intensidad recomendada.

    Atributos:
        sleep_hours: horas dormidas la noche anterior (None si se desconoce).
        consecutive_night_shifts: turnos de noche seguidos recientes.
        stress_level: nivel de estres reportado (1-10).
    """

    sleep_hours: Optional[float] = None
    consecutive_night_shifts: int = 0
    stress_level: int = 1


def condition_intensity_cap(profile: UserProfile) -> int:
    """Tope de intensidad mas estricto entre las condiciones del usuario."""
    cap = MAX_SCALE
    for c in profile.conditions:
        if c.max_intensity is not None:
            cap = min(cap, c.max_intensity)
    return cap


def condition_hiit_limit(profile: UserProfile) -> Optional[int]:
    """Maximo de sesiones HIIT/semana segun las condiciones (None = sin limite)."""
    limites: List[int] = [c.max_hiit_per_week for c in profile.conditions
                          if c.max_hiit_per_week is not None]
    return min(limites) if limites else None


def max_allowed_intensity(profile: UserProfile,
                          context: Optional[WorkoutContext] = None) -> int:
    """Intensidad maxima permitida hoy (escala 1-10).

    Parte del tope por condiciones de salud y lo reduce segun el contexto:
      - Dormir menos de 6 h: se limita al 60% de la escala (=6).
      - 3 o mas turnos de noche seguidos: se reduce en 2 puntos por fatiga.
    """
    cap = condition_intensity_cap(profile)
    if context is not None:
        if context.sleep_hours is not None and context.sleep_hours < 6:
            cap = min(cap, 6)  # 60% de 10
        if context.consecutive_night_shifts >= 3:
            cap = max(1, cap - 2)
    return cap


def adapt_exercise_intensity(intensity_max: int, profile: UserProfile,
                             context: Optional[WorkoutContext] = None) -> int:
    """Ajusta la intensidad objetivo de un ejercicio al tope permitido."""
    return min(intensity_max, max_allowed_intensity(profile, context))
