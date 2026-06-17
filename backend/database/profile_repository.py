"""Repositorio de perfiles: guarda y reconstruye UserProfile desde SQLite."""
from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from ..data.condition_rules import get_conditions
from ..models.body_goal import BodyGoal
from ..models.muscle_focus import MuscleFocus
from ..models.user_profile import UserProfile


class ProfileRepository:
    """Operaciones CRUD sobre perfiles de usuario."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, profile: UserProfile) -> int:
        """Inserta un perfil y devuelve su id."""
        cur = self.conn.execute(
            """INSERT INTO profiles
               (name, age, goal, conditions, muscle_levels, environments, equipment)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                profile.name,
                profile.age,
                profile.goal.value,
                json.dumps(profile.condition_keys()),
                json.dumps(profile.muscle_focus.levels()),
                json.dumps(profile.available_environments),
                json.dumps(profile.available_equipment),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get(self, profile_id: int) -> Optional[UserProfile]:
        """Devuelve el perfil con ese id, o None si no existe."""
        row = self.conn.execute(
            "SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_profile(row)

    def list_all(self) -> List[dict]:
        """Lista resumida de perfiles (id, nombre, objetivo)."""
        filas = self.conn.execute(
            "SELECT id, name, goal FROM profiles ORDER BY id").fetchall()
        return [{"id": f["id"], "name": f["name"], "goal": f["goal"]} for f in filas]

    def delete(self, profile_id: int) -> bool:
        """Borra un perfil. Devuelve True si existia."""
        cur = self.conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        self.conn.commit()
        return cur.rowcount > 0

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> UserProfile:
        """Reconstruye un UserProfile a partir de una fila de la tabla."""
        return UserProfile(
            name=row["name"],
            age=row["age"],
            conditions=get_conditions(json.loads(row["conditions"])),
            goal=BodyGoal(row["goal"]),
            muscle_focus=MuscleFocus(json.loads(row["muscle_levels"])),
            available_environments=json.loads(row["environments"]),
            available_equipment=json.loads(row["equipment"]),
        )
