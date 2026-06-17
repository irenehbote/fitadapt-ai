"""Puntuacion justa de XP para la gamificacion.

Principio clave: quien entrena con condiciones de salud que dificultan el
ejercicio debe recibir un reconocimiento proporcional. Por eso el XP se
multiplica por la dificultad combinada del perfil. Asi, el mismo esfuerzo
puntua mas para quien lo tiene mas dificil.
"""
from __future__ import annotations

from enum import Enum

from ..models.exercise import Exercise
from ..models.user_profile import UserProfile


class RPGClass(Enum):
    """Clases de personaje (solo visibles dentro de un reto)."""

    WARRIOR = "warrior"        # Fuerza / cargas pesadas
    RANGER = "ranger"          # Cardio / exterior
    MONK = "monk"              # Flexibilidad / cuerpo-mente
    PALADIN = "paladin"        # Equilibrado
    BERSERKER = "berserker"    # HIIT / alta intensidad


def intensity_multiplier(intensity: int) -> float:
    """Multiplicador segun la intensidad (escala 1-10 -> 0.5 a 2.0)."""
    if not 1 <= intensity <= 10:
        raise ValueError("La intensidad debe estar entre 1 y 10")
    return round(0.5 + (intensity - 1) / 9 * 1.5, 3)


def consistency_bonus(streak_days: int) -> float:
    """Bonus por racha: +0.1 por dia, partiendo de 1.0 y con tope en 2.0."""
    if streak_days < 0:
        raise ValueError("La racha no puede ser negativa")
    return min(2.0, round(1.0 + 0.1 * streak_days, 3))


def exercise_xp(exercise: Exercise, intensity: int, streak_days: int,
                profile: UserProfile) -> int:
    """XP ganado por un ejercicio, con hándicap justo segun la condicion.

    xp = base * mult_intensidad * bonus_consistencia * dificultad_condicion
    """
    xp = (
        exercise.base_xp
        * intensity_multiplier(intensity)
        * consistency_bonus(streak_days)
        * profile.combined_difficulty_multiplier()
    )
    return round(xp)
