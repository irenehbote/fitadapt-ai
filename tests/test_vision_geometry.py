"""Pruebas de la geometria del pipeline de fotos (sin dependencias externas)."""
import math
import unittest

from backend.vision.geometry import (circumference_cm, cm_per_pixel,
                                     ellipse_perimeter)


class TestVisionGeometry(unittest.TestCase):
    def test_cm_per_pixel(self):
        # 170 cm en 850 px -> 0.2 cm/px.
        self.assertAlmostEqual(cm_per_pixel(850, 170), 0.2)

    def test_cm_per_pixel_invalido(self):
        with self.assertRaises(ValueError):
            cm_per_pixel(0, 170)

    def test_elipse_es_circulo(self):
        # Con semiejes iguales, el perimetro es el de un circulo: 2*pi*r.
        self.assertAlmostEqual(ellipse_perimeter(5, 5), 2 * math.pi * 5, places=6)

    def test_elipse_intermedia(self):
        # El perimetro de una elipse esta entre el de los dos circulos limite.
        p = ellipse_perimeter(10, 4)
        self.assertGreater(p, 2 * math.pi * 4)
        self.assertLess(p, 2 * math.pi * 10)

    def test_circunferencia_cm(self):
        # Seccion circular: anchura = profundidad = 100 px, 0.2 cm/px -> diametro 20 cm.
        # Circunferencia esperada = pi * 20 ~ 62.8 cm.
        c = circumference_cm(100, 100, 0.2)
        self.assertAlmostEqual(c, math.pi * 20, delta=0.1)

    def test_circunferencia_invalida(self):
        with self.assertRaises(ValueError):
            circumference_cm(0, 100, 0.2)


if __name__ == "__main__":
    unittest.main()
