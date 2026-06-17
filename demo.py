"""Demostracion de FitAdapt AI.

Crea un par de perfiles de ejemplo y muestra como el motor adapta la
recomendacion a la salud, el objetivo y el entorno de cada persona.

Ejecuta:  python demo.py
"""
from backend.data.condition_rules import get_conditions
from backend.engine.intensity_adapter import WorkoutContext
from backend.engine.recommendation_engine import generate_recommendations
from backend.models.body_goal import BodyGoal
from backend.models.muscle_focus import MuscleFocus
from backend.models.user_profile import UserProfile


def mostrar(perfil: UserProfile, context: WorkoutContext | None = None) -> None:
    """Imprime por pantalla la recomendacion para un perfil."""
    rec = generate_recommendations(perfil, context=context)
    print("=" * 64)
    print(f"Usuario: {perfil.name} ({perfil.age} anios)")
    print(f"Objetivo: {perfil.goal.value}")
    if perfil.conditions:
        print("Condiciones: " + ", ".join(c.name for c in perfil.conditions))
    print(f"Entornos: {', '.join(perfil.available_environments)}")
    print("-" * 64)
    print(f"Cardio/semana:   {rec.cardio_sessions_per_week}")
    print(f"Fuerza/semana:   {rec.strength_sessions_per_week}")
    print(f"HIIT/semana max: {rec.weekly_hiit_limit}")
    print(f"Intensidad maxima hoy (1-10): {rec.max_intensity_today}")
    print(f"Ejercicios seguros disponibles: {len(rec.safe_exercises)}")
    ejemplos = ", ".join(e.name for e in rec.safe_exercises[:6])
    print(f"  p. ej.: {ejemplos}")
    top = sorted(rec.volume_allocation.items(), key=lambda kv: kv[1], reverse=True)[:3]
    print("Musculos con mas volumen: " +
          ", ".join(f"{m} ({v} series)" for m, v in top))
    if rec.notes:
        print("Notas de adaptacion:")
        for n in rec.notes:
            print(f"  - {n}")
    print()


def main() -> None:
    # Perfil 1: SOP, quiere perder peso, entrena en casa con mancuernas.
    ana = UserProfile(
        name="Ana", age=31,
        conditions=get_conditions(["pcos"]),
        goal=BodyGoal.LOSE,
        muscle_focus=MuscleFocus.from_primary(["glutes", "quadriceps"]),
        available_environments=["home"],
        available_equipment=["dumbbell", "mat", "resistance_band"],
    )
    mostrar(ana)

    # Perfil 2: enfermedad cardiovascular, mantener, ha dormido poco.
    luis = UserProfile(
        name="Luis", age=64,
        conditions=get_conditions(["cardiovascular_disease"]),
        goal=BodyGoal.MAINTAIN,
        available_environments=["gym", "outdoor"],
        available_equipment=["dumbbell", "bike", "rower", "none"],
    )
    mostrar(luis, context=WorkoutContext(sleep_hours=5))


if __name__ == "__main__":
    main()
