"""Conexion a la base de datos SQLite y creacion del esquema.

Usamos SQLite (incluido en Python) para no anadir dependencias. Una sola
conexion basta porque el servidor HTTP atiende las peticiones de una en una.
"""
from __future__ import annotations

import sqlite3

# Nombre del fichero de base de datos por defecto (en la raiz del repo).
DEFAULT_DB = "fitadapt.db"

# Esquema: perfiles y su historico de medidas.
SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    age             INTEGER NOT NULL,
    goal            TEXT NOT NULL,
    conditions      TEXT NOT NULL,   -- JSON: lista de claves de condiciones
    muscle_levels   TEXT NOT NULL,   -- JSON: {musculo: nivel}
    environments    TEXT NOT NULL,   -- JSON: lista
    equipment       TEXT NOT NULL    -- JSON: lista
);

CREATE TABLE IF NOT EXISTS measurements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id   INTEGER NOT NULL,
    label        TEXT NOT NULL,
    day_index    INTEGER NOT NULL,   -- dias desde la primera medida
    weight_kg    REAL NOT NULL,
    waist_cm     REAL NOT NULL,
    body_fat_pct REAL,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
"""


def connect(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    """Abre una conexion SQLite con claves foraneas activadas y filas tipo dict."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Crea las tablas si no existen."""
    conn.executescript(SCHEMA)
    conn.commit()
