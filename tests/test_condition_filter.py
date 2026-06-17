"""Pruebas del filtrado de ejercicios por condiciones de salud."""
import unittest

from backend.data.condition_rules import get_conditions
from backend.data.exercises import EXERCISES
from backend.engine.condition_filter import filter_exercises, is_safe
from backend.models.body_goal import BodyGoal
from backend.models.user_profile import UserProfile


def _perfil(condition_keys):
    """Crea un perfil con acceso a todo (entornos y equipamiento) salvo la salud."""
    return UserProfile(
        name="Test", age=35,
        conditions=get_conditions(condition_keys),
        goal=BodyGoal.MAINTAIN,
        available_environments=["gym", "home", "outdoor"],
        available_equipment=["barbell", "squat_rack", "dumbbell", "bench", "cable",
                             "pull_up_bar", "resistance_band", "box", "bike",
                             "rower", "mat"],
    )


class TestConditionFilter(unittest.TestCase):
    def test_artrosis_rodilla_sin_alto_impacto(self):
        perfil = _perfil(["knee_osteoarthritis_severe"])
        seguros = filter_exercises(EXERCISES, perfil, require_available=False)
        # Ningun ejercicio seguro debe ser de alto impacto articular.
        self.assertTrue(all(e.joint_impact != "high" for e in seguros))
        ids = {e.id for e in seguros}
        self.assertNotIn("running", ids)      # alto impacto
        self.assertNotIn("back_squat", ids)   # contraindicado explicitamente
        self.assertIn("cycling", ids)         # bajo impacto, sí permitido

    def test_osteoporosis_sin_flexion_columna_ni_saltos(self):
        perfil = _perfil(["osteoporosis"])
        seguros = filter_exercises(EXERCISES, perfil, require_available=False)
        ids = {e.id for e in seguros}
        self.assertNotIn("crunch", ids)     # flexion de columna
        self.assertNotIn("box_jump", ids)   # salto
        self.assertNotIn("hiit_circuit", ids)
        self.assertTrue(all(e.joint_impact != "high" for e in seguros))

    def test_usuario_sano_tiene_ejercicios(self):
        perfil = _perfil([])
        seguros = filter_exercises(EXERCISES, perfil, require_available=False)
        # Sin condiciones, todo el catalogo es seguro.
        self.assertEqual(len(seguros), len(EXERCISES))

    def test_disponibilidad_por_equipamiento(self):
        # Usuario solo en casa y sin equipamiento: no puede usar la barra.
        perfil = UserProfile(name="Casa", age=30,
                             available_environments=["home"],
                             available_equipment=["none"])
        seguros = filter_exercises(EXERCISES, perfil)
        ids = {e.id for e in seguros}
        self.assertIn("push_up", ids)        # peso corporal en casa
        self.assertNotIn("back_squat", ids)  # necesita barra y gimnasio

    def test_is_safe_coherente(self):
        perfil = _perfil(["cardiovascular_disease"])
        plank = next(e for e in EXERCISES if e.id == "plank")
        # La plancha es isometrico sostenido: contraindicado en cardiovascular.
        self.assertFalse(is_safe(plank, perfil))


if __name__ == "__main__":
    unittest.main()
