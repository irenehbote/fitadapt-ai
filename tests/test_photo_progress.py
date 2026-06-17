"""Pruebas del informe de progreso corporal."""
import unittest

from backend.analytics.photo_progress import (MeasurementSnapshot,
                                              estimate_body_fat_from_image,
                                              generate_progress_report)
from backend.data.condition_rules import get_condition


class TestPhotoProgress(unittest.TestCase):
    def test_informe_perdida_peso(self):
        antes = MeasurementSnapshot("inicio", weight_kg=80, waist_cm=90, body_fat_pct=28)
        despues = MeasurementSnapshot("12 sem", weight_kg=76, waist_cm=85, body_fat_pct=25)
        r = generate_progress_report(antes, despues, days_between=84)
        self.assertLess(r.weight_change_pct, 0)      # ha bajado de peso
        self.assertEqual(r.waist_change_cm, -5.0)
        self.assertEqual(r.body_fat_change, -3.0)
        self.assertTrue(r.plausible)                 # ~0.33 kg/sem, normal

    def test_cambio_inverosimil_se_marca(self):
        antes = MeasurementSnapshot("a", weight_kg=80, waist_cm=90)
        despues = MeasurementSnapshot("b", weight_kg=68, waist_cm=80)  # -12 kg
        r = generate_progress_report(antes, despues, days_between=7)
        self.assertFalse(r.plausible)
        self.assertTrue(any("inusualmente" in c.lower() for c in r.commentary))

    def test_contexto_por_condicion(self):
        antes = MeasurementSnapshot("a", weight_kg=80, waist_cm=90)
        despues = MeasurementSnapshot("b", weight_kg=78, waist_cm=88)
        hipo = get_condition("hypothyroidism")
        r = generate_progress_report(antes, despues, days_between=56, condition=hipo)
        self.assertTrue(any("NORMAL" in c for c in r.commentary))

    def test_dias_invalidos(self):
        antes = MeasurementSnapshot("a", weight_kg=80, waist_cm=90)
        despues = MeasurementSnapshot("b", weight_kg=79, waist_cm=89)
        with self.assertRaises(ValueError):
            generate_progress_report(antes, despues, days_between=0)

    def test_estimacion_por_imagen_no_implementada(self):
        # Es honesto: no inventamos un % de grasa a partir de una foto.
        with self.assertRaises(NotImplementedError):
            estimate_body_fat_from_image(b"datos")


if __name__ == "__main__":
    unittest.main()
