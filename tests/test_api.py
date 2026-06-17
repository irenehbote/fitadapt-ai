"""Pruebas de la API REST (a traves de la funcion de enrutado route())."""
import unittest

from backend.api.app import build_profile_from_dict, route


class TestApiRoute(unittest.TestCase):
    def test_health(self):
        status, body = route("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_conditions_incluye_pcos(self):
        status, body = route("GET", "/conditions")
        self.assertEqual(status, 200)
        claves = {c["key"] for c in body["conditions"]}
        self.assertIn("pcos", claves)

    def test_exercises_no_vacio(self):
        status, body = route("GET", "/exercises")
        self.assertEqual(status, 200)
        self.assertGreater(len(body["exercises"]), 0)

    def test_recommendations_cardiovascular_sin_hiit(self):
        payload = {"name": "Luis", "age": 64, "goal": "lose",
                   "conditions": ["cardiovascular_disease"],
                   "environments": ["gym"], "equipment": ["dumbbell", "none"]}
        status, body = route("POST", "/recommendations", payload)
        self.assertEqual(status, 200)
        self.assertEqual(body["weekly_hiit_limit"], 0)
        self.assertLessEqual(body["max_intensity_today"], 6)

    def test_recommendations_condicion_invalida_da_400(self):
        status, body = route("POST", "/recommendations", {"conditions": ["inventada"]})
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_objetivo_invalido_da_400(self):
        status, body = route("POST", "/recommendations", {"goal": "volar"})
        self.assertEqual(status, 400)

    def test_ruta_desconocida_da_404(self):
        status, body = route("GET", "/no-existe")
        self.assertEqual(status, 404)

    def test_build_profile_desde_dict(self):
        perfil = build_profile_from_dict({"name": "Ana", "age": 31, "goal": "gain",
                                          "muscle_focus": {"primary": ["glutes"]}})
        self.assertEqual(perfil.name, "Ana")
        self.assertEqual(perfil.muscle_focus.volume_allocation()["glutes"], 16)


if __name__ == "__main__":
    unittest.main()
