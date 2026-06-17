"""Modelo de condiciones de salud (enfermedades y sindromes).

Cada condicion describe COMO debe adaptarse el ejercicio para una persona que
la padece: que ejercicios evitar, cuanta intensidad permitir, cuanto HIIT como
maximo, y como ajustar las expectativas de progreso.

La idea central de FitAdapt AI es que el ejercicio "seguro y efectivo" depende
de la salud de cada persona. Este modelo es la base de esa inteligencia.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class HealthCondition:
    """Reglas de adaptacion del ejercicio para una condicion de salud concreta.

    Atributos:
        key: identificador interno (p. ej. "pcos").
        name: nombre legible (p. ej. "Sindrome de ovario poliquistico").
        contraindicated_joint_impacts: niveles de impacto articular a evitar.
            Por ejemplo {"high"} significa "nada de alto impacto".
        contraindicated_movement_patterns: patrones de movimiento a evitar
            (p. ej. {"jump", "spinal_flexion"}).
        max_intensity: tope de intensidad permitido en la escala 1-10
            (None = sin tope por esta condicion).
        max_hiit_per_week: maximo de sesiones HIIT por semana
            (None = sin limite; 0 = HIIT no permitido).
        weight_loss_rate_factor: factor realista sobre el ritmo de perdida de
            peso. 1.0 = ritmo estandar; 0.6 = un 40% mas lento de lo habitual.
            Sirve para NO frustrar al usuario con expectativas irreales.
        difficulty_multiplier: cuanto mas dificil es entrenar con esta condicion
            (se usa para puntuar de forma justa en el modo retos).
        notes: explicacion breve y humana de la adaptacion.
    """

    key: str
    name: str
    contraindicated_joint_impacts: frozenset = field(default_factory=frozenset)
    contraindicated_movement_patterns: frozenset = field(default_factory=frozenset)
    max_intensity: Optional[int] = None
    max_hiit_per_week: Optional[int] = None
    weight_loss_rate_factor: float = 1.0
    difficulty_multiplier: float = 1.0
    notes: str = ""
