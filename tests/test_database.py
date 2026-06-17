"""Pruebas de la persistencia en SQLite (perfiles y medidas)."""
import unittest

from backend.analytics.photo_progress import MeasurementSnapshot
from backend.data.condition_rules import get_conditions
from backend.database.db import connect, init_db
from backend.database.measurement_repository import MeasurementRepository
from backend.database.profile_repository import ProfileRepository
from backend.models.body_goal import BodyGoal
from backend.models.muscle_focus import MuscleFocus
from backend.models.user_profile import UserProfile


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Base de datos en memoria, nueva en cada prueba.
        self.conn = connect(":memory:")
        init_db(self.conn)
        self.profiles = ProfileRepository(self.conn)
        self.measurements = MeasurementRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _perfil(self):
        return UserProfile(
            name="Ana", age=31,
            conditions=get_conditions(["pcos"]),
            goal=BodyGoal.LOSE,
            muscle_focus=MuscleFocus.from_primary(["glutes", "quadriceps"]),
            available_environments=["home"],
            available_equipment=["dumbbell", "mat"],
        )

    def test_crear_y_recuperar_perfil(self):
        pid = self.profiles.create(self._perfil())
        recuperado = self.profiles.get(pid)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.name, "Ana")
        self.assertEqual(recuperado.goal, BodyGoal.LOSE)
        self.assertEqual(recuperado.condition_keys(), ["pcos"])
        # El enfoque muscular se restaura igual.
        self.assertEqual(recuperado.muscle_focus.volume_allocation()["glutes"], 16)

    def test_listar_perfiles(self):
        self.profiles.create(self._perfil())
        self.profiles.create(self._perfil())
        self.assertEqual(len(self.profiles.list_all()), 2)

    def test_perfil_inexistente(self):
        self.assertIsNone(self.profiles.get(999))

    def test_borrar_perfil(self):
        pid = self.profiles.create(self._perfil())
        self.assertTrue(self.profiles.delete(pid))
        self.assertIsNone(self.profiles.get(pid))
        self.assertFalse(self.profiles.delete(pid))  # ya no existe

    def test_medidas_se_guardan_ordenadas(self):
        pid = self.profiles.create(self._perfil())
        self.measurements.add(pid, MeasurementSnapshot("12 sem", 76, 85), day_index=84)
        self.measurements.add(pid, MeasurementSnapshot("inicio", 80, 90), day_index=0)
        historico = self.measurements.list_for(pid)
        self.assertEqual(len(historico), 2)
        # Vienen ordenadas por day_index ascendente.
        self.assertEqual(historico[0]["day_index"], 0)
        self.assertEqual(historico[0]["snapshot"].weight_kg, 80)

    def test_borrar_perfil_borra_sus_medidas(self):
        pid = self.profiles.create(self._perfil())
        self.measurements.add(pid, MeasurementSnapshot("a", 80, 90), day_index=0)
        self.profiles.delete(pid)
        self.assertEqual(self.measurements.list_for(pid), [])


if __name__ == "__main__":
    unittest.main()
