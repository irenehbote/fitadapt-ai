"""Estimacion del porcentaje de grasa corporal a partir de medidas.

Implementa dos metodos clasicos y validados sobre cinta metrica:
  - Marina de EE. UU. (Navy): usa circunferencias (cuello, cintura, cadera) y altura.
  - Deurenberg (basado en IMC): usa peso, altura, edad y sexo.

IMPORTANTE: son ESTIMACIONES con un margen tipico de +/-3-4% frente a metodos de
referencia (DEXA). No son una medicion clinica. Ver MEDICAL_DISCLAIMER.md.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class BodyFatEstimate:
    """Resultado de una estimacion de grasa corporal."""

    body_fat_pct: float
    method: str
    category: str
    confidence_note: str


def navy_body_fat(sex: str, height_cm: float, neck_cm: float, waist_cm: float,
                  hip_cm: Optional[float] = None) -> float:
    """Porcentaje de grasa corporal por la formula de la Marina de EE. UU.

    - Hombres: necesita cuello y cintura.
    - Mujeres: necesita ademas la cadera.
    Las medidas van en centimetros.
    """
    sex = sex.lower()
    if height_cm <= 0 or neck_cm <= 0 or waist_cm <= 0:
        raise ValueError("Las medidas deben ser positivas")

    if sex in ("male", "hombre", "m", "h"):
        if waist_cm - neck_cm <= 0:
            raise ValueError("La cintura debe ser mayor que el cuello")
        bf = (495 / (1.0324 - 0.19077 * math.log10(waist_cm - neck_cm)
                     + 0.15456 * math.log10(height_cm)) - 450)
    elif sex in ("female", "mujer", "f"):
        if hip_cm is None or hip_cm <= 0:
            raise ValueError("Para mujeres se necesita la cadera")
        if waist_cm + hip_cm - neck_cm <= 0:
            raise ValueError("Cintura + cadera deben superar el cuello")
        bf = (495 / (1.29579 - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm)
                     + 0.22100 * math.log10(height_cm)) - 450)
    else:
        raise ValueError(f"Sexo no reconocido: {sex}")

    return round(max(2.0, min(60.0, bf)), 1)


def deurenberg_body_fat(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Estimacion por IMC (Deurenberg). Menos precisa, pero no necesita cinta."""
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        raise ValueError("Peso, altura y edad deben ser positivos")
    sexo_codigo = 1 if sex.lower() in ("male", "hombre", "m", "h") else 0
    bmi = weight_kg / (height_cm / 100) ** 2
    bf = 1.20 * bmi + 0.23 * age - 10.8 * sexo_codigo - 5.4
    return round(max(2.0, min(60.0, bf)), 1)


# Umbrales de categoria (% grasa) por sexo, de menor a mayor.
_CATEGORIES = {
    "male": [(6, "esencial"), (14, "atletico"), (18, "en forma"),
             (25, "promedio"), (100, "elevado")],
    "female": [(14, "esencial"), (21, "atletico"), (25, "en forma"),
               (32, "promedio"), (100, "elevado")],
}


def body_fat_category(body_fat_pct: float, sex: str) -> str:
    """Clasifica un porcentaje de grasa segun rangos habituales por sexo."""
    clave = "male" if sex.lower() in ("male", "hombre", "m", "h") else "female"
    for umbral, etiqueta in _CATEGORIES[clave]:
        if body_fat_pct < umbral:
            return etiqueta
    return "elevado"


def estimate_body_fat(sex: str, height_cm: float, *,
                      neck_cm: Optional[float] = None,
                      waist_cm: Optional[float] = None,
                      hip_cm: Optional[float] = None,
                      weight_kg: Optional[float] = None,
                      age: Optional[int] = None) -> BodyFatEstimate:
    """Elige el mejor metodo disponible y devuelve la estimacion completa.

    Usa la formula Navy si hay circunferencias; si no, recurre al IMC (Deurenberg).
    """
    if neck_cm and waist_cm:
        bf = navy_body_fat(sex, height_cm, neck_cm, waist_cm, hip_cm)
        metodo = "navy"
        nota = "Estimacion por circunferencias (Navy). Margen tipico +/-3-4%."
    elif weight_kg and age:
        bf = deurenberg_body_fat(sex, weight_kg, height_cm, age)
        metodo = "bmi_deurenberg"
        nota = ("Estimacion por IMC (Deurenberg), menos precisa: no distingue "
                "musculo de grasa. Margen tipico +/-5%.")
    else:
        raise ValueError("Faltan datos: aporta cuello+cintura, o peso+edad")

    return BodyFatEstimate(
        body_fat_pct=bf,
        method=metodo,
        category=body_fat_category(bf, sex),
        confidence_note=nota,
    )
