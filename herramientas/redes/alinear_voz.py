"""
Trocea el audio de un guion entero (UN solo audio de Gemini para todo el reel) en una pieza por frase.

Gemini hace pausas parecidas dentro y entre frases, así que no basta con cortar en los silencios. Aquí se
hace un «alineado forzado» sencillo: se lee el mismo guion con Kokoro frase a frase (sabemos dónde acaba cada
una), se comparan las dos grabaciones con DTW sobre MFCC y cada final de frase de Kokoro se lleva a su
momento en la voz de Gemini, ajustándolo al silencio más cercano. Necesita librosa (se instala sola) y Kokoro
(voz_kokoro.py, descarga su modelo la primera vez).
"""
import subprocess, sys
import numpy as np


def _librosa():
    try:
        import librosa
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "librosa"], check=True)
        import librosa
    return librosa


def _silencios(a, sr, minimo=10):
    hop = int(.01 * sr)
    e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    q = e < max(250, np.percentile(e, 20) * 1.5)
    S, i = [], 0
    while i < len(q):
        if q[i]:
            j = i
            while j < len(q) and q[j]:
                j += 1
            if j - i >= minimo:
                S.append(((i + j) // 2, j - i))
            i = j
        else:
            i += 1
    return S


def alinear(pcm, sr, frases):
    """Devuelve una lista de pcm (uno por frase) o None si el resultado no es creíble."""
    import voz_gemini as G
    from voz_kokoro import Kokoro24
    librosa = _librosa()
    if len(frases) <= 1:
        return [G.recortar(pcm, sr)]
    k = Kokoro24()
    g = np.frombuffer(pcm, dtype="<i2").astype(np.float32)
    piezas, lims, t = [], [], 0
    pausa = np.zeros(int(0.35 * 24000), dtype=np.float32)
    for f in frases:
        b, _ = k.decir(f)
        x = np.frombuffer(b, dtype="<i2").astype(np.float32)
        piezas += [x, pausa]
        t += len(x)
        lims.append(t + len(pausa) // 2)
        t += len(pausa)
    kk = np.concatenate(piezas)

    def mfcc(x, s):
        m = librosa.feature.mfcc(y=x / 32768, sr=s, n_mfcc=20, hop_length=int(.01 * s), n_fft=int(.025 * s) * 2)[1:]
        return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)

    _, wp = librosa.sequence.dtw(X=mfcc(kk, 24000), Y=mfcc(g, sr), metric="cosine")
    mapa = {}
    for i, j in wp[::-1]:
        mapa.setdefault(int(i), []).append(int(j))
    S = _silencios(g, sr)
    hop, cortes = int(.01 * sr), []
    for L in lims[:-1]:
        fk = L // 240
        js = mapa.get(fk) or mapa[min(mapa, key=lambda z: abs(z - fk))]
        fj = int(np.median(js))
        cand = [c for c in S if abs(c[0] - fj) <= 50]
        if cand:
            fj = min(cand, key=lambda c: abs(c[0] - fj) - c[1] * 0.3)[0]
        cortes.append(fj * hop)
    if any(b <= a for a, b in zip(cortes, cortes[1:])):
        return None
    lim = [0] + cortes + [len(g)]
    trozos = [G.recortar(g[lim[i]:lim[i + 1]].astype("<i2").tobytes(), sr) for i in range(len(frases))]
    for f, p in zip(frases, trozos):
        seg = len(p) / 2 / sr
        if seg < 0.4 or not (6 <= len(f) / seg <= 26):
            return None
    return trozos
