"""Pruebas de la adaptacion hormonal por fase del ciclo."""
import unittest

from backend.data.condition_rules import get_conditions
from backend.engine.hormonal_adapter import (CyclePhase, hormonal_intensity_factor,
                                             hormonal_notes, phase_for_day)
from backend.models.user_profile import UserProfile


class TestHormonalAdapter(unittest.TestCase):
    def test_fases_por_dia(self):
        self.assertEqual(phase_for_day(2), CyclePhase.MENSTRUAL)
        self.assertEqual(phase_for_day(9), CyclePhase.FOLLICULAR)
        self.assertEqual(phase_for_day(14), CyclePhase.OVULATION)
        self.assertEqual(phase_for_day(22), CyclePhase.LUTEAL)

    def test_dia_invalido(self):
        with self.assertRaises(ValueError):
            phase_for_day(40)

    def test_factor_lutea_menor_que_folicular(self):
        sana = UserProfile(name="A", age=30)
        self.assertLess(hormonal_intensity_factor(sana, 22),
                        hormonal_intensity_factor(sana, 9))

    def test_pcos_reduce_mas_en_lutea(self):
        sana = UserProfile(name="A", age=30)
        sop = UserProfile(name="B", age=30, conditions=get_conditions(["pcos"]))
        # En fase lutea, el SOP reduce un 15% adicional.
        self.assertLess(hormonal_intensity_factor(sop, 22),
                        hormonal_intensity_factor(sana, 22))

    def test_factor_en_rango(self):
        sop = UserProfile(name="B", age=30, conditions=get_conditions(["pcos"]))
        for dia in range(1, 29):
            f = hormonal_intensity_factor(sop, dia)
            self.assertTrue(0 < f <= 1.0)

    def test_notas_incluyen_fase(self):
        sop = UserProfile(name="B", age=30, conditions=get_conditions(["pcos"]))
        notas = hormonal_notes(sop, 22)
        self.assertTrue(any("lutea" in n.lower() for n in notas))
        self.assertTrue(any("SOP" in n for n in notas))


if __name__ == "__main__":
    unittest.main()
