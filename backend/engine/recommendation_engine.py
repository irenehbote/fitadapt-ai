"""Motor de recomendacion: genera el plan semanal adaptado al usuario.

Combina todo lo anterior:
  - filtra ejercicios seguros y disponibles (condition_filter),
  - reparte el volumen por musculo (muscle_focus),
  - fija sesiones de cardio/fuerza y rangos segun el objetivo (body_goal),
  - limita el HIIT segun salud y objetivo,
  - calcula el tope de intensidad del dia (intensity_adapter).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..models.body_goal import goal_parameters
from ..models.exercise import Exercise
from ..models.user_profile import UserProfile
from ..data.exercises import EXERCISES
from .condition_filter import filter_exercises
from .intensity_adapter import (WorkoutContext, condition_hiit_limit,
                                max_allowed_intensity)


@dataclass
class Recommendation:
    """Resultado de la recomendacion semanal."""

    safe_exercises: List[Exercise]
    volume_allocation: Dict[str, int]
    cardio_sessions_per_week: tuple
    strength_sessions_per_week: tuple
    weekly_hiit_limit: int
    max_intensity_today: int
    exercises_by_muscle: Dict[str, List[Exercise]] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def weekly_hiit_limit(profile: UserProfile) -> int:
    """Sesiones de HIIT/semana finales: lo mas bajo entre objetivo y salud."""
    objetivo = goal_parameters(profile.goal)["hiit_sessions_per_week"]
    salud = condition_hiit_limit(profile)
    if salud is None:
        return objetivo
    return min(objetivo, salud)


def _group_by_primary_muscle(exercises: List[Exercise]) -> Dict[str, List[Exercise]]:
    """Agrupa los ejercicios por su primer musculo principal."""
    grupos: Dict[str, List[Exercise]] = {}
    for ex in exercises:
        if not ex.primary_muscles:
            continue
        grupos.setdefault(ex.primary_muscles[0], []).append(ex)
    return grupos


def generate_recommendations(profile: UserProfile,
                             exercises: Optional[List[Exercise]] = None,
                             context: Optional[WorkoutContext] = None) -> Recommendation:
    """Genera la recomendacion semanal completa para el perfil dado."""
    catalogo = exercises if exercises is not None else EXERCISES
    seguros = filter_exercises(catalogo, profile)
    params = goal_parameters(profile.goal)

    rec = Recommendation(
        safe_exercises=seguros,
        volume_allocation=profile.muscle_focus.volume_allocation(),
        cardio_sessions_per_week=params["cardio_sessions_per_week"],
        strength_sessions_per_week=params["strength_sessions_per_week"],
        weekly_hiit_limit=weekly_hiit_limit(profile),
        max_intensity_today=max_allowed_intensity(profile, context),
        exercises_by_muscle=_group_by_primary_muscle(seguros),
    )

    # Notas humanas: recordamos las adaptaciones de cada condicion.
    for c in profile.conditions:
        if c.notes:
            rec.notes.append(f"{c.name}: {c.notes}")
    return rec
