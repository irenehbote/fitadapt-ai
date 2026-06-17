"""Pruebas de la analitica de progreso corporal."""
import unittest

from backend.analytics.body_stats import (linear_trend, moving_average,
                                          percent_change, progress_score)
from backend.data.condition_rules import get_condition


class TestBodyStats(unittest.TestCase):
    def test_percent_change(self):
        self.assertAlmostEqual(percent_change(80, 72), -10.0)

    def test_linear_trend_negativa(self):
        # Peso que baja: pendiente negativa.
        self.assertLess(linear_trend([80, 79, 78, 77]), 0)

    def test_moving_average(self):
        self.assertEqual(moving_average([1, 2, 3, 4], 2), [1.5, 2.5, 3.5])

    def test_moving_average_ventana_grande(self):
        self.assertEqual(moving_average([1, 2], 5), [])

    def test_progress_score_perdida_normal(self):
        # Una perdida del 10% sin condicion equivale a "progreso completo".
        self.assertEqual(progress_score([80, 72]), 100.0)

    def test_progress_score_ajusta_por_condicion(self):
        valores = [80, 77.5]  # perdida del ~3.1%
        sin_condicion = progress_score(valores)
        con_hipo = progress_score(valores, condition=get_condition("hypothyroidism"))
        # Con hipotiroidismo el mismo avance puntua mas alto (expectativa menor).
        self.assertGreater(con_hipo, sin_condicion)

    def test_linear_trend_requiere_dos_valores(self):
        with self.assertRaises(ValueError):
            linear_trend([1])


if __name__ == "__main__":
    unittest.main()
