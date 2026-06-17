"""Pruebas de la integracion con Google Fit (logica de influencia y normalizacion)."""
import unittest

from backend.integrations.google_fit import (GoogleFitClient, HealthData,
                                             recommend_adjustments)


class TestGoogleFit(unittest.TestCase):
    def test_dormir_poco_limita_intensidad(self):
        adj = recommend_adjustments(HealthData(sleep_hours_last_night=5))
        self.assertEqual(adj.intensity_cap, 6)
        self.assertTrue(adj.notes)

    def test_muchos_pasos_reduce_cardio(self):
        adj = recommend_adjustments(HealthData(steps_today=12000))
        self.assertTrue(adj.reduce_cardio)

    def test_fc_reposo_al_alza_sugiere_descarga(self):
        adj = recommend_adjustments(HealthData(resting_hr_trend="increasing"))
        self.assertTrue(adj.suggest_deload)

    def test_sin_datos_no_cambia_nada(self):
        adj = recommend_adjustments(HealthData())
        self.assertEqual(adj.intensity_cap, 10)
        self.assertFalse(adj.reduce_cardio)
        self.assertFalse(adj.suggest_deload)

    def test_normalize_convierte_payload(self):
        raw = {"steps": 8000, "sleep_minutes": 420, "resting_hr_trend": "stable"}
        data = GoogleFitClient.normalize(raw)
        self.assertEqual(data.steps_today, 8000)
        self.assertEqual(data.sleep_hours_last_night, 7.0)  # 420 min = 7 h
        self.assertEqual(data.resting_hr_trend, "stable")

    def test_conexion_real_no_implementada(self):
        cliente = GoogleFitClient()
        with self.assertRaises(NotImplementedError):
            cliente.connect()


if __name__ == "__main__":
    unittest.main()
