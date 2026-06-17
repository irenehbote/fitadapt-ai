"""Filtrado de ejercicios por seguridad y disponibilidad.

Este es el corazon de la seguridad de FitAdapt AI: dado un perfil con sus
condiciones de salud, descarta los ejercicios contraindicados y los que el
usuario no puede hacer (por entorno o falta de equipamiento).
"""
from __future__ import annotations

from typing import List, Optional

from ..models.exercise import Exercise
from ..models.user_profile import UserProfile


def contraindication_reason(exercise: Exercise, profile: UserProfile) -> Optional[str]:
    """Devuelve el motivo por el que un ejercicio NO es seguro, o None si lo es.

    Comprueba, para cada condicion del usuario:
      1. Impacto articular prohibido (p. ej. osteoporosis y alto impacto).
      2. Patron de movimiento prohibido (p. ej. saltos, flexion de columna).
      3. Contraindicacion explicita del ejercicio para esa condicion.
    """
    for condition in profile.conditions:
        if exercise.joint_impact in condition.contraindicated_joint_impacts:
            return (f"{condition.name}: evitar impacto articular "
                    f"'{exercise.joint_impact}'")
        if exercise.movement_pattern in condition.contraindicated_movement_patterns:
            return (f"{condition.name}: evitar el patron "
                    f"'{exercise.movement_pattern}'")
        if condition.key in exercise.contraindicated_conditions:
            return f"{condition.name}: ejercicio contraindicado"
    return None


def is_safe(exercise: Exercise, profile: UserProfile) -> bool:
    """True si el ejercicio no esta contraindicado para el usuario."""
    return contraindication_reason(exercise, profile) is None


def is_available(exercise: Exercise, profile: UserProfile) -> bool:
    """True si el usuario puede hacer el ejercicio con su entorno y equipamiento."""
    entorno_ok = any(env in profile.available_environments
                     for env in exercise.environments)
    equipo_ok = exercise.needs_only(profile.available_equipment)
    return entorno_ok and equipo_ok


def filter_exercises(exercises: List[Exercise], profile: UserProfile,
                     require_available: bool = True) -> List[Exercise]:
    """Devuelve los ejercicios seguros (y, por defecto, tambien disponibles)."""
    resultado = []
    for ex in exercises:
        if not is_safe(ex, profile):
            continue
        if require_available and not is_available(ex, profile):
            continue
        resultado.append(ex)
    return resultado
