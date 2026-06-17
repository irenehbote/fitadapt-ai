"""Estimacion EXPERIMENTAL de circunferencias y grasa corporal desde fotos.

Cadena: foto frontal + lateral -> MediaPipe Pose Landmarker (Tasks API) ->
silueta + landmarks -> anchuras a la altura de cuello/cintura/cadera ->
calibracion por altura real -> circunferencias (elipse) -> formula Navy.

LIMITACIONES (honestas):
  - Estimacion orientativa, margen amplio (~±5-8%), peor que con cinta metrica.
  - Necesita foto frontal y lateral, cuerpo entero, ropa ajustada y la altura real.
  - Requiere dependencias extra (requirements-vision.txt) y un modelo descargado
    con `python -m backend.vision.download_model`.

La precision real NO esta validada contra un metodo de referencia.
"""
from __future__ import annotations

import os
from typing import Dict

from ..analytics.body_composition import body_fat_category, navy_body_fat
from .geometry import cm_per_pixel, ellipse_perimeter


class VisionUnavailableError(RuntimeError):
    """Faltan dependencias de vision o el modelo no esta descargado."""


class NoPersonDetectedError(ValueError):
    """No se detecto una persona en la imagen."""


# Indices de landmarks de Pose que usamos.
_NOSE, _LSHOULDER, _RSHOULDER, _LHIP, _RHIP = 0, 11, 12, 23, 24

# Ruta del modelo (se puede sobreescribir con la variable de entorno).
_DEFAULT_MODEL = os.path.join(os.path.dirname(__file__), "models",
                              "pose_landmarker_lite.task")


def model_path() -> str:
    """Ruta al fichero del modelo Pose Landmarker."""
    return os.environ.get("FITADAPT_POSE_MODEL", _DEFAULT_MODEL)


def is_available() -> bool:
    """True si mediapipe/opencv/numpy estan instalados."""
    try:
        import cv2  # noqa: F401
        import mediapipe  # noqa: F401
        import numpy  # noqa: F401
        return True
    except ImportError:
        return False


def model_available() -> bool:
    """True si el fichero del modelo existe en disco."""
    return os.path.exists(model_path())


def _require() -> None:
    if not is_available():
        raise VisionUnavailableError(
            "Faltan dependencias de vision. Instala: pip install -r requirements-vision.txt")
    if not model_available():
        raise VisionUnavailableError(
            "Modelo no encontrado. Descargalo con: python -m backend.vision.download_model")


def _decode(image_bytes: bytes):
    import cv2
    import numpy as np
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("No se pudo leer la imagen")
    return img


def _analyze(image_bytes: bytes):
    """Devuelve (mascara_bool, niveles_y_en_px, alto, ancho) de la persona."""
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    img = _decode(image_bytes)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    alto, ancho = img.shape[:2]

    options = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=model_path()),
        output_segmentation_masks=True,
        num_poses=1,
    )
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        res = landmarker.detect(mp_image)

    if not res.pose_landmarks or not res.segmentation_masks:
        raise NoPersonDetectedError("No se detecto una persona en la imagen")

    mask = res.segmentation_masks[0].numpy_view() > 0.5
    lm = res.pose_landmarks[0]

    def y(i: int) -> float:
        return lm[i].y * alto

    niveles = {
        "nose_y": y(_NOSE),
        "shoulder_y": (y(_LSHOULDER) + y(_RSHOULDER)) / 2,
        "hip_y": (y(_LHIP) + y(_RHIP)) / 2,
    }
    return mask, niveles, alto, ancho


def width_at(mask, row: float) -> float:
    """Anchura (px) de la silueta en una fila dada (max_x - min_x)."""
    import numpy as np
    fila = int(round(row))
    fila = max(0, min(mask.shape[0] - 1, fila))
    xs = np.where(mask[fila])[0]
    if xs.size == 0:
        return 0.0
    return float(xs.max() - xs.min() + 1)


def person_height_px(mask) -> float:
    """Altura (px) de la persona: extension vertical de la silueta."""
    import numpy as np
    ys = np.where(mask.any(axis=1))[0]
    if ys.size == 0:
        raise NoPersonDetectedError("La silueta esta vacia")
    return float(ys.max() - ys.min() + 1)


def level_rows(niveles: dict) -> Dict[str, float]:
    """Filas (y, px) donde medimos cuello, cintura y cadera (aproximadas)."""
    s, h, n = niveles["shoulder_y"], niveles["hip_y"], niveles["nose_y"]
    return {
        "neck": s - 0.15 * (s - n),
        "waist": s + 0.55 * (h - s),
        "hip": h,
    }


def estimate_circumferences(front_bytes: bytes, side_bytes: bytes,
                            height_cm: float) -> Dict[str, float]:
    """Estima cuello, cintura y cadera (cm) desde una foto frontal y una lateral."""
    _require()
    mask_f, niv_f, _, _ = _analyze(front_bytes)
    mask_s, niv_s, _, _ = _analyze(side_bytes)
    cmpx_f = cm_per_pixel(person_height_px(mask_f), height_cm)
    cmpx_s = cm_per_pixel(person_height_px(mask_s), height_cm)
    filas_f, filas_s = level_rows(niv_f), level_rows(niv_s)

    circunferencias: Dict[str, float] = {}
    for parte in ("neck", "waist", "hip"):
        ancho_frontal_cm = width_at(mask_f, filas_f[parte]) * cmpx_f
        profundidad_cm = width_at(mask_s, filas_s[parte]) * cmpx_s
        if ancho_frontal_cm <= 0 or profundidad_cm <= 0:
            raise NoPersonDetectedError(f"No se pudo medir la zona '{parte}'")
        circ = ellipse_perimeter(ancho_frontal_cm / 2, profundidad_cm / 2)
        circunferencias[parte] = round(circ, 1)
    return circunferencias


def estimate_body_fat_from_photos(front_bytes: bytes, side_bytes: bytes,
                                  height_cm: float, sex: str) -> dict:
    """Estima la grasa corporal (%) desde fotos, via circunferencias + Navy."""
    circ = estimate_circumferences(front_bytes, side_bytes, height_cm)
    bf = navy_body_fat(sex, height_cm, neck_cm=circ["neck"],
                       waist_cm=circ["waist"], hip_cm=circ["hip"])
    return {
        "circumferences": circ,
        "body_fat_pct": bf,
        "category": body_fat_category(bf, sex),
        "method": "photo_navy",
        "confidence_note": ("Estimacion EXPERIMENTAL por foto (margen amplio, "
                            "~±5-8%). No es una medicion: mejora con fotos de "
                            "cuerpo entero (frontal y lateral) y la altura correcta."),
    }
