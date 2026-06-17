"""Reto 1v1 opcional entre dos personas.

Diseno deliberado: la gamificacion SOLO esta activa dentro de un reto aceptado.
No hay XP pasivo ni ranking siempre visible: la app es, ante todo, una
herramienta privada. El reto es un anadido social que se elige activar.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Optional


class ChallengeStatus(Enum):
    """Estados posibles de un reto."""

    PENDING = "pending"     # Esperando que el oponente acepte
    ACTIVE = "active"       # En curso
    DECLINED = "declined"   # Rechazado (sin verguenza por declinar)
    FINISHED = "finished"   # Terminado


class Challenge:
    """Reto 1v1 entre 'challenger' (quien invita) y 'opponent' (invitado)."""

    def __init__(self, challenger: str, opponent: str, duration_days: int = 7):
        if duration_days <= 0:
            raise ValueError("La duracion debe ser positiva")
        self.challenger = challenger
        self.opponent = opponent
        self.duration_days = duration_days
        self.status = ChallengeStatus.PENDING
        self._xp: Dict[str, float] = {challenger: 0.0, opponent: 0.0}

    def accept(self) -> None:
        """El oponente acepta: el reto comienza."""
        if self.status != ChallengeStatus.PENDING:
            raise ValueError("Solo se puede aceptar un reto pendiente")
        self.status = ChallengeStatus.ACTIVE

    def decline(self) -> None:
        """El oponente declina: no pasa nada, el reto se cierra."""
        if self.status != ChallengeStatus.PENDING:
            raise ValueError("Solo se puede declinar un reto pendiente")
        self.status = ChallengeStatus.DECLINED

    def add_xp(self, participant: str, amount: float) -> None:
        """Suma XP a un participante. Solo cuenta con el reto ACTIVO."""
        if self.status != ChallengeStatus.ACTIVE:
            raise ValueError("Solo se puntua durante un reto activo")
        if participant not in self._xp:
            raise ValueError(f"{participant} no participa en este reto")
        self._xp[participant] += amount

    def scores(self) -> Dict[str, float]:
        """Devuelve el marcador actual (solo visible para los dos jugadores)."""
        return dict(self._xp)

    def finish(self) -> Optional[str]:
        """Cierra el reto y devuelve el ganador (None si hay empate)."""
        if self.status not in (ChallengeStatus.ACTIVE, ChallengeStatus.FINISHED):
            raise ValueError("Solo se puede finalizar un reto activo")
        self.status = ChallengeStatus.FINISHED
        a, b = self.challenger, self.opponent
        if self._xp[a] > self._xp[b]:
            return a
        if self._xp[b] > self._xp[a]:
            return b
        return None
