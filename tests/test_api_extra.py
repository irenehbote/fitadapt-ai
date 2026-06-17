"""Pruebas de los endpoints de modulos y de persistencia de la API."""
import unittest

from backend.api.app import make_context, route
from backend.database.db import connect, init_db


class TestModuleEndpoints(unittest.TestCase):
    def test_hormonal(self):
        status, body = route("POST", "/hormonal",
                             {"conditions": ["pcos"], "cycle_day": 22})
        self.assertEqual(status, 200)
        self.assertEqual(body["phase"], "luteal")
        self.assertLess(body["intensity_factor"], 1.0)

    def test_fatigue(self):
        status, body = route("POST", "/fatigue",
                             {"consecutive_work_days": 5, "night_shifts_this_week": 3,
                              "hours_slept_last_night": 5, "stress_level": 6})
        self.assertEqual(status, 200)
        self.assertTrue(body["high_fatigue"])

    def test_google_fit(self):
        status, body = route("POST", "/google-fit", {"sleep_hours_last_night": 5})
        self.assertEqual(status, 200)
        self.assertEqual(body["intensity_cap"], 6)

    def test_xp_y_error(self):
        status, body = route("POST", "/xp",
                             {"exercise_id": "goblet_squat", "intensity": 6,
                              "streak_days": 3, "conditions": ["pcos"]})
        self.assertEqual(status, 200)
        self.assertGreater(body["xp"], 0)
        status, _ = route("POST", "/xp", {"exercise_id": "no-existe"})
        self.assertEqual(status, 400)

    def test_substitute(self):
        status, body = route("POST", "/substitute",
                             {"exercise_id": "back_squat", "environments": ["home"],
                              "equipment": ["dumbbell"]})
        self.assertEqual(status, 200)
        self.assertTrue(body["changed"])
        self.assertIsNotNone(body["resolved"])

    def test_progress(self):
        status, body = route("POST", "/progress", {
            "before": {"label": "a", "weight_kg": 80, "waist_cm": 90},
            "after": {"label": "b", "weight_kg": 76, "waist_cm": 85},
            "days_between": 84, "condition": "hypothyroidism"})
        self.assertEqual(status, 200)
        self.assertLess(body["weight_change_pct"], 0)


class TestPersistenceEndpoints(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        init_db(self.conn)
        self.ctx = make_context(self.conn)

    def tearDown(self):
        self.conn.close()

    def _crear(self):
        status, body = route("POST", "/profiles", {
            "name": "Ana", "age": 31, "goal": "lose", "conditions": ["pcos"],
            "muscle_focus": {"primary": ["glutes"]}, "environments": ["home"],
            "equipment": ["dumbbell", "mat"]}, ctx=self.ctx)
        self.assertEqual(status, 201)
        return body["id"]

    def test_sin_contexto_da_503(self):
        status, _ = route("GET", "/profiles")  # sin ctx
        self.assertEqual(status, 503)

    def test_crear_listar_obtener(self):
        pid = self._crear()
        status, lista = route("GET", "/profiles", ctx=self.ctx)
        self.assertEqual(status, 200)
        self.assertEqual(len(lista["profiles"]), 1)
        status, perfil = route("GET", f"/profiles/{pid}", ctx=self.ctx)
        self.assertEqual(status, 200)
        self.assertEqual(perfil["name"], "Ana")

    def test_recommendation_de_perfil_guardado(self):
        pid = self._crear()
        status, rec = route("GET", f"/profiles/{pid}/recommendation", ctx=self.ctx)
        self.assertEqual(status, 200)
        self.assertEqual(rec["volume_allocation"]["glutes"], 16)

    def test_medidas_y_progreso(self):
        pid = self._crear()
        route("POST", f"/profiles/{pid}/measurements",
              {"label": "inicio", "day_index": 0, "weight_kg": 80, "waist_cm": 90},
              ctx=self.ctx)
        route("POST", f"/profiles/{pid}/measurements",
              {"label": "12 sem", "day_index": 84, "weight_kg": 76, "waist_cm": 85},
              ctx=self.ctx)
        status, prog = route("GET", f"/profiles/{pid}/progress", ctx=self.ctx)
        self.assertEqual(status, 200)
        self.assertLess(prog["weight_change_pct"], 0)

    def test_progreso_sin_medidas_suficientes(self):
        pid = self._crear()
        status, _ = route("GET", f"/profiles/{pid}/progress", ctx=self.ctx)
        self.assertEqual(status, 400)

    def test_borrar(self):
        pid = self._crear()
        status, _ = route("DELETE", f"/profiles/{pid}", ctx=self.ctx)
        self.assertEqual(status, 200)
        status, _ = route("GET", f"/profiles/{pid}", ctx=self.ctx)
        self.assertEqual(status, 404)

    def test_perfil_inexistente_da_404(self):
        status, _ = route("GET", "/profiles/999", ctx=self.ctx)
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
