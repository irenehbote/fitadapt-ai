"""Descarga el modelo de MediaPipe Pose Landmarker (necesario para el pipeline de fotos).

Uso:
    python -m backend.vision.download_model              # verificacion TLS normal
    python -m backend.vision.download_model --insecure   # si tu red intercepta TLS

El binario del modelo NO se versiona en git (ver .gitignore). Cada quien lo
descarga en su maquina con este script.

Nota sobre --insecure: desactiva la verificacion del certificado TLS. Uselo solo
si tu red corporativa intercepta HTTPS y confias en ella; lo ideal es instalar
el certificado raiz corporativo para no necesitar este flag.
"""
from __future__ import annotations

import argparse
import os
import ssl
import urllib.request

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task")

DEST = os.path.join(os.path.dirname(__file__), "models", "pose_landmarker_lite.task")


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga el modelo Pose Landmarker.")
    parser.add_argument("--insecure", action="store_true",
                        help="Desactiva la verificacion TLS (redes que interceptan HTTPS).")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    context = ssl._create_unverified_context() if args.insecure else None

    print(f"Descargando modelo desde {MODEL_URL} ...")
    with urllib.request.urlopen(MODEL_URL, context=context) as resp, open(DEST, "wb") as f:
        f.write(resp.read())
    print(f"Modelo guardado en {DEST} ({os.path.getsize(DEST)} bytes)")


if __name__ == "__main__":
    main()
