"""
Música de fondo propia para los reels (sintetizada aquí mismo: sin derechos de nadie, se puede usar libremente).
Genera herramientas/redes/musica/<nombre>.wav: un bucle suave tipo lo-fi (piano eléctrico, bajo y batería ligera).
  python3 herramientas/redes/musica.py            # crea los bucles que falten
"""
import pathlib, wave
import numpy as np

SR = 44100
AQUI = pathlib.Path(__file__).parent / "musica"
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def f(nota, octava):
    return 440.0 * 2 ** ((NOTAS[nota] + 12 * (octava + 1) - 69) / 12)


def piano(fr, dur, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 2.2) * (1 - np.exp(-t * 300))
    s = (np.sin(2 * np.pi * fr * t) + 0.45 * np.sin(2 * np.pi * 2 * fr * t) * np.exp(-t * 4)
         + 0.18 * np.sin(2 * np.pi * 3 * fr * t) * np.exp(-t * 6) + 0.5 * np.sin(2 * np.pi * fr * 1.003 * t))
    return vel * s * env * (1 + 0.04 * np.sin(2 * np.pi * 5 * t))


def bajo(fr, dur):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * fr * t) + 0.25 * np.sin(4 * np.pi * fr * t)) * np.exp(-t * 1.5) * (1 - np.exp(-t * 200))


def bombo(dur=0.35):
    t = np.arange(int(dur * SR)) / SR
    return np.sin(2 * np.pi * (45 + 70 * np.exp(-t * 25)) * t) * np.exp(-t * 9)


def ruido(dur, decae, rng):
    t = np.arange(int(dur * SR)) / SR
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)  # más agudo
    return n * np.exp(-t * decae)


def bucle(nombre, acordes, bpm, compases=16, semilla=1):
    rng = np.random.default_rng(semilla)
    pulso = 60 / bpm
    total = int(compases * 4 * pulso * SR)
    out = np.zeros(total + SR * 2)
    def pon(x, seg, g):
        i = int(seg * SR); out[i:i + len(x)] += g * x
    for c in range(compases):
        raiz, notas = acordes[c % len(acordes)]
        t0 = c * 4 * pulso
        for k, (n, o) in enumerate(notas):          # acorde arpegiado suave
            pon(piano(f(n, o), 4 * pulso + 1), t0 + k * 0.03, 0.16)
        for b in (0, 2.5):                           # pequeño motivo
            n, o = notas[(c + int(b)) % len(notas)]
            pon(piano(f(n, o + 1), 1.2, 0.8), t0 + b * pulso, 0.07)
        pon(bajo(f(raiz, 2), 2 * pulso), t0, 0.32)
        pon(bajo(f(raiz, 2), 1.5 * pulso), t0 + 2.5 * pulso, 0.22)
        for b in range(4):
            if b in (0, 2):
                pon(bombo(), t0 + b * pulso, 0.5)
            if b in (1, 3):
                pon(ruido(0.25, 18, rng), t0 + b * pulso, 0.10)
            for h in (0, 0.5):
                pon(ruido(0.06, 70, rng), t0 + (b + h) * pulso + rng.uniform(-0.008, 0.008), 0.035 if h else 0.05)
    out = out[:total]
    cola = int(0.05 * SR); out[:cola] *= np.linspace(0, 1, cola); out[-cola:] *= np.linspace(1, 0, cola)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.8
    AQUI.mkdir(exist_ok=True)
    with wave.open(str(AQUI / f"{nombre}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype("<i2").tobytes())


BUCLES = {
    "suave": ([("F", [("F", 3), ("A", 3), ("C", 4), ("E", 4)]), ("E", [("E", 3), ("G", 3), ("B", 3), ("D", 4)]),
               ("D", [("D", 3), ("F", 3), ("A", 3), ("C", 4)]), ("C", [("C", 3), ("E", 3), ("G", 3), ("B", 3)])], 88),
    "animada": ([("C", [("C", 4), ("E", 4), ("G", 4), ("B", 4)]), ("A", [("A", 3), ("C", 4), ("E", 4), ("G", 4)]),
                 ("F", [("F", 3), ("A", 3), ("C", 4), ("E", 4)]), ("G", [("G", 3), ("B", 3), ("D", 4), ("F", 4)])], 100),
}

if __name__ == "__main__":
    for n, (ac, bpm) in BUCLES.items():
        if not (AQUI / f"{n}.wav").exists():
            bucle(n, ac, bpm)
            print("creado", AQUI / f"{n}.wav")
