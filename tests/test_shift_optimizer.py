"""Pruebas de la optimizacion por turnos, horarios de gym y fatiga."""
import unittest

from backend.scheduling.shift_optimizer import (closing_soon,
                                               fatigue_adjusted_intensity_cap,
                                               fatigue_score,
                                               gym_available_for_slot,
                                               is_high_fatigue,
                                               optimal_workout_window)


class TestShiftOptimizer(unittest.TestCase):
    def test_fatiga_alta_tras_turnos_noche(self):
        score = fatigue_score(consecutive_work_days=4, night_shifts_this_week=3,
                              hours_slept_last_night=5, stress_level=6)
        self.assertEqual(score, 100)  # acotado a 100
        self.assertTrue(is_high_fatigue(score))

    def test_fatiga_baja_descansado(self):
        score = fatigue_score(consecutive_work_days=1, night_shifts_this_week=0,
                              hours_slept_last_night=8, stress_level=1)
        self.assertFalse(is_high_fatigue(score))

    def test_cap_intensidad_por_fatiga(self):
        self.assertEqual(fatigue_adjusted_intensity_cap(80), 6)   # fatiga alta
        self.assertEqual(fatigue_adjusted_intensity_cap(65), 8)   # moderada (~75%)
        self.assertEqual(fatigue_adjusted_intensity_cap(30), 10)  # sin cambios

    def test_gym_disponible(self):
        self.assertTrue(gym_available_for_slot(18, 19, 6, 22))
        self.assertFalse(gym_available_for_slot(21.5, 22.5, 6, 22))

    def test_gym_24h(self):
        self.assertTrue(gym_available_for_slot(3, 4, 0, 24))

    def test_cierra_pronto(self):
        # El gym cierra a las 22:00 y la franja acaba a las 21:30 (30 min antes).
        self.assertTrue(closing_soon(21.5, 22))
        self.assertFalse(closing_soon(19, 22))

    def test_ventana_optima_tras_despertar(self):
        self.assertEqual(optimal_workout_window(7), (11, 13))

    def test_franja_invalida(self):
        with self.assertRaises(ValueError):
            gym_available_for_slot(20, 18, 6, 22)


if __name__ == "__main__":
    unittest.main()
