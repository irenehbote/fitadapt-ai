"""Pruebas de la adaptacion de intensidad segun salud y contexto."""
import unittest

from backend.data.condition_rules import get_conditions
from backend.engine.intensity_adapter import (WorkoutContext,
                                              adapt_exercise_intensity,
                                              condition_intensity_cap,
                                              max_allowed_intensity)
from backend.models.user_profile import UserProfile


class TestIntensityAdapter(unittest.TestCase):
    def test_fibromialgia_limita_intensidad(self):
        perfil = UserProfile(name="A", age=45,
                             conditions=get_conditions(["fibromyalgia"]))
        self.assertEqual(condition_intensity_cap(perfil), 5)
        self.assertEqual(max_allowed_intensity(perfil), 5)

    def test_cardiovascular_tope_6(self):
        perfil = UserProfile(name="B", age=62,
                             conditions=get_conditions(["cardiovascular_disease"]))
        self.assertEqual(max_allowed_intensity(perfil), 6)

    def test_dormir_poco_baja_al_60(self):
        sano = UserProfile(name="C", age=30)
        ctx = WorkoutContext(sleep_hours=5)
        self.assertEqual(max_allowed_intensity(sano, ctx), 6)

    def test_combina_salud_y_contexto(self):
        perfil = UserProfile(name="D", age=45,
                             conditions=get_conditions(["fibromyalgia"]))
        ctx = WorkoutContext(sleep_hours=5)
        # El tope mas estricto manda: fibromialgia (5) por debajo del 60% (6).
        self.assertEqual(max_allowed_intensity(perfil, ctx), 5)

    def test_turnos_noche_reducen_intensidad(self):
        sano = UserProfile(name="E", age=30)
        ctx = WorkoutContext(consecutive_night_shifts=3)
        self.assertEqual(max_allowed_intensity(sano, ctx), 8)

    def test_adaptar_intensidad_de_ejercicio(self):
        perfil = UserProfile(name="F", age=45,
                             conditions=get_conditions(["fibromyalgia"]))
        # Un ejercicio que puede llegar a 9 se recorta al tope seguro (5).
        self.assertEqual(adapt_exercise_intensity(9, perfil), 5)


if __name__ == "__main__":
    unittest.main()
