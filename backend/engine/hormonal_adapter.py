"""Adaptacion del ejercicio segun la fase del ciclo hormonal.

A lo largo del ciclo menstrual cambian la energia y la recuperacion. Para
algunas condiciones (SOP, hipotiroidismo, menopausia) conviene ajustar la
intensidad en ciertas fases. Este modulo calcula la fase a partir del dia del
ciclo y devuelve un factor de intensidad (0-1) y una nota explicativa.

Las pautas son generales y educativas (ver MEDICAL_DISCLAIMER.md).
"""
from __future__ import annotations

from enum import Enum
from typing import List

from ..models.user_profile import UserProfile


class CyclePhase(Enum):
    """Fases del ciclo menstrual."""

    MENSTRUAL = "menstrual"      # Dias 1-5: energia tipicamente mas baja
    FOLLICULAR = "follicular"    # Hasta la ovulacion: energia en aumento (pico)
    OVULATION = "ovulation"      # Mitad del ciclo
    LUTEAL = "luteal"            # Tras la ovulacion: puede bajar la energia


def phase_for_day(cycle_day: int, cycle_length: int = 28) -> CyclePhase:
    """Devuelve la fase del ciclo para un dia dado (1 = primer dia de regla)."""
    if not 1 <= cycle_day <= cycle_length:
        raise ValueError("cycle_day debe estar entre 1 y cycle_length")
    ovulacion = round(cycle_length / 2)
    if cycle_day <= 5:
        return CyclePhase.MENSTRUAL
    if cycle_day < ovulacion:
        return CyclePhase.FOLLICULAR
    if cycle_day == ovulacion:
        return CyclePhase.OVULATION
    return CyclePhase.LUTEAL


# Factor base de intensidad por fase (multiplicador 0-1).
_PHASE_FACTOR = {
    CyclePhase.MENSTRUAL: 0.85,
    CyclePhase.FOLLICULAR: 1.0,
    CyclePhase.OVULATION: 1.0,
    CyclePhase.LUTEAL: 0.90,
}


def hormonal_intensity_factor(profile: UserProfile, cycle_day: int,
                              cycle_length: int = 28) -> float:
    """Factor de intensidad (0-1) segun la fase y las condiciones del usuario.

    Regla especial del SOP: en fase lutea se reduce un 15% adicional, porque el
    exceso de carga en esa fase puede empeorar el equilibrio hormonal.
    """
    fase = phase_for_day(cycle_day, cycle_length)
    factor = _PHASE_FACTOR[fase]
    if "pcos" in profile.condition_keys() and fase == CyclePhase.LUTEAL:
        factor *= 0.85
    return round(factor, 3)


def hormonal_notes(profile: UserProfile, cycle_day: int,
                   cycle_length: int = 28) -> List[str]:
    """Notas humanas sobre la adaptacion hormonal del dia."""
    fase = phase_for_day(cycle_day, cycle_length)
    notas = [f"Fase del ciclo: {fase.value} (dia {cycle_day}/{cycle_length})."]
    if fase == CyclePhase.LUTEAL:
        notas.append("Fase lutea: prioriza recuperacion; reduce algo la carga "
                     "si notas mas fatiga.")
    if "pcos" in profile.condition_keys() and fase == CyclePhase.LUTEAL:
        notas.append("SOP: reduce la intensidad ~15% en fase lutea.")
    if fase == CyclePhase.FOLLICULAR:
        notas.append("Fase folicular: buen momento para tus sesiones mas exigentes.")
    return notas
