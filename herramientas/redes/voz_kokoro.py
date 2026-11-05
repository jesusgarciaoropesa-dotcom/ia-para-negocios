"""
Voz en off con Kokoro (código abierto, licencia Apache 2.0: uso comercial permitido, gratis y sin cuentas).

Voz elegida por Jesús: em_alex (hombre, español). El modelo (~350 MB) no se guarda en el repo: se
descarga de GitHub la primera vez a ~/.cache/kokoro y se reutiliza.

    from voz_kokoro import Kokoro24
    k = Kokoro24()                      # voz y velocidad por defecto
    audio_int16_bytes, segundos = k.decir("Hola, esto es una prueba.")
"""
import subprocess, sys, urllib.request
from pathlib import Path

VOZ = "em_alex"
VELOCIDAD = 1.0            # >1 = más rápido
CACHE = Path.home() / ".cache" / "kokoro"
BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
ARCHIVOS = {"kokoro-v1.0.onnx": 300_000_000, "voices-v1.0.bin": 25_000_000}


def _asegurar():
    try:
        import kokoro_onnx  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "kokoro-onnx"], check=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    for nombre, minimo in ARCHIVOS.items():
        ruta = CACHE / nombre
        if not ruta.exists() or ruta.stat().st_size < minimo:
            print(f"Descargando {nombre}…", file=sys.stderr)
            tmp = ruta.with_suffix(".part")
            urllib.request.urlretrieve(BASE + nombre, tmp)
            tmp.rename(ruta)


class Kokoro24:
    sr = 24000

    def __init__(self, voz=VOZ, velocidad=VELOCIDAD):
        _asegurar()
        from kokoro_onnx import Kokoro
        self.k = Kokoro(str(CACHE / "kokoro-v1.0.onnx"), str(CACHE / "voices-v1.0.bin"))
        self.voz, self.velocidad = voz, velocidad

    def decir(self, texto):
        import numpy as np
        a, sr = self.k.create(texto, voice=self.voz, speed=self.velocidad, lang="es")
        self.sr = sr
        # Quita el silencio que Kokoro deja al principio y al final (las pausas las ponemos nosotros)
        umbral = 0.01
        idx = np.where(np.abs(a) > umbral)[0]
        if len(idx):
            a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
        pcm = (np.clip(a, -1, 1) * 32767).astype("<i2").tobytes()
        return pcm, len(pcm) / 2 / sr
