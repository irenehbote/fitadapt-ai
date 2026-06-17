"""Catalogo de ejercicios de FitAdapt AI.

Cada ejercicio esta etiquetado con su impacto articular, patron de movimiento,
entornos, equipamiento y condiciones para las que es bueno o esta contraindicado.
Esa informacion es la que permite al motor recomendar de forma segura.
"""
from __future__ import annotations

from typing import Dict, List

from ..models.exercise import Exercise


EXERCISES: List[Exercise] = [
    # --- Tren inferior: sentadilla ---
    Exercise("back_squat", "Sentadilla con barra", ["quadriceps", "glutes"],
             ["hamstrings", "core"], ["gym"], ["barbell", "squat_rack"],
             3, 9, "moderate", "squat", cardiovascular_demand="moderate",
             beneficial_for=["osteoporosis", "type2_diabetes"],
             contraindicated_conditions=["knee_osteoarthritis_severe"], base_xp=15),
    Exercise("goblet_squat", "Sentadilla goblet (mancuerna)", ["quadriceps", "glutes"],
             ["core"], ["home", "gym"], ["dumbbell"], 3, 7, "moderate", "squat",
             beneficial_for=["type2_diabetes"], base_xp=10),
    Exercise("bodyweight_squat", "Sentadilla con peso corporal", ["quadriceps", "glutes"],
             [], ["home", "outdoor"], ["none"], 2, 5, "low", "squat",
             beneficial_for=["osteoporosis"], base_xp=6),
    Exercise("lunge", "Zancada", ["quadriceps", "glutes"], ["hamstrings"],
             ["home", "outdoor", "gym"], ["none"], 3, 7, "moderate", "lunge", base_xp=9),
    # --- Tren inferior: bisagra de cadera ---
    Exercise("deadlift", "Peso muerto", ["glutes", "hamstrings", "back"], ["core"],
             ["gym"], ["barbell"], 4, 9, "moderate", "hinge",
             beneficial_for=["osteoporosis"], base_xp=16),
    Exercise("rdl_dumbbell", "Peso muerto rumano (mancuernas)", ["hamstrings", "glutes"],
             ["back"], ["home", "gym"], ["dumbbell"], 3, 7, "low", "hinge", base_xp=10),
    Exercise("hip_thrust", "Empuje de cadera", ["glutes"], ["hamstrings"],
             ["home", "gym"], ["none"], 3, 7, "low", "hinge", base_xp=10),
    # --- Empuje (push) ---
    Exercise("bench_press", "Press de banca", ["chest", "arms"], ["shoulders"],
             ["gym"], ["barbell", "bench"], 3, 9, "low", "push", base_xp=14),
    Exercise("push_up", "Flexiones", ["chest", "arms"], ["shoulders", "core"],
             ["home", "outdoor"], ["none"], 2, 7, "low", "push", base_xp=8),
    Exercise("overhead_press", "Press militar (mancuernas)", ["shoulders", "arms"],
             ["core"], ["home", "gym"], ["dumbbell"], 3, 8, "low", "push", base_xp=10),
    # --- Tiron (pull) ---
    Exercise("pull_up", "Dominadas", ["back", "arms"], ["core"],
             ["gym", "home", "outdoor"], ["pull_up_bar"], 4, 9, "low", "pull", base_xp=14),
    Exercise("lat_pulldown", "Jalon al pecho", ["back", "arms"], [],
             ["gym"], ["cable"], 3, 8, "low", "pull", base_xp=10),
    Exercise("band_row", "Remo con banda elastica", ["back", "arms"], [],
             ["home", "outdoor"], ["resistance_band"], 2, 6, "low", "pull", base_xp=7),
    Exercise("dumbbell_row", "Remo con mancuerna", ["back", "arms"], [],
             ["home", "gym"], ["dumbbell"], 3, 7, "low", "pull", base_xp=9),
    # --- Core ---
    Exercise("plank", "Plancha", ["core"], ["shoulders"],
             ["home", "outdoor", "gym"], ["none"], 2, 6, "low", "isometric_hold", base_xp=6),
    Exercise("crunch", "Abdominal clasico", ["core"], [],
             ["home", "gym"], ["none"], 2, 5, "low", "spinal_flexion",
             contraindicated_conditions=["osteoporosis"], base_xp=5),
    Exercise("hanging_leg_raise", "Elevacion de piernas en barra", ["core"], [],
             ["gym", "outdoor"], ["pull_up_bar"], 4, 7, "low", "core", base_xp=9),
    # --- Cardio ---
    Exercise("running", "Correr", ["cardio"], ["quadriceps"],
             ["outdoor", "gym"], ["none"], 4, 9, "high", "cardio",
             cardiovascular_demand="high", beneficial_for=["type2_diabetes"],
             contraindicated_conditions=["knee_osteoarthritis_severe"], base_xp=12),
    Exercise("walking", "Caminar", ["cardio"], [],
             ["outdoor", "home", "gym"], ["none"], 1, 4, "low", "cardio",
             cardiovascular_demand="moderate",
             beneficial_for=["pcos", "hypothyroidism", "fibromyalgia",
                             "cardiovascular_disease", "osteoporosis"], base_xp=5),
    Exercise("cycling", "Bicicleta", ["cardio", "quadriceps"], [],
             ["gym", "outdoor"], ["bike"], 3, 8, "low", "cardio",
             cardiovascular_demand="high", beneficial_for=["knee_osteoarthritis_severe"],
             base_xp=9),
    Exercise("rowing_machine", "Maquina de remo", ["cardio", "back"], ["quadriceps"],
             ["gym"], ["rower"], 4, 9, "low", "cardio", cardiovascular_demand="high",
             base_xp=12),
    Exercise("hiit_circuit", "Circuito HIIT", ["cardio"], ["quadriceps", "glutes"],
             ["home", "gym", "outdoor"], ["none"], 7, 10, "high", "cardio",
             is_hiit=True, cardiovascular_demand="high",
             contraindicated_conditions=["cardiovascular_disease", "osteoporosis"],
             base_xp=18),
    Exercise("box_jump", "Salto al cajon", ["quadriceps", "glutes"], ["calves"],
             ["gym", "outdoor"], ["box"], 6, 9, "high", "jump",
             cardiovascular_demand="high",
             contraindicated_conditions=["osteoporosis", "knee_osteoarthritis_severe"],
             base_xp=14),
    # --- Aislamiento y movilidad ---
    Exercise("calf_raise", "Elevacion de gemelos", ["calves"], [],
             ["home", "gym"], ["none"], 2, 5, "low", "isolation", base_xp=4),
    Exercise("bicep_curl", "Curl de biceps", ["arms"], [],
             ["home", "gym"], ["dumbbell"], 2, 6, "low", "isolation", base_xp=5),
    Exercise("yoga_flow", "Secuencia de yoga", ["core"], ["full_body"],
             ["home", "outdoor"], ["mat"], 2, 5, "low", "mobility",
             beneficial_for=["pcos", "fibromyalgia", "hypothyroidism"], base_xp=7),
]


# Indice por id para buscar rapido.
EXERCISES_BY_ID: Dict[str, Exercise] = {e.id: e for e in EXERCISES}
