"""
Voz natural para los reels con Gemini TTS (voz "Achird", elegida por Jesús el 12-11-2026).

La máquina de los agentes no llega a Google, así que la voz se genera en Supabase:
  1. El generador calcula qué textos hay que leer (uno por lámina) y una CLAVE por texto.
  2. Si falta algún audio, se pide a la función `voz` de Supabase con el pedido que imprime
     `--pedido-voz` (el agente lo manda con net.http_post por SQL, ver METODO.md).
  3. La función guarda cada audio en la rama "voces" del repo otro (voces/reels/<clave>.wav) y el
     generador lo descarga de raw.githubusercontent.com (eso sí se alcanza) y lo trocea por frases.
Si no hay audio de Gemini, el generador usa la voz de antes (Kokoro) para no quedarse sin voz.
"""
import hashlib, json, sys, urllib.request
from pathlib import Path

VOZ = "Achird"
ESTILO_LIBRE = ("Lee este texto en español de España (acento castellano peninsular), con voz natural y cercana, "
                "como un creador de contenido explicando algo útil a un amigo en un reel: ritmo ágil, entonación viva, "
                "sin sonar a anuncio ni a robot.")
ESTILO = ESTILO_LIBRE[:-1] + ". Entre una frase y la siguiente deja siempre una pausa clara de casi un segundo."
# El cupo gratuito de Google es de pocos audios al día: se pide UN audio por reel (todo el guion, con pausas
# entre frases) y se trocea aquí. Si el troceo no cuadra, se piden audios por lámina como respaldo.
RAW = "https://raw.githubusercontent.com/jesusgarciaoropesa-dotcom/otro/voces/"
FUNCION = "https://gimoqpusrdltlkrwsykr.supabase.co/functions/v1/voz"
CACHE = Path.home() / ".cache" / "voz-gemini"


def clave(texto, voz=VOZ, estilo=ESTILO):
    return hashlib.sha1(f"{voz}|{estilo}|{texto}".encode("utf-8")).hexdigest()[:16]


def ruta(texto, voz=VOZ, estilo=ESTILO):
    return f"reels/{clave(texto, voz, estilo)}.wav"


def descargar(texto, voz=VOZ, estilo=ESTILO):
    """Devuelve (pcm int16 bytes, sr) del audio ya generado, o None si todavía no existe."""
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / f"{clave(texto, voz, estilo)}.wav"
    if not local.exists():
        try:
            with urllib.request.urlopen(RAW + ruta(texto, voz, estilo), timeout=30) as r:
                local.write_bytes(r.read())
        except Exception:
            return None
    import wave
    with wave.open(str(local), "rb") as w:
        return w.readframes(w.getnframes()), w.getframerate()


def pedido(textos, voz=VOZ, estilo=ESTILO):
    """Lo que hay que mandar a la función `voz` (solo los textos que aún no tienen audio), en tandas de 6."""
    faltan = [t for t in dict.fromkeys(textos) if descargar(t, voz, estilo) is None]
    piezas = [{"ruta": ruta(t, voz, estilo), "texto": t} for t in faltan]
    return [{"voz": voz, "estilo": estilo, "piezas": piezas[i:i + 6]} for i in range(0, len(piezas), 6)]


def partir_validado(pcm, sr, frases):
    """Como partir(), pero devuelve None si algún trozo no cuadra con su frase (velocidad imposible)."""
    trozos = partir(pcm, sr, [len(f) for f in frases])
    for f, p in zip(frases, trozos):
        seg = len(p) / 2 / sr
        if seg < 0.25 or not (5 <= len(f) / max(seg, 0.01) <= 32):
            return None
    return trozos


def guion_entero(frases_por_lamina):
    """Une las frases de todas las láminas en un solo texto (un solo audio para todo el reel)."""
    return " ".join(f for k in sorted(frases_por_lamina) for f in frases_por_lamina[k])


def repartir_entero(frases_por_lamina, voz=VOZ):
    """Si existe el audio del guion entero y se trocea bien, devuelve {lámina: [pcm por frase]} y sr."""
    r = descargar(guion_entero(frases_por_lamina), voz)
    if not r:
        return None, None
    pcm, sr = r
    todas = [f for k in sorted(frases_por_lamina) for f in frases_por_lamina[k]]
    trozos = partir_validado(pcm, sr, todas)
    if not trozos:
        return None, sr
    out, i = {}, 0
    for k in sorted(frases_por_lamina):
        n = len(frases_por_lamina[k])
        out[k] = trozos[i:i + n]
        i += n
    return out, sr


def sql_pedido(tandas):
    """Sentencias SQL listas para que el agente las ejecute (una por tanda)."""
    out = []
    for t in tandas:
        j = json.dumps(t, ensure_ascii=False).replace("$v$", "")
        out.append(f"select net.http_post(url:='{FUNCION}', headers:='{{\"Content-Type\":\"application/json\"}}'::jsonb, "
                   f"body:=$v${j}$v$::jsonb, timeout_milliseconds:=150000);")
    return out


def recortar(pcm, sr, antes=0.03, despues=0.08, umbral=500):
    import numpy as np
    a = np.frombuffer(pcm, dtype="<i2")
    idx = np.where(np.abs(a) > umbral)[0]
    if not len(idx):
        return pcm
    return a[max(0, idx[0] - int(antes * sr)): idx[-1] + int(despues * sr)].tobytes()


def partir(pcm, sr, pesos):
    """Trocea el audio de una lámina en len(pesos) frases. Se le pide a Gemini una pausa clara entre frases,
    así que se corta en los len(pesos)-1 silencios más largos (en orden). Si faltan silencios, se reparte
    lo que queda según la longitud de cada frase. Devuelve una lista de pcm sin silencios en los bordes."""
    import numpy as np
    n = len(pesos)
    a16 = np.frombuffer(pcm, dtype="<i2")
    if n <= 1:
        return [recortar(pcm, sr)]
    a = a16.astype(np.float32)
    hop = int(0.01 * sr)
    energia = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, max(1, len(a) - hop), hop)])
    umbral = max(250.0, float(np.percentile(energia, 20)) * 1.5)
    callado = energia < umbral
    voz = np.where(~callado)[0]
    if not len(voz):
        return [b""] * n
    ini, fin = voz[0], voz[-1]
    silencios, i = [], ini
    while i <= fin:
        if callado[i]:
            j = i
            while j <= fin and callado[j]:
                j += 1
            if j - i >= 8:
                silencios.append((j - i, (i + j) // 2))
            i = j
        else:
            i += 1
    elegidos = sorted(c for _, c in sorted(silencios, reverse=True)[:n - 1])
    cortes = [c * hop for c in elegidos]
    if len(cortes) < n - 1:   # no hay pausas suficientes: reparte por longitud de texto
        suma, acum, cortes = float(sum(pesos)), 0, []
        for k in range(n - 1):
            acum += pesos[k]
            cortes.append(int(ini * hop + (fin - ini) * hop * acum / suma))
    limites = [0] + cortes + [len(a16)]
    return [recortar(a16[limites[k]:limites[k + 1]].tobytes(), sr) for k in range(n)]


def partir_alineado(pcm, sr, frases):
    """Trocea el audio de un guion entero en len(frases) trozos eligiendo, entre todos los silencios, los
    que mejor cuadran con donde debería acabar cada frase según su longitud (Gemini también hace pausas
    dentro de una frase, tras «?» o «:», así que no vale coger sin más los silencios más largos).
    Devuelve la lista de pcm, o None si algún trozo sale con una velocidad imposible."""
    import numpy as np
    n = len(frases)
    a16 = np.frombuffer(pcm, dtype="<i2")
    if n <= 1:
        return [recortar(pcm, sr)]
    a = a16.astype(np.float32)
    hop = int(0.01 * sr)
    energia = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, max(1, len(a) - hop), hop)])
    umbral = max(250.0, float(np.percentile(energia, 20)) * 1.5)
    callado = energia < umbral
    voz = np.where(~callado)[0]
    if not len(voz):
        return None
    ini, fin = int(voz[0]), int(voz[-1])
    cands, i = [], ini
    while i <= fin:
        if callado[i]:
            j = i
            while j <= fin and callado[j]:
                j += 1
            if j - i >= 10:
                cands.append(((i + j) // 2, j - i))
            i = j
        else:
            i += 1
    if len(cands) < n - 1:
        return None
    pesos = [len(f) + 6 for f in frases]          # +6: cada frase lleva su pausa
    suma, acum, objetivos = float(sum(pesos)), 0, []
    for k in range(n - 1):
        acum += pesos[k]
        objetivos.append(ini + (fin - ini) * acum / suma)
    span = float(fin - ini)
    m = len(cands)
    def coste(k, c):
        pos, largo = cands[c]
        return ((pos - objetivos[k]) / span) ** 2 * 400 - min(largo, 80) / 80.0
    INF = float("inf")
    dp = [[INF] * m for _ in range(n - 1)]
    prev = [[-1] * m for _ in range(n - 1)]
    for c in range(m):
        dp[0][c] = coste(0, c)
    for k in range(1, n - 1):
        mejor, arg = INF, -1
        for c in range(m):
            if c - 1 >= 0 and dp[k - 1][c - 1] < mejor:
                mejor, arg = dp[k - 1][c - 1], c - 1
            if arg >= 0:
                dp[k][c] = mejor + coste(k, c)
                prev[k][c] = arg
    c = min(range(m), key=lambda x: dp[n - 2][x])
    if dp[n - 2][c] == INF:
        return None
    elegidos = []
    for k in range(n - 2, -1, -1):
        elegidos.append(cands[c][0])
        c = prev[k][c]
    cortes = [p * hop for p in reversed(elegidos)]
    limites = [0] + cortes + [len(a16)]
    trozos = [recortar(a16[limites[k]:limites[k + 1]].tobytes(), sr) for k in range(n)]
    for f, t in zip(frases, trozos):
        seg = len(t) / 2 / sr
        if seg < 0.25 or not (4 <= len(f) / max(seg, 0.01) <= 32):
            return None
    return trozos


if __name__ == "__main__":
    print(__doc__)
