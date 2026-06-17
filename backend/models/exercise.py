"""Modelo de ejercicio.

Cada ejercicio guarda la informacion que el motor necesita para decidir si es
seguro y adecuado para una persona concreta: que musculos trabaja, donde se
puede hacer, que equipamiento requiere, su impacto articular, etc.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# Niveles validos de impacto articular, de menor a mayor estres en las articulaciones.
JOINT_IMPACTS = ("low", "moderate", "high")

# Entornos donde se puede entrenar.
ENVIRONMENTS = ("gym", "home", "outdoor")


@dataclass(frozen=True)
class Exercise:
    """Un ejercicio del catalogo.

    Atributos:
        id: identificador unico (p. ej. "back_squat").
        name: nombre legible.
        primary_muscles: musculos principales que trabaja.
        secondary_muscles: musculos secundarios.
        environments: entornos donde se puede realizar (gym/home/outdoor).
        equipment_required: equipamiento necesario; ["none"] si no requiere nada.
        intensity_min / intensity_max: rango de intensidad posible (escala 1-10).
        joint_impact: impacto sobre las articulaciones ("low"/"moderate"/"high").
        movement_pattern: patron de movimiento (squat, hinge, push, pull, lunge,
            cardio, core, jump, spinal_flexion, isometric_hold, mobility, isolation).
        is_hiit: True si es entrenamiento interválico de alta intensidad.
        cardiovascular_demand: demanda cardiovascular ("low"/"moderate"/"high").
        beneficial_for: claves de condiciones para las que es especialmente bueno.
        contraindicated_conditions: claves de condiciones para las que NO es seguro.
        base_xp: puntos base para la gamificacion.
    """

    id: str
    name: str
    primary_muscles: List[str]
    secondary_muscles: List[str] = field(default_factory=list)
    environments: List[str] = field(default_factory=lambda: ["gym"])
    equipment_required: List[str] = field(default_factory=lambda: ["none"])
    intensity_min: int = 1
    intensity_max: int = 10
    joint_impact: str = "low"
    movement_pattern: str = "general"
    is_hiit: bool = False
    cardiovascular_demand: str = "low"
    beneficial_for: List[str] = field(default_factory=list)
    contraindicated_conditions: List[str] = field(default_factory=list)
    base_xp: int = 10

    def all_muscles(self) -> List[str]:
        """Devuelve todos los musculos trabajados (principales + secundarios)."""
        return list(self.primary_muscles) + list(self.secondary_muscles)

    def needs_only(self, available_equipment) -> bool:
        """True si el usuario tiene todo el equipamiento necesario.

        El valor "none" siempre esta disponible (no requiere nada).
        """
        disponible = set(available_equipment) | {"none"}
        return all(eq in disponible for eq in self.equipment_required)
