#!/usr/bin/env python3
"""
Genera las láminas de un carrusel de iando (Instagram/Facebook) a partir de un JSON.

    python3 herramientas/redes/generar_carrusel.py configs/<slug>.json [--salida carruseles]

Crea carruseles/<slug>/01.jpg, 02.jpg… (1080x1350, 4:5) y carruseles/<slug>/historia.jpg (1080x1920).
Son láminas de diseño (sin fotos): degradado de la marca, tipografía Inter incluida en el repo.

Tipos de lámina (campo "tipo"):
  portada  {kicker, titulo, destacado?, subtitulo?}          → primera lámina
  punto    {num?, titulo, texto, dato?}                       → una idea por lámina
  lista    {titulo, items: [..] (3-5)}                        → checklist corta
  versus   {titulo, izquierda:{titulo,items}, derecha:{titulo,items}} → comparación
  cierre   {titulo, texto?, cta?}                             → última lámina (guía en la web / te lo monto)
"""
import argparse, base64, html, json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
F = AQUI / "fuentes"


def fuente(peso):
    b = base64.b64encode((F / f"inter-latin-{peso}-normal.woff2").read_bytes()).decode()
    return f"@font-face{{font-family:Inter;font-weight:{peso};src:url(data:font/woff2;base64,{b}) format('woff2')}}"


CSS = "".join(fuente(p) for p in (400, 600, 800)) + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;font-family:Inter,sans-serif;overflow:hidden}
.l{position:relative;width:1080px;height:1350px;padding:96px 88px;display:flex;flex-direction:column}
.g{background:linear-gradient(140deg,#4f46e5 0%,#6366f1 45%,#8b5cf6 100%);color:#fff}
.c{background:#f6f6fb;color:#1e1b4b}
.red{position:absolute;inset:0;opacity:.13;pointer-events:none}
.top{display:flex;align-items:center;gap:18px;font-weight:600;font-size:30px;letter-spacing:.5px}
.logo{width:58px;height:58px;border-radius:14px;background:linear-gradient(140deg,#6366f1,#8b5cf6);display:grid;place-items:center}
.g .logo{background:rgba(255,255,255,.18)}
.kicker{display:inline-block;align-self:flex-start;font-weight:800;font-size:30px;letter-spacing:3px;text-transform:uppercase;padding:14px 26px;border-radius:999px;background:rgba(255,255,255,.18)}
.c .kicker{background:#e0e7ff;color:#4338ca}
h1{font-weight:800;font-size:104px;line-height:1.02;letter-spacing:-3px}
h2{font-weight:800;font-size:78px;line-height:1.06;letter-spacing:-2px}
.dest{background:linear-gradient(transparent 62%,#facc15 62%,#facc15 92%,transparent 92%);color:inherit}
.g .dest{color:#fde68a;background:none}
.sub{font-size:44px;line-height:1.3;font-weight:400;opacity:.92}
.txt{font-size:46px;line-height:1.38;color:#3730a3}
.num{width:132px;height:132px;border-radius:34px;background:linear-gradient(140deg,#6366f1,#8b5cf6);color:#fff;font-weight:800;font-size:72px;display:grid;place-items:center}
.dato{background:#fff;border-left:12px solid #8b5cf6;border-radius:24px;padding:36px 40px;font-size:38px;line-height:1.35;color:#312e81;box-shadow:0 10px 30px rgba(79,70,229,.10)}
.dato b{font-weight:800}
ul{list-style:none;display:flex;flex-direction:column;gap:30px}
li{display:flex;gap:28px;align-items:flex-start;font-size:44px;line-height:1.3;color:#312e81}
li i{flex:none;width:58px;height:58px;border-radius:50%;background:#6366f1;display:grid;place-items:center;margin-top:2px}
.vs{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:56px;flex:1}
.col{background:#fff;border-radius:28px;padding:40px 34px;box-shadow:0 10px 30px rgba(79,70,229,.10)}
.col h3{font-size:44px;font-weight:800;margin-bottom:26px;color:#4338ca}
.col li{font-size:36px;gap:18px}
.col li i{width:42px;height:42px}
.pie{position:absolute;left:88px;right:88px;bottom:64px;display:flex;justify-content:space-between;align-items:center;font-size:30px;font-weight:600;opacity:.75}
.pill{background:#fff;color:#4f46e5;font-weight:800;font-size:36px;padding:22px 38px;border-radius:999px;align-self:flex-start}
.cta{margin-top:40px;background:rgba(255,255,255,.14);border:2px solid rgba(255,255,255,.35);border-radius:28px;padding:34px 38px;font-size:40px;line-height:1.35}
.esp{flex:1}
.centro{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:40px}
.dato{margin-top:56px}
body.h{height:1920px}.h .l{height:1920px;padding:150px 96px}
"""

CHIP = """<svg width="34" height="34" viewBox="0 0 20 20" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="8" height="8" rx="1"/><path d="M8 6V3M11 6V3M14 6V3M8 14v3M11 14v3M14 14v3M6 8H3M6 11H3M6 14H3M14 8h3M14 11h3M14 14h3"/></svg>"""
CHECK = """<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>"""


def red(alto=1350):
    # Líneas de circuito suaves (siempre iguales para que el perfil se vea uniforme)
    import random
    r = random.Random(11)
    d = []
    for _ in range(26):
        x, y, L = r.randint(0, 1080), r.randint(0, alto), r.randint(60, 220)
        v = r.choice([-1, 1]) * r.randint(30, 90)
        d.append(f'<path d="M{x} {y}h{L}v{v}"/><circle cx="{x}" cy="{y}" r="6"/>')
    return f'<svg class="red" viewBox="0 0 1080 {alto}"><g stroke="#fff" stroke-width="3" fill="none">{"".join(d)}</g></svg>'


def e(t):
    return html.escape(str(t or ""))


def resaltar(titulo, destacado):
    t = e(titulo)
    if destacado and e(destacado) in t:
        t = t.replace(e(destacado), f'<span class="dest">{e(destacado)}</span>', 1)
    return t


def cabecera(oscuro):
    return f'<div class="top"><div class="logo">{CHIP}</div><span>iando.xyz</span></div>'


def pie(i, n, oscuro):
    flecha = "Desliza →" if i < n else "Guárdalo"
    return f'<div class="pie"><span>IA para negocios</span><span>{i}/{n} · {flecha}</span></div>'


def lamina(s, i, n):
    t = s.get("tipo", "punto")
    if t == "portada":
        cuerpo = f"""{red()}{cabecera(True)}<div class="esp"></div>
        <span class="kicker">{e(s.get('kicker'))}</span>
        <h1 style="margin-top:44px">{resaltar(s['titulo'], s.get('destacado'))}</h1>
        {f'<p class="sub" style="margin-top:40px">{e(s.get("subtitulo"))}</p>' if s.get('subtitulo') else ''}
        <div style="height:150px"></div>"""
        return "g", cuerpo + pie(i, n, True)
    if t == "cierre":
        cuerpo = f"""{red()}{cabecera(True)}<div class="esp"></div>
        <h2 style="font-size:88px">{resaltar(s['titulo'], s.get('destacado'))}</h2>
        {f'<p class="sub" style="margin-top:36px">{e(s.get("texto"))}</p>' if s.get('texto') else ''}
        <div class="cta">{e(s.get('cta') or '¿Prefieres que te lo monten? Webs, reservas y automatizaciones para tu negocio. Enlace en la bio.')}</div>
        <div style="height:150px"></div>"""
        return "g", cuerpo + pie(i, n, True)
    if t == "lista":
        items = "".join(f"<li><i>{CHECK}</i><span>{e(x)}</span></li>" for x in s.get("items", [])[:6])
        cuerpo = f"""{cabecera(False)}<div class="centro">
        <h2>{resaltar(s['titulo'], s.get('destacado'))}</h2><div style="height:64px"></div><ul>{items}</ul></div><div style="height:90px"></div>"""
        return "c", cuerpo + pie(i, n, False)
    if t == "versus":
        def col(c):
            its = "".join(f"<li><i>{CHECK}</i><span>{e(x)}</span></li>" for x in c.get("items", [])[:5])
            return f'<div class="col"><h3>{e(c.get("titulo"))}</h3><ul>{its}</ul></div>'
        cuerpo = f"""{cabecera(False)}<div style="height:70px"></div><h2>{resaltar(s['titulo'], s.get('destacado'))}</h2>
        <div class="vs">{col(s.get('izquierda', {}))}{col(s.get('derecha', {}))}</div><div style="height:110px"></div>"""
        return "c", cuerpo + pie(i, n, False)
    # punto
    num = f'<div class="num">{e(s.get("num"))}</div><div style="height:56px"></div>' if s.get("num") else ""
    dato = f'<div class="dato">{s_dato(s.get("dato"))}</div>' if s.get("dato") else ""
    cuerpo = f"""{cabecera(False)}<div class="centro">{num}
    <h2>{resaltar(s['titulo'], s.get('destacado'))}</h2>
    <p class="txt" style="margin-top:40px">{e(s.get('texto'))}</p>{dato}</div><div style="height:90px"></div>"""
    return "c", cuerpo + pie(i, n, False)


def s_dato(t):
    # **negrita** sencilla
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(t))


def historia(portada):
    cuerpo = f"""{red(1920)}{cabecera(True)}<div class="esp"></div>
    <span class="kicker">{e(portada.get('kicker'))}</span>
    <h1 style="margin-top:50px;font-size:112px">{resaltar(portada['titulo'], portada.get('destacado'))}</h1>
    {f'<p class="sub" style="margin-top:44px">{e(portada.get("subtitulo"))}</p>' if portada.get('subtitulo') else ''}
    <div style="height:90px"></div><span class="pill">Nuevo post · míralo 👆</span><div style="height:260px"></div>"""
    return cuerpo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--salida", default="carruseles")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    slides = cfg["slides"]
    if not 3 <= len(slides) <= 10:
        sys.exit("Un carrusel necesita entre 3 y 10 láminas")
    if slides[0].get("tipo") != "portada":
        sys.exit("La primera lámina tiene que ser de tipo 'portada'")
    out = Path(a.salida) / cfg["slug"]
    out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    hechos = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            clase, cuerpo = lamina(s, i, len(slides))
            pg.set_content(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='l {clase}'>{cuerpo}</div></body></html>")
            pg.wait_for_timeout(150)
            desborda = pg.evaluate("(() => { const l = document.querySelector('.l'); return l.scrollHeight > l.clientHeight + 2 || l.scrollWidth > l.clientWidth + 2; })()")
            if desborda:
                print(f"AVISO: la lámina {i} tiene demasiado texto y se sale; acórtalo", file=sys.stderr)
            ruta = out / f"{i:02d}.jpg"
            pg.screenshot(path=str(ruta), type="jpeg", quality=92)
            hechos.append(str(ruta))
        pg.set_viewport_size({"width": 1080, "height": 1920})
        pg.set_content(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body class='h'><div class='l g'>{historia(slides[0])}</div></body></html>")
        pg.wait_for_timeout(150)
        pg.screenshot(path=str(out / "historia.jpg"), type="jpeg", quality=92)
        b.close()
    print(json.dumps({"laminas": hechos, "historia": str(out / "historia.jpg")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
