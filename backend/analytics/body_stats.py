"""Analitica de progreso corporal con estadistica basica (solo libreria estandar).

Incluye media movil, tendencia lineal (ritmo de cambio) y una puntuacion de
progreso que tiene en cuenta la condicion de salud: para algunas condiciones un
ritmo mas lento es perfectamente NORMAL, y el sistema no debe penalizarlo.
"""
from __future__ import annotations

from typing import List, Sequence

from ..models.health_conditions import HealthCondition


def moving_average(values: Sequence[float], window: int) -> List[float]:
    """Media movil simple. Suaviza el ruido del dia a dia (p. ej. el peso)."""
    if window <= 0:
        raise ValueError("La ventana debe ser un entero positivo")
    if len(values) < window:
        return []
    medias = []
    for i in range(len(values) - window + 1):
        tramo = values[i:i + window]
        medias.append(sum(tramo) / window)
    return medias


def linear_trend(values: Sequence[float]) -> float:
    """Pendiente de la recta de minimos cuadrados (cambio medio por paso).

    Negativo = bajando (p. ej. perdiendo peso); positivo = subiendo.
    Se asume que las medidas estan igualmente espaciadas en el tiempo.
    """
    n = len(values)
    if n < 2:
        raise ValueError("Se necesitan al menos dos valores")
    xs = list(range(n))
    media_x = sum(xs) / n
    media_y = sum(values) / n
    numerador = sum((x - media_x) * (y - media_y) for x, y in zip(xs, values))
    denominador = sum((x - media_x) ** 2 for x in xs)
    if denominador == 0:
        return 0.0
    return numerador / denominador


def percent_change(first: float, last: float) -> float:
    """Cambio porcentual entre el primer y el ultimo valor."""
    if first == 0:
        raise ValueError("El valor inicial no puede ser cero")
    return (last - first) / first * 100.0


def progress_score(values: Sequence[float], condition: HealthCondition | None = None,
                   lower_is_better: bool = True) -> float:
    """Puntuacion de progreso 0-100 ajustada a la condicion de salud.

    Mide cuanto ha cambiado la serie en la direccion deseada respecto a una
    referencia del 10% de cambio total. Si hay una condicion que hace el cambio
    mas lento (p. ej. hipotiroidismo), se divide la expectativa por su factor,
    de modo que un avance "lento pero real" siga puntuando bien.
    """
    if len(values) < 2:
        return 0.0
    cambio = percent_change(values[0], values[-1])
    # Si lo bueno es bajar (peso, grasa), un cambio negativo es progreso.
    avance = -cambio if lower_is_better else cambio

    expectativa = 10.0  # referencia: un 10% de cambio se considera "completo"
    if condition is not None and condition.weight_loss_rate_factor > 0:
        expectativa *= condition.weight_loss_rate_factor

    puntuacion = avance / expectativa * 100.0
    # Acotamos entre 0 y 100.
    return round(max(0.0, min(100.0, puntuacion)), 1)
