"""Enfoque muscular: a que musculos quiere dar prioridad el usuario.

El usuario marca cada grupo muscular con un nivel de prioridad. A partir de eso
repartimos el volumen semanal de entrenamiento (medido en "series efectivas por
musculo y semana"). Mas prioridad => mas series.
"""
from __future__ import annotations

from typing import Dict, Iterable


# Grupos musculares que maneja el sistema.
MUSCLE_GROUPS = (
    "quadriceps", "glutes", "hamstrings", "chest", "back",
    "shoulders", "arms", "core", "calves",
)

# Niveles de prioridad y las series semanales que les asignamos.
PRIORITY_VOLUME = {
    "primary": 16,      # Foco principal: 14-20 series/semana
    "secondary": 10,    # Foco secundario: 8-12 series/semana
    "maintenance": 5,   # Solo mantenimiento: 4-8 series/semana
}


class MuscleFocus:
    """Seleccion de prioridades musculares del usuario.

    Cualquier musculo no asignado se considera "maintenance" por defecto, para
    que el plan siempre sea equilibrado y no descuide ninguna zona.
    """

    def __init__(self, levels: Dict[str, str] | None = None):
        # Empezamos con todos los musculos en "mantenimiento".
        self._levels: Dict[str, str] = {m: "maintenance" for m in MUSCLE_GROUPS}
        if levels:
            for muscle, level in levels.items():
                self.set_level(muscle, level)

    def set_level(self, muscle: str, level: str) -> None:
        """Asigna un nivel de prioridad a un musculo."""
        if muscle not in MUSCLE_GROUPS:
            raise ValueError(f"Grupo muscular desconocido: {muscle}")
        if level not in PRIORITY_VOLUME:
            raise ValueError(f"Nivel de prioridad desconocido: {level}")
        self._levels[muscle] = level

    def volume_allocation(self) -> Dict[str, int]:
        """Devuelve las series semanales asignadas a cada musculo."""
        return {m: PRIORITY_VOLUME[level] for m, level in self._levels.items()}

    def levels(self) -> Dict[str, str]:
        """Devuelve una copia de los niveles por musculo (para persistir/restaurar)."""
        return dict(self._levels)

    def muscles_with_level(self, level: str) -> list:
        """Devuelve los musculos que tienen el nivel de prioridad indicado."""
        return [m for m, lvl in self._levels.items() if lvl == level]

    @classmethod
    def from_primary(cls, primary: Iterable[str], secondary: Iterable[str] = ()):
        """Atajo: crea un enfoque marcando musculos como primarios/secundarios."""
        levels = {}
        for m in primary:
            levels[m] = "primary"
        for m in secondary:
            levels[m] = "secondary"
        return cls(levels)
