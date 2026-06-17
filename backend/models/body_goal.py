"""Objetivo corporal del usuario y como afecta a los parametros del plan.

Hay tres objetivos posibles: perder peso, mantener o ganar musculo. Cada uno
cambia cuanto cardio y cuanta fuerza se programa, los rangos de repeticiones,
cuanto HIIT, etc.
"""
from __future__ import annotations

from enum import Enum


class BodyGoal(Enum):
    """Objetivo principal del usuario."""

    LOSE = "lose"        # Perder grasa / peso
    MAINTAIN = "maintain"  # Mantener la composicion actual
    GAIN = "gain"        # Ganar musculo / peso


# Parametros del plan segun el objetivo.
# Las sesiones se expresan como rango (minimo, maximo) por semana.
_GOAL_PARAMETERS = {
    BodyGoal.LOSE: {
        "cardio_sessions_per_week": (3, 4),
        "strength_sessions_per_week": (3, 4),
        "hiit_sessions_per_week": 2,
        "rep_range": (12, 20),
        "rest_seconds": (60, 90),
        "priority_metric": "composicion_corporal",
    },
    BodyGoal.MAINTAIN: {
        "cardio_sessions_per_week": (2, 3),
        "strength_sessions_per_week": (3, 3),
        "hiit_sessions_per_week": 1,
        "rep_range": (8, 12),
        "rest_seconds": (90, 120),
        "priority_metric": "equilibrio",
    },
    BodyGoal.GAIN: {
        "cardio_sessions_per_week": (1, 2),
        "strength_sessions_per_week": (4, 5),
        "hiit_sessions_per_week": 0,
        "rep_range": (6, 12),
        "rest_seconds": (120, 180),
        "priority_metric": "fuerza",
    },
}


def goal_parameters(goal: BodyGoal) -> dict:
    """Devuelve una copia de los parametros del plan para el objetivo dado."""
    return dict(_GOAL_PARAMETERS[goal])
