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
ESTILO = ("Lee este texto en español de España (acento castellano peninsular), con voz natural y cercana, "
          "como un creador de contenido explicando algo útil a un amigo en un reel: ritmo ágil, entonación viva, "
          "sin sonar a anuncio ni a robot. Entre una frase y la siguiente deja siempre una pausa clara de casi un segundo.")
RAW = "https://raw.githubusercontent.com/jesusgarciaoropesa-dotcom/otro/voces/"
FUNCION = "https://gimoqpusrdltlkrwsykr.supabase.co/functions/v1/voz"
CACHE = Path.home() / ".cache" / "voz-gemini"


def clave(texto, voz=VOZ, estilo=ESTILO):
    return hashlib.sha1(f"{voz}|{estilo}|{texto}".encode("utf-8")).hexdigest()[:16]


def ruta(texto, voz=VOZ):
    return f"reels/{clave(texto, voz)}.wav"


def descargar(texto, voz=VOZ):
    """Devuelve (pcm int16 bytes, sr) del audio ya generado, o None si todavía no existe."""
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / f"{clave(texto, voz)}.wav"
    if not local.exists():
        try:
            with urllib.request.urlopen(RAW + ruta(texto, voz), timeout=30) as r:
                local.write_bytes(r.read())
        except Exception:
            return None
    import wave
    with wave.open(str(local), "rb") as w:
        return w.readframes(w.getnframes()), w.getframerate()


def pedido(textos, voz=VOZ):
    """Lo que hay que mandar a la función `voz` (solo los textos que aún no tienen audio), en tandas de 6."""
    faltan = [t for t in dict.fromkeys(textos) if descargar(t, voz) is None]
    piezas = [{"ruta": ruta(t, voz), "texto": t} for t in faltan]
    return [{"voz": voz, "estilo": ESTILO, "piezas": piezas[i:i + 6]} for i in range(0, len(piezas), 6)]


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


if __name__ == "__main__":
    print(__doc__)
