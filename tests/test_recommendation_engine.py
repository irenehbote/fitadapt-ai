"""Pruebas del motor de recomendacion semanal."""
import unittest

from backend.data.condition_rules import get_conditions
from backend.engine.recommendation_engine import (generate_recommendations,
                                                   weekly_hiit_limit)
from backend.engine.intensity_adapter import condition_hiit_limit
from backend.models.body_goal import BodyGoal
from backend.models.muscle_focus import MuscleFocus
from backend.models.user_profile import UserProfile


class TestRecommendationEngine(unittest.TestCase):
    def test_pcos_limita_hiit_a_3(self):
        perfil = UserProfile(name="A", age=30, conditions=get_conditions(["pcos"]))
        self.assertEqual(condition_hiit_limit(perfil), 3)
        # El plan final nunca debe superar 3 sesiones HIIT/semana.
        self.assertLessEqual(weekly_hiit_limit(perfil), 3)

    def test_cardiovascular_sin_hiit(self):
        perfil = UserProfile(name="B", age=60,
                             conditions=get_conditions(["cardiovascular_disease"]),
                             goal=BodyGoal.LOSE)
        self.assertEqual(condition_hiit_limit(perfil), 0)
        self.assertEqual(weekly_hiit_limit(perfil), 0)

    def test_enfoque_muscular_asigna_mas_volumen(self):
        focus = MuscleFocus.from_primary(["glutes", "quadriceps"])
        perfil = UserProfile(name="C", age=28, muscle_focus=focus)
        rec = generate_recommendations(perfil)
        volumen = rec.volume_allocation
        # Los musculos prioritarios reciben el maximo volumen.
        self.assertEqual(max(volumen.values()), volumen["glutes"])
        self.assertGreater(volumen["glutes"], volumen["calves"])

    def test_objetivo_perder_peso_cardio_3_a_4(self):
        perfil = UserProfile(name="D", age=40, goal=BodyGoal.LOSE)
        rec = generate_recommendations(perfil)
        self.assertEqual(rec.cardio_sessions_per_week, (3, 4))

    def test_recomendacion_completa_tiene_datos(self):
        perfil = UserProfile(name="E", age=33,
                             conditions=get_conditions(["pcos", "hypothyroidism"]),
                             available_environments=["home", "gym"],
                             available_equipment=["dumbbell", "mat", "none"])
        rec = generate_recommendations(perfil)
        self.assertTrue(len(rec.safe_exercises) > 0)
        self.assertTrue(len(rec.notes) >= 2)  # una nota por condicion
        self.assertTrue(1 <= rec.max_intensity_today <= 10)


if __name__ == "__main__":
    unittest.main()
