"""Sustitucion de ejercicios entre entornos (gimnasio, casa, exterior).

Si un ejercicio no se puede hacer en el entorno/equipamiento del usuario, busca
la mejor alternativa: un ejercicio seguro y disponible que trabaje los mismos
musculos y, a ser posible, con el mismo patron de movimiento.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..data.exercises import EXERCISES
from ..models.exercise import Exercise
from ..models.user_profile import UserProfile
from .condition_filter import is_available, is_safe


def _similarity(candidate: Exercise, original: Exercise) -> int:
    """Puntua cuanto se parece un candidato al ejercicio original.

    +2 si comparten el patron de movimiento; +1 por cada musculo principal comun.
    """
    score = 0
    if candidate.movement_pattern == original.movement_pattern:
        score += 2
    score += len(set(candidate.primary_muscles) & set(original.primary_muscles))
    return score


def substitute_exercise(exercise: Exercise, profile: UserProfile,
                        catalog: Optional[List[Exercise]] = None) -> Optional[Exercise]:
    """Devuelve el ejercicio a realizar para el usuario.

    - Si el ejercicio ya es seguro y disponible, lo devuelve tal cual.
    - Si no, busca la mejor alternativa segura y disponible que comparta
      musculos. Devuelve None si no hay ninguna.
    """
    cat = catalog if catalog is not None else EXERCISES
    if is_safe(exercise, profile) and is_available(exercise, profile):
        return exercise

    candidatos = [
        e for e in cat
        if e.id != exercise.id
        and is_safe(e, profile)
        and is_available(e, profile)
        and set(e.primary_muscles) & set(exercise.primary_muscles)
    ]
    if not candidatos:
        return None
    # Mayor similitud primero; en empate, orden alfabetico para ser deterministas.
    candidatos.sort(key=lambda e: (-_similarity(e, exercise), e.name))
    return candidatos[0]


@dataclass
class Substitution:
    """Resultado de adaptar un ejercicio al entorno del usuario."""

    original: Exercise
    resolved: Optional[Exercise]
    changed: bool


def adapt_plan(exercises: List[Exercise], profile: UserProfile,
               catalog: Optional[List[Exercise]] = None) -> List[Substitution]:
    """Adapta una lista de ejercicios al entorno y equipamiento del usuario."""
    resultado = []
    for ex in exercises:
        sub = substitute_exercise(ex, profile, catalog)
        cambiado = sub is not None and sub.id != ex.id
        resultado.append(Substitution(original=ex, resolved=sub, changed=cambiado))
    return resultado
