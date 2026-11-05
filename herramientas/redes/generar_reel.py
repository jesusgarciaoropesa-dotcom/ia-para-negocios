#!/usr/bin/env python3
"""
Convierte la configuración de un carrusel de iando en un reel animado con voz en off
(vídeo vertical 1080x1920, sin música).

    python3 herramientas/redes/generar_reel.py configs/<slug>.json [--salida reels] [--fps 30] [--sin-voz]

Usa el mismo JSON que generar_carrusel.py. La voz (Kokoro, voz "em_alex", gratis y de uso comercial libre;
ver voz_kokoro.py) marca el ritmo: cada título y frase aparece en pantalla justo
cuando se lee, con pausas tras los títulos, los puntos y las comas. Cada escena dura lo que tarda
en leerse. Se dibuja fotograma a fotograma con Chromium y se monta con ffmpeg en reels/<slug>.mp4,
más reels/<slug>-portada.jpg para la portada del reel.

Opcional en cada lámina: "reel" = {"titulo"?, "texto"?, "dato"?...} versión más corta solo para el
vídeo (se ve y se lee en lugar de la del carrusel). "voz" = texto que se lee en lugar del de pantalla (si la pronunciación
de algo sale rara, escríbelo como se dice). Para comprobar lo que se va a leer: --guion.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_carrusel import fuente, CHIP, CHECK, e, s_dato  # noqa: E402

import re, wave
CSS = "".join(fuente(p) for p in (400, 600, 800)) + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;color:#fff;
 background:linear-gradient(150deg,#4338ca 0%,#6366f1 45%,#8b5cf6 100%)}
.fondo{position:absolute;inset:-200px;opacity:.14;animation:deriva 40s linear both}
@keyframes deriva{from{transform:translate(0,0)}to{transform:translate(-160px,-260px)}}
.marca{position:absolute;top:120px;left:96px;display:flex;align-items:center;gap:20px;font-weight:600;font-size:36px;z-index:5}
.logo{width:68px;height:68px;border-radius:16px;background:rgba(255,255,255,.2);display:grid;place-items:center}
.barra{position:absolute;top:84px;left:96px;right:96px;height:8px;border-radius:9px;background:rgba(255,255,255,.22);overflow:hidden;z-index:5}
.barra i{display:block;height:100%;background:#fde68a;transform-origin:left;animation:barra var(--total) linear both}
@keyframes barra{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.esc{position:absolute;inset:0;padding:300px 96px 260px;display:flex;flex-direction:column;justify-content:center;opacity:0;
 animation:entra .5s cubic-bezier(.2,.8,.2,1) var(--ini) both, sale var(--sal) ease-in var(--fin) forwards}
.esc.ultima{animation:entra .5s cubic-bezier(.2,.8,.2,1) var(--ini) both}
@keyframes entra{from{opacity:0}to{opacity:1}}
@keyframes sale{from{opacity:1;transform:none}to{opacity:0;transform:translateX(-120px)}}
.ap{opacity:0;animation:sube .6s cubic-bezier(.2,.8,.2,1) both}
@keyframes sube{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:none}}
span.ap{animation-name:aparece;animation-duration:.5s}
@keyframes aparece{from{opacity:0}to{opacity:1}}
.pop{opacity:0;animation:pop .55s cubic-bezier(.3,1.6,.5,1) both}
@keyframes pop{from{opacity:0;transform:scale(.4) rotate(-12deg)}to{opacity:1;transform:none}}
.pal{display:inline-block;opacity:0;animation:pal .45s cubic-bezier(.2,.8,.2,1) both}
@keyframes pal{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
.kicker{align-self:flex-start;font-weight:800;font-size:34px;letter-spacing:4px;text-transform:uppercase;padding:16px 30px;border-radius:999px;background:rgba(255,255,255,.2)}
h1{font-weight:800;font-size:124px;line-height:1.02;letter-spacing:-3px;margin-top:50px}
h2{font-weight:800;font-size:92px;line-height:1.05;letter-spacing:-2px}
.dest{color:#fde68a}
.sub{font-size:50px;line-height:1.3;opacity:.92;margin-top:48px}
.card{background:#fff;color:#1e1b4b;border-radius:44px;padding:70px 64px;box-shadow:0 30px 80px rgba(30,27,75,.35)}
.card h2{color:#1e1b4b}
.card .dest{color:#4f46e5}
.num{width:150px;height:150px;border-radius:40px;background:linear-gradient(140deg,#6366f1,#8b5cf6);color:#fff;font-weight:800;font-size:84px;display:grid;place-items:center;margin-bottom:56px}
.txt{font-size:52px;line-height:1.36;color:#3730a3;margin-top:44px}
.dato{margin-top:52px;background:#eef2ff;border-left:14px solid #8b5cf6;border-radius:28px;padding:40px 44px;font-size:42px;line-height:1.35;color:#312e81}
.dato b{font-weight:800}
ul{list-style:none;display:flex;flex-direction:column;gap:34px;margin-top:60px}
li{display:flex;gap:30px;align-items:flex-start;font-size:50px;line-height:1.28;color:#312e81}
li i{flex:none;width:64px;height:64px;border-radius:50%;background:#6366f1;display:grid;place-items:center;margin-top:2px}
.vs{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:56px}
.col{background:#eef2ff;border-radius:30px;padding:40px 32px}
.col h3{font-size:46px;font-weight:800;margin-bottom:26px;color:#4338ca}
.col li{font-size:38px;gap:16px}.col li i{width:46px;height:46px}
.cta{margin-top:60px;background:rgba(255,255,255,.16);border:3px solid rgba(255,255,255,.4);border-radius:34px;padding:44px 48px;font-size:46px;line-height:1.35}
.web{margin-top:70px;align-self:flex-start;background:#fff;color:#4f46e5;font-weight:800;font-size:54px;padding:28px 54px;border-radius:999px}
.desliza{position:absolute;bottom:150px;left:0;right:0;text-align:center;font-size:38px;font-weight:600;opacity:.8}
"""



def red():
    import random
    r = random.Random(5)
    d = []
    for _ in range(46):
        x, y, L = r.randint(0, 1480), r.randint(0, 2320), r.randint(80, 260)
        v = r.choice([-1, 1]) * r.randint(40, 120)
        d.append(f'<path d="M{x} {y}h{L}v{v}"/><circle cx="{x}" cy="{y}" r="7"/>')
    return f'<svg class="fondo" viewBox="0 0 1480 2320" width="1480" height="2320"><g stroke="#fff" stroke-width="3.5" fill="none">{"".join(d)}</g></svg>'



ENTRADA = 0.45      # la voz empieza cuando la escena ya ha entrado
COLA = 0.50         # respiro al acabar cada escena
SAL = 0.45          # transición de salida
VELOCIDAD = 1.10    # >1 = más rápido (voz Kokoro "em_alex")
PAUSA = {"titulo": 0.50, ".": 0.38, "?": 0.40, "!": 0.38, ":": 0.30, ";": 0.30, ",": 0.18, "item": 0.32, "": 0.26}
LEER_DATOS = False  # el recuadro "dato" se ve pero no se lee (en una lámina: "voz": {"dato": "..."} para leerlo)
CPS_SIN_VOZ = 14    # caracteres por segundo cuando se genera sin voz

# Cómo se dice lo que se escribe de otra forma (añade aquí lo que la voz lea raro)
DICCIONARIO = [
    (r"\ben iando\.xyz", "en nuestra web"), (r"iando\.xyz", "iando"), (r"\bChatGPT\b", "chat ye pe te"), (r"\bGPT\b", "ye pe te"),
    (r"Click-to-WhatsApp", "clic tu guasap"), (r"WhatsApp", "guasap"), (r"\bIA\b", "i a"),
    (r"\bCRM\b", "ce erre eme"), (r"\bAPI\b", "a pe i"), (r"\bSEO\b", "seo"), (r"\bPDF\b", "pe de efe"),
    (r"(\d)\s?€", r"\1 euros"), (r"€", "euros"), (r"(\d)\s?%", r"\1 por ciento"),
    (r"\s=\s", ": "), (r"→", ","), (r"\*\*", ""), (r"[«»\"“”]", ""), (r"·", ","), (r"\s+-\s+", ", "),
]
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
NUM = ["", "Uno", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete", "Ocho", "Nueve", "Diez"]


def decir(t):
    t = EMOJI.sub("", str(t or ""))
    for a, b in DICCIONARIO:
        t = re.sub(a, b, t)
    return re.sub(r"\s+", " ", t).strip()


def frases(t):
    """Parte un texto en frases cortas por la puntuación: (texto en pantalla, pausa después)."""
    t = re.sub(r"\s+", " ", str(t or "")).strip()
    if not t:
        return []
    trozos = [x for x in re.split(r"(?<=[,.;:?!])\s+", t) if x.strip()]
    return [(x, PAUSA.get(x.strip()[-1], PAUSA[""])) for x in trozos]


class Voz:
    def __init__(self, activa):
        self.activa, self.v, self.sr = activa, None, 24000
        if activa:
            from voz_kokoro import Kokoro24
            self.v = Kokoro24(velocidad=VELOCIDAD)
            self.sr = self.v.sr

    def decir(self, texto):
        """Devuelve (audio int16 bytes, segundos)."""
        txt = decir(texto)
        if not txt:
            return b"", 0.0
        if not self.activa:
            return b"", max(0.8, len(txt) / CPS_SIN_VOZ)
        if not re.search(r"[.,;:?!]$", txt):
            txt += "."
        return self.v.decir(txt)


class Linea:
    """Va colocando los trozos de voz en el tiempo."""
    def __init__(self, voz):
        self.voz, self.t, self.trozos = voz, 0.0, []

    def di(self, texto, pausa, voz_alt=None):
        audio, dur = self.voz.decir(voz_alt if voz_alt is not None else texto)
        ini = self.t
        if dur:
            self.trozos.append((ini, audio, texto))
            self.t += dur + pausa
        return ini, dur


def palabras(titulo, destacado, ini, dur):
    """Título palabra a palabra, al ritmo en que se lee; las del destacado en amarillo."""
    dest = set((destacado or "").lower().split())
    ws = str(titulo).split()
    paso = (dur * 0.85 / max(1, len(ws))) if dur else 0.09
    out = []
    for k, w in enumerate(ws):
        cls = "pal dest" if w.lower().strip(",.:;¿?¡!") in dest else "pal"
        out.append(f'<span class="{cls}" style="animation-delay:{ini + k * paso:.2f}s">{e(w)}</span>')
    return " ".join(out)


def d(t):
    return f'style="animation-delay:{t:.2f}s"'


def voz_de(s, campo):
    v = s.get("voz")
    if isinstance(v, dict):
        return v.get(campo)
    return v if (isinstance(v, str) and campo in ("texto", "subtitulo")) else None


def parrafo(L, texto, voz_alt=None, cls="", fin_pausa=None):
    """Párrafo que aparece frase a frase mientras se lee. Si hay texto alternativo de voz, se lee entero."""
    if voz_alt:
        ini, _ = L.di(texto, PAUSA["."], voz_alt)
        return f'<span class="ap" {d(ini)}>{s_dato(texto)}</span>'
    out = []
    fr = frases(texto)
    for k, (x, pausa) in enumerate(fr):
        if fin_pausa is not None and k == len(fr) - 1:
            pausa = fin_pausa
        ini, _ = L.di(x, pausa)
        out.append(f'<span class="ap" {d(ini)}>{s_dato(x)}</span>')
    return " ".join(out)


def escena(s, L, ini):
    """Devuelve (html de la escena, instante en que termina la voz)."""
    s = {**s, **(s.get("reel") or {})}   # versión corta para el vídeo, si la hay
    t = s.get("tipo", "punto")
    L.t = ini + ENTRADA
    if t == "portada":
        a, dur = L.di(s["titulo"], PAUSA["titulo"], voz_de(s, "titulo"))
        h = f'<span class="kicker ap" {d(ini + 0.2)}>{e(s.get("kicker"))}</span><h1>{palabras(s["titulo"], s.get("destacado"), a, dur)}</h1>'
        if s.get("subtitulo"):
            h += f'<p class="sub">{parrafo(L, s["subtitulo"], voz_de(s, "subtitulo"))}</p>'
        return h
    if t == "cierre":
        a, dur = L.di(s["titulo"], PAUSA["titulo"], voz_de(s, "titulo"))
        h = f'<h2 style="font-size:104px">{palabras(s["titulo"], s.get("destacado"), a, dur)}</h2>'
        if s.get("texto"):
            h += f'<p class="sub ap" {d(L.t - 0.2)}>{e(s["texto"])}</p>'
        cta = s.get("cta") or "¿Prefieres que te lo monten? Webs, reservas y automatizaciones para tu negocio."
        h += f'<div class="cta ap" {d(L.t + 0.2)}>{e(cta)}</div>'
        b, _ = L.di("Enlace en la bio.", 0)
        h += f'<span class="web pop" {d(b)}>Enlace en la bio 👆</span>'
        return h
    dentro = ""
    if t == "punto":
        if s.get("num"):
            n = str(s["num"])
            dentro += f'<div class="num pop" {d(ini + 0.2)}>{e(n)}</div>'
        a, dur = L.di(s["titulo"], PAUSA["titulo"], voz_de(s, "titulo"))
        dentro += f"<h2>{palabras(s['titulo'], s.get('destacado'), a, dur)}</h2>"
        if s.get("texto"):
            dentro += f'<p class="txt">{parrafo(L, s["texto"], voz_de(s, "texto"), fin_pausa=PAUSA["titulo"] if s.get("dato") else None)}</p>'
        if s.get("dato"):
            fr0 = L.t
            if LEER_DATOS or voz_de(s, "dato"):
                dentro += f'<div class="dato ap" {d(fr0)}>{parrafo(L, s["dato"], voz_de(s, "dato"))}</div>'
            else:
                dentro += f'<div class="dato ap" {d(fr0 - 0.1)}>{s_dato(s["dato"])}</div>'
                L.t += min(2.4, 0.9 + len(s["dato"]) / 45)
    elif t == "lista":
        a, dur = L.di(s["titulo"], PAUSA["titulo"], voz_de(s, "titulo"))
        its = ""
        for x in s.get("items", [])[:6]:
            b, _ = L.di(x, PAUSA["item"])
            its += f'<li class="ap" {d(b)}><i>{CHECK}</i><span>{e(x)}</span></li>'
        dentro += f"<h2>{palabras(s['titulo'], s.get('destacado'), a, dur)}</h2><ul>{its}</ul>"
    elif t == "versus":
        a, dur = L.di(s["titulo"], PAUSA["titulo"], voz_de(s, "titulo"))
        cols = ""
        for lado in ("izquierda", "derecha"):
            c = s.get(lado, {})
            b, _ = L.di(c.get("titulo", ""), PAUSA[":"])
            its = ""
            for x in c.get("items", [])[:5]:
                b2, _ = L.di(x, PAUSA[","])
                its += f'<li class="ap" {d(b2)}><i>{CHECK}</i><span>{e(x)}</span></li>'
            cols += f'<div class="col ap" {d(b)}><h3>{e(c.get("titulo"))}</h3><ul style="margin-top:0">{its}</ul></div>'
            L.t += 0.2
        dentro += f"<h2>{palabras(s['titulo'], s.get('destacado'), a, dur)}</h2><div class=\"vs\">{cols}</div>"
    return f'<div class="card ap" {d(ini + 0.05)}>{dentro}</div>'


def montar(cfg, voz):
    L = Linea(voz)
    slides = cfg["slides"]
    t, partes, portada_t = 0.0, [], 2.4
    for k, s in enumerate(slides):
        html = escena(s, L, t)
        fin_voz = L.t
        extra = 1.0 if s.get("tipo") == "cierre" else 0
        dur = max(2.6, fin_voz - t + COLA + extra)
        if k == 0:
            portada_t = min(dur - SAL - 0.1, fin_voz - t)
        ultima = k == len(slides) - 1
        estilo = f"--ini:{t:.2f}s;--fin:{t + dur - SAL:.2f}s;--sal:{SAL}s"
        partes.append(f'<section class="esc{" ultima" if ultima else ""}" style="{estilo}">{html}</section>')
        t += dur
    total = t + 0.4
    pagina = f"""<html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="--total:{total:.2f}s">
    {red()}<div class="marca"><div class="logo">{CHIP}</div><span>iando.xyz</span></div>
    {''.join(partes)}</body></html>"""
    return pagina, total, L.trozos, portada_t


def escribir_audio(trozos, total, sr, ruta):
    buf = bytearray(b"\x00\x00" * int((total + 0.5) * sr))
    for ini, audio, _ in trozos:
        o = int(ini * sr) * 2
        buf[o:o + len(audio)] = audio
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(buf))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--salida", default="reels")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--sin-voz", action="store_true")
    ap.add_argument("--guion", action="store_true", help="solo muestra lo que se lee y cuándo")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    voz = Voz(not a.sin_voz)
    html, total, trozos, portada_t = montar(cfg, voz)
    if a.guion:
        for ini, _, txt in trozos:
            print(f"{ini:6.2f}s  {decir(txt)}")
        print(f"Total: {total:.1f} s")
        return
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    mp4 = out / f"{cfg['slug']}.mp4"
    tmp = Path(tempfile.mkdtemp())
    from playwright.sync_api import sync_playwright
    n = int(total * a.fps)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(html)
        pg.wait_for_timeout(300)
        pg.evaluate("document.getAnimations().forEach(x => x.pause())")
        fp = int(portada_t * a.fps)
        for f in range(n):
            ms = f * 1000 / a.fps
            pg.evaluate(f"document.getAnimations().forEach(x => x.currentTime = {ms})")
            pg.screenshot(path=str(tmp / f"{f:05d}.jpg"), type="jpeg", quality=90)
            if f == fp:
                shutil.copy(tmp / f"{f:05d}.jpg", out / f"{cfg['slug']}-portada.jpg")
        b.close()
    if trozos:
        escribir_audio(trozos, total, voz.sr, tmp / "voz.wav")
        audio = ["-i", str(tmp / "voz.wav")]
        filtro = ["-af", "loudnorm=I=-16:TP=-1.5,apad", "-ar", "44100"]
    else:
        audio = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        filtro = []
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", str(tmp / "%05d.jpg"), *audio,
                    "-map", "0:v", "-map", "1:a", *filtro, "-shortest",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-profile:v", "high",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(mp4)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"reel": str(mp4), "portada": str(out / f"{cfg['slug']}-portada.jpg"), "segundos": round(total, 1), "voz": bool(trozos)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
