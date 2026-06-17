"""Pruebas del pipeline de vision.

Lo que necesita el modelo descargado se salta automaticamente si no esta presente.
"""
import unittest

from backend.vision import body_measure
from backend.vision.body_measure import NoPersonDetectedError, VisionUnavailableError

VISION = body_measure.is_available()
MODEL = body_measure.model_available()


class TestVisionAvailability(unittest.TestCase):
    def test_is_available_es_booleano(self):
        self.assertIsInstance(body_measure.is_available(), bool)

    @unittest.skipUnless(VISION, "mediapipe no instalado")
    @unittest.skipIf(MODEL, "el modelo esta presente, no aplica el caso de ausencia")
    def test_sin_modelo_da_error_claro(self):
        # Si falta el modelo, el pipeline avisa en vez de fallar de forma rara.
        with self.assertRaises(VisionUnavailableError):
            body_measure.estimate_circumferences(b"x", b"y", height_cm=170)


@unittest.skipUnless(VISION, "mediapipe/opencv/numpy no instalados")
class TestVisionHelpers(unittest.TestCase):
    def test_width_at_sobre_mascara_sintetica(self):
        import numpy as np
        mask = np.zeros((50, 60), dtype=bool)
        mask[20, 10:31] = True  # fila 20: x=10..30 -> 21 px de ancho
        self.assertEqual(body_measure.width_at(mask, 20), 21.0)
        self.assertEqual(body_measure.width_at(mask, 0), 0.0)

    def test_person_height_px(self):
        import numpy as np
        mask = np.zeros((100, 40), dtype=bool)
        mask[10:31, 5:35] = True  # filas 10..30 -> 21 px de alto
        self.assertEqual(body_measure.person_height_px(mask), 21.0)

    def test_person_height_vacia(self):
        import numpy as np
        with self.assertRaises(NoPersonDetectedError):
            body_measure.person_height_px(np.zeros((10, 10), dtype=bool))

    def test_level_rows_ordenados(self):
        filas = body_measure.level_rows(
            {"nose_y": 50, "shoulder_y": 150, "hip_y": 400})
        self.assertLess(filas["neck"], filas["waist"])
        self.assertLess(filas["waist"], filas["hip"])


@unittest.skipUnless(VISION and MODEL, "se necesita mediapipe y el modelo descargado")
class TestVisionEndToEnd(unittest.TestCase):
    def test_imagen_en_blanco_no_detecta_persona(self):
        import cv2
        import numpy as np
        blanco = np.zeros((200, 200, 3), dtype=np.uint8)
        ok, buf = cv2.imencode(".png", blanco)
        self.assertTrue(ok)
        data = buf.tobytes()
        with self.assertRaises(NoPersonDetectedError):
            body_measure.estimate_circumferences(data, data, height_cm=170)


if __name__ == "__main__":
    unittest.main()
