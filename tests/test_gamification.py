"""Pruebas de la gamificacion: puntuacion justa y retos 1v1."""
import unittest

from backend.data.condition_rules import get_conditions
from backend.data.exercises import EXERCISES_BY_ID
from backend.gamification.challenge import Challenge, ChallengeStatus
from backend.gamification.fair_scoring import (consistency_bonus, exercise_xp,
                                              intensity_multiplier)
from backend.models.user_profile import UserProfile


class TestFairScoring(unittest.TestCase):
    def test_multiplicador_intensidad(self):
        self.assertEqual(intensity_multiplier(1), 0.5)
        self.assertEqual(intensity_multiplier(10), 2.0)
        self.assertLess(intensity_multiplier(3), intensity_multiplier(8))

    def test_bonus_consistencia_con_tope(self):
        self.assertEqual(consistency_bonus(0), 1.0)
        self.assertEqual(consistency_bonus(5), 1.5)
        self.assertEqual(consistency_bonus(50), 2.0)  # tope

    def test_handicap_justo_por_condicion(self):
        ex = EXERCISES_BY_ID["goblet_squat"]
        sin = UserProfile(name="Sin", age=30)
        con = UserProfile(name="Con", age=30, conditions=get_conditions(["pcos"]))
        xp_sin = exercise_xp(ex, intensity=6, streak_days=3, profile=sin)
        xp_con = exercise_xp(ex, intensity=6, streak_days=3, profile=con)
        # El SOP da un multiplicador 1.2x: el mismo esfuerzo puntua mas.
        self.assertGreater(xp_con, xp_sin)

    def test_intensidad_invalida(self):
        with self.assertRaises(ValueError):
            intensity_multiplier(11)


class TestChallenge(unittest.TestCase):
    def test_flujo_aceptar_y_ganar(self):
        reto = Challenge("Ana", "Luis", duration_days=7)
        self.assertEqual(reto.status, ChallengeStatus.PENDING)
        reto.accept()
        self.assertEqual(reto.status, ChallengeStatus.ACTIVE)
        reto.add_xp("Ana", 120)
        reto.add_xp("Luis", 90)
        ganador = reto.finish()
        self.assertEqual(ganador, "Ana")
        self.assertEqual(reto.status, ChallengeStatus.FINISHED)

    def test_no_puntua_si_no_esta_activo(self):
        reto = Challenge("Ana", "Luis")
        with self.assertRaises(ValueError):
            reto.add_xp("Ana", 10)  # sigue PENDING

    def test_declinar_sin_problema(self):
        reto = Challenge("Ana", "Luis")
        reto.decline()
        self.assertEqual(reto.status, ChallengeStatus.DECLINED)

    def test_empate(self):
        reto = Challenge("Ana", "Luis")
        reto.accept()
        reto.add_xp("Ana", 50)
        reto.add_xp("Luis", 50)
        self.assertIsNone(reto.finish())

    def test_participante_desconocido(self):
        reto = Challenge("Ana", "Luis")
        reto.accept()
        with self.assertRaises(ValueError):
            reto.add_xp("Pedro", 10)


if __name__ == "__main__":
    unittest.main()
