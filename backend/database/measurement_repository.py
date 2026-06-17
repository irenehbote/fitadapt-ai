"""Repositorio de medidas corporales asociadas a un perfil."""
from __future__ import annotations

import sqlite3
from typing import List

from ..analytics.photo_progress import MeasurementSnapshot


class MeasurementRepository:
    """Guarda y recupera el historico de medidas de un perfil."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, profile_id: int, snapshot: MeasurementSnapshot,
            day_index: int) -> int:
        """Anade una medida y devuelve su id."""
        cur = self.conn.execute(
            """INSERT INTO measurements
               (profile_id, label, day_index, weight_kg, waist_cm, body_fat_pct)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (profile_id, snapshot.label, day_index, snapshot.weight_kg,
             snapshot.waist_cm, snapshot.body_fat_pct),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_for(self, profile_id: int) -> List[dict]:
        """Devuelve las medidas de un perfil ordenadas por day_index.

        Cada elemento incluye el snapshot y su day_index.
        """
        filas = self.conn.execute(
            "SELECT * FROM measurements WHERE profile_id = ? ORDER BY day_index",
            (profile_id,)).fetchall()
        return [
            {
                "snapshot": MeasurementSnapshot(
                    label=f["label"], weight_kg=f["weight_kg"],
                    waist_cm=f["waist_cm"], body_fat_pct=f["body_fat_pct"]),
                "day_index": f["day_index"],
            }
            for f in filas
        ]
