"""Pruebas de la sustitucion de ejercicios entre entornos."""
import unittest

from backend.data.exercises import EXERCISES_BY_ID
from backend.engine.environment_adapter import adapt_plan, substitute_exercise
from backend.models.user_profile import UserProfile


class TestEnvironmentAdapter(unittest.TestCase):
    def setUp(self):
        # Usuario que entrena en casa con mancuernas y esterilla.
        self.casa = UserProfile(name="Casa", age=30,
                                available_environments=["home"],
                                available_equipment=["dumbbell", "mat"])

    def test_sustituye_sentadilla_de_gym(self):
        back_squat = EXERCISES_BY_ID["back_squat"]  # solo gimnasio + barra
        sub = substitute_exercise(back_squat, self.casa)
        self.assertIsNotNone(sub)
        self.assertNotEqual(sub.id, "back_squat")
        # La alternativa mantiene el patron de sentadilla y trabaja la misma zona.
        self.assertEqual(sub.movement_pattern, "squat")
        self.assertTrue(set(sub.primary_muscles) & {"quadriceps", "glutes"})
        # Y, claro, debe ser realizable en casa.
        self.assertIn("home", sub.environments)

    def test_no_cambia_si_ya_es_disponible(self):
        goblet = EXERCISES_BY_ID["goblet_squat"]  # casa + mancuerna
        sub = substitute_exercise(goblet, self.casa)
        self.assertEqual(sub.id, "goblet_squat")

    def test_adapt_plan_marca_cambios(self):
        plan = [EXERCISES_BY_ID["back_squat"], EXERCISES_BY_ID["goblet_squat"]]
        resultado = adapt_plan(plan, self.casa)
        self.assertTrue(resultado[0].changed)       # back_squat se sustituye
        self.assertFalse(resultado[1].changed)      # goblet_squat se mantiene
        for s in resultado:
            self.assertIsNotNone(s.resolved)

    def test_alternativa_es_segura_y_disponible(self):
        from backend.engine.condition_filter import is_available, is_safe
        bench = EXERCISES_BY_ID["bench_press"]  # gym + barra + banco
        sub = substitute_exercise(bench, self.casa)
        self.assertIsNotNone(sub)
        self.assertTrue(is_available(sub, self.casa))
        self.assertTrue(is_safe(sub, self.casa))


if __name__ == "__main__":
    unittest.main()
