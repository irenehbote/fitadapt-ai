"""Geometria pura del pipeline de fotos (sin dependencias externas).

A partir de anchuras medidas en una silueta (en pixeles) y de la altura real de
la persona, estimamos circunferencias en centimetros. La idea:

  1. Calibrar la escala: si conocemos la altura real (cm) y la altura en pixeles,
     obtenemos cuantos cm mide cada pixel.
  2. Aproximar cada seccion del cuerpo (cintura, cadera...) como una ELIPSE cuyos
     ejes son la anchura (vista frontal) y la profundidad (vista lateral).
  3. Calcular el perimetro de la elipse con la aproximacion de Ramanujan.

Es una aproximacion: el cuerpo no es una elipse perfecta. Sirve para una
estimacion orientativa, no para una medicion exacta.
"""
from __future__ import annotations

import math


def cm_per_pixel(height_px: float, real_height_cm: float) -> float:
    """Cuantos centimetros representa cada pixel, dada la altura real."""
    if height_px <= 0 or real_height_cm <= 0:
        raise ValueError("La altura en pixeles y en cm debe ser positiva")
    return real_height_cm / height_px


def ellipse_perimeter(semi_axis_a: float, semi_axis_b: float) -> float:
    """Perimetro de una elipse (aproximacion de Ramanujan).

    Para un circulo (a == b == r) se reduce a 2*pi*r, como debe ser.
    """
    if semi_axis_a < 0 or semi_axis_b < 0:
        raise ValueError("Los semiejes no pueden ser negativos")
    a, b = semi_axis_a, semi_axis_b
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))


def circumference_cm(front_width_px: float, side_depth_px: float,
                     cm_per_px: float) -> float:
    """Circunferencia (cm) de una seccion, dada su anchura frontal y profundidad lateral."""
    if front_width_px <= 0 or side_depth_px <= 0 or cm_per_px <= 0:
        raise ValueError("Las medidas deben ser positivas")
    a = (front_width_px * cm_per_px) / 2  # semieje frontal en cm
    b = (side_depth_px * cm_per_px) / 2   # semieje lateral en cm
    return round(ellipse_perimeter(a, b), 1)
