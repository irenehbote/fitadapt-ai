"""Catalogo de condiciones de salud soportadas, con sus reglas de adaptacion.

Las reglas estan basadas en pautas generales de ejercicio adaptado. NO son
consejo medico: ver MEDICAL_DISCLAIMER.md.
"""
from __future__ import annotations

from typing import Dict, List

from ..models.health_conditions import HealthCondition


# Diccionario clave -> condicion. Es la "base de datos" de condiciones.
CONDITIONS: Dict[str, HealthCondition] = {
    "pcos": HealthCondition(
        key="pcos",
        name="Sindrome de ovario poliquistico (SOP)",
        # El exceso de HIIT puede empeorar el equilibrio hormonal (cortisol).
        max_hiit_per_week=3,
        # La perdida de peso suele ser mas lenta; ajustamos expectativas.
        weight_loss_rate_factor=0.7,
        difficulty_multiplier=1.2,
        notes="Priorizar fuerza (mejora la sensibilidad a la insulina). "
              "Limitar HIIT a 3/semana para no disparar el cortisol.",
    ),
    "hypothyroidism": HealthCondition(
        key="hypothyroidism",
        name="Hipotiroidismo",
        weight_loss_rate_factor=0.5,
        difficulty_multiplier=1.3,
        notes="La fatiga es real y el gasto energetico es menor de lo esperado. "
              "Mas descanso entre sesiones y celebrar logros no relacionados con la bascula.",
    ),
    "type2_diabetes": HealthCondition(
        key="type2_diabetes",
        name="Diabetes tipo 2",
        difficulty_multiplier=1.1,
        notes="El entrenamiento de fuerza mejora la sensibilidad a la insulina. "
              "Entrenar 1-3 h despues de comer ayuda a controlar la glucosa.",
    ),
    "cardiovascular_disease": HealthCondition(
        key="cardiovascular_disease",
        name="Enfermedad cardiovascular",
        # Nada de alta intensidad ni HIIT; evitar sostenidos isometricos largos.
        max_intensity=6,
        max_hiit_per_week=0,
        contraindicated_movement_patterns=frozenset({"isometric_hold"}),
        difficulty_multiplier=1.2,
        notes="Respetar zonas de frecuencia cardiaca. Calentar minimo 10 min y "
              "evitar maniobra de Valsalva (aguantar la respiracion al esforzarse).",
    ),
    "osteoporosis": HealthCondition(
        key="osteoporosis",
        name="Osteoporosis",
        # Evitar impacto alto (riesgo de fractura) y flexion forzada de columna.
        contraindicated_joint_impacts=frozenset({"high"}),
        contraindicated_movement_patterns=frozenset({"jump", "spinal_flexion"}),
        difficulty_multiplier=1.2,
        notes="Requiere ejercicio con carga para estimular el hueso, pero sin "
              "impacto alto ni flexion de columna (nada de saltos ni abdominales clasicos).",
    ),
    "fibromyalgia": HealthCondition(
        key="fibromyalgia",
        name="Fibromialgia",
        # Empezar a baja intensidad por el umbral de dolor mas bajo.
        max_intensity=5,
        difficulty_multiplier=1.5,
        notes="Empezar al 40-50% de la intensidad habitual y subir como mucho un "
              "10% por semana. Los dias de brote, movilidad suave y caminar.",
    ),
    "asthma": HealthCondition(
        key="asthma",
        name="Asma",
        difficulty_multiplier=1.1,
        notes="Calentamiento largo (15 min) para evitar broncoconstriccion. "
              "Mejor formato interválico que alta intensidad sostenida.",
    ),
    "knee_osteoarthritis_severe": HealthCondition(
        key="knee_osteoarthritis_severe",
        name="Artrosis de rodilla (grave)",
        # Evitar impacto alto en las articulaciones.
        contraindicated_joint_impacts=frozenset({"high"}),
        contraindicated_movement_patterns=frozenset({"jump"}),
        difficulty_multiplier=1.2,
        notes="Evitar alto impacto y cargas axiales pesadas en la rodilla. "
              "Preferir trabajo de bajo impacto y fortalecimiento controlado.",
    ),
}


def get_condition(key: str) -> HealthCondition:
    """Devuelve la condicion de salud con esa clave (lanza KeyError si no existe)."""
    return CONDITIONS[key]


def get_conditions(keys: List[str]) -> List[HealthCondition]:
    """Devuelve la lista de condiciones para las claves dadas."""
    return [CONDITIONS[k] for k in keys]
