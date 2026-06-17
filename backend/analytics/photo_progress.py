"""Informe de progreso corporal entre dos momentos.

Genera un informe comparando dos conjuntos de medidas (peso, cintura, % graso
si se conoce). El informe es honesto: trabaja con las MEDIDAS que se le pasan,
incluye contexto segun la condicion de salud y marca cambios poco plausibles.

NOTA sobre la estimacion por foto: estimar el % de grasa a partir de imagenes
requiere un modelo de vision por computador que NO esta integrado. La funcion
`estimate_body_fat_from_image` existe como punto de integracion y lanza
NotImplementedError a proposito, para no inventar resultados.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..models.health_conditions import HealthCondition
from .body_stats import percent_change, progress_score


@dataclass
class MeasurementSnapshot:
    """Medidas corporales en un momento dado."""

    label: str
    weight_kg: float
    waist_cm: float
    body_fat_pct: Optional[float] = None


@dataclass
class ProgressReport:
    """Resultado del informe de progreso entre dos medidas."""

    days_between: int
    weight_change_pct: float
    waist_change_cm: float
    body_fat_change: Optional[float]
    progress_score: float
    weekly_weight_change_kg: float
    plausible: bool
    commentary: List[str] = field(default_factory=list)


# Ritmo de cambio de peso considerado fisiologicamente plausible (kg/semana).
MAX_PLAUSIBLE_WEEKLY_KG = 1.5


def generate_progress_report(before: MeasurementSnapshot, after: MeasurementSnapshot,
                             days_between: int,
                             condition: Optional[HealthCondition] = None) -> ProgressReport:
    """Crea un informe de progreso comparando dos conjuntos de medidas."""
    if days_between <= 0:
        raise ValueError("days_between debe ser positivo")

    cambio_peso_pct = percent_change(before.weight_kg, after.weight_kg)
    cambio_cintura = round(after.waist_cm - before.waist_cm, 1)
    cambio_grasa = None
    if before.body_fat_pct is not None and after.body_fat_pct is not None:
        cambio_grasa = round(after.body_fat_pct - before.body_fat_pct, 1)

    semanas = days_between / 7
    cambio_semanal_kg = round((after.weight_kg - before.weight_kg) / semanas, 2)
    plausible = abs(cambio_semanal_kg) <= MAX_PLAUSIBLE_WEEKLY_KG

    score = progress_score([before.weight_kg, after.weight_kg], condition=condition,
                           lower_is_better=True)

    comentarios: List[str] = []
    if cambio_cintura < 0:
        comentarios.append(f"Cintura: {cambio_cintura} cm (reduccion).")
    if cambio_grasa is not None:
        comentarios.append(f"Grasa estimada: {cambio_grasa} puntos "
                           f"(margen tipico +/-3, ten cuidado al interpretar).")
    if condition is not None:
        comentarios.append(
            f"Para {condition.name}, un ritmo mas lento es NORMAL: "
            f"se valoran tambien los avances no relacionados con la bascula.")
    if not plausible:
        comentarios.append(
            "Cambio de peso inusualmente rapido: verifica que las medidas se "
            "tomaron en condiciones similares. Si es real, consulta con tu medico.")

    return ProgressReport(
        days_between=days_between,
        weight_change_pct=round(cambio_peso_pct, 2),
        waist_change_cm=cambio_cintura,
        body_fat_change=cambio_grasa,
        progress_score=score,
        weekly_weight_change_kg=cambio_semanal_kg,
        plausible=plausible,
        commentary=comentarios,
    )


def estimate_body_fat_from_image(image_bytes: bytes) -> float:
    """Punto de integracion para estimar % de grasa desde una foto.

    NO esta implementado: requiere un modelo de vision por computador
    (p. ej. deteccion de pose + estimacion de composicion). Lanza
    NotImplementedError a proposito para no devolver datos inventados.
    """
    raise NotImplementedError(
        "La estimacion de grasa corporal por imagen aun no esta integrada. "
        "Usa medidas manuales con generate_progress_report().")
