"""Perfil de usuario: reune toda la informacion que el motor necesita.

Incluye la salud (condiciones), el objetivo, el enfoque muscular y el entorno
disponible (donde puede entrenar y con que equipamiento).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .body_goal import BodyGoal
from .health_conditions import HealthCondition
from .muscle_focus import MuscleFocus


@dataclass
class UserProfile:
    """Perfil completo de una persona usuaria.

    Atributos:
        name: nombre.
        age: edad en anios.
        conditions: lista de condiciones de salud que padece.
        goal: objetivo corporal (perder/mantener/ganar).
        muscle_focus: prioridades musculares.
        available_environments: entornos disponibles (gym/home/outdoor).
        available_equipment: equipamiento disponible.
    """

    name: str
    age: int
    conditions: List[HealthCondition] = field(default_factory=list)
    goal: BodyGoal = BodyGoal.MAINTAIN
    muscle_focus: MuscleFocus = field(default_factory=MuscleFocus)
    available_environments: List[str] = field(default_factory=lambda: ["home"])
    available_equipment: List[str] = field(default_factory=lambda: ["none"])

    def condition_keys(self) -> List[str]:
        """Devuelve las claves de las condiciones de salud del usuario."""
        return [c.key for c in self.conditions]

    def combined_difficulty_multiplier(self) -> float:
        """Multiplicador de dificultad combinando todas las condiciones.

        Para puntuar de forma justa en los retos: alguien con varias condiciones
        que dificultan el ejercicio recibe mas reconocimiento por el mismo
        esfuerzo. Se multiplican los factores de cada condicion.
        """
        factor = 1.0
        for c in self.conditions:
            factor *= c.difficulty_multiplier
        return round(factor, 4)
