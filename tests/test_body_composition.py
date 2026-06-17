"""Pruebas de la estimacion de grasa corporal por medidas."""
import unittest

from backend.analytics.body_composition import (body_fat_category,
                                               deurenberg_body_fat,
                                               estimate_body_fat, navy_body_fat)


class TestBodyComposition(unittest.TestCase):
    def test_navy_hombre(self):
        # Hombre 180 cm, cuello 38, cintura 85 -> ~16% (valor conocido de la formula).
        bf = navy_body_fat("male", 180, 38, 85)
        self.assertAlmostEqual(bf, 16.1, delta=0.5)

    def test_navy_mujer(self):
        # Mujer 165 cm, cuello 34, cintura 75, cadera 95 -> ~26%.
        bf = navy_body_fat("female", 165, 34, 75, hip_cm=95)
        self.assertAlmostEqual(bf, 26.4, delta=0.6)

    def test_navy_mujer_requiere_cadera(self):
        with self.assertRaises(ValueError):
            navy_body_fat("female", 165, 34, 75)

    def test_navy_cintura_menor_que_cuello(self):
        with self.assertRaises(ValueError):
            navy_body_fat("male", 180, 40, 38)

    def test_deurenberg(self):
        # Comprobacion de coherencia: mas peso a igual altura/edad => mas grasa.
        bajo = deurenberg_body_fat("male", 70, 180, 30)
        alto = deurenberg_body_fat("male", 95, 180, 30)
        self.assertGreater(alto, bajo)

    def test_categoria(self):
        self.assertEqual(body_fat_category(10, "male"), "atletico")
        self.assertEqual(body_fat_category(35, "female"), "elevado")

    def test_estimate_elige_navy(self):
        est = estimate_body_fat("male", 180, neck_cm=38, waist_cm=85)
        self.assertEqual(est.method, "navy")
        self.assertTrue(0 < est.body_fat_pct < 60)
        self.assertTrue(est.category)

    def test_estimate_fallback_bmi(self):
        est = estimate_body_fat("male", 180, weight_kg=80, age=30)
        self.assertEqual(est.method, "bmi_deurenberg")

    def test_estimate_sin_datos(self):
        with self.assertRaises(ValueError):
            estimate_body_fat("male", 180)


if __name__ == "__main__":
    unittest.main()
