#!/usr/bin/env python3
"""
Control de calidad de una landing del taller de iando.

    python3 taller/qa_landing.py demos/<slug>/index.html --capturas demos/<slug>/capturas

Abre la página con Chromium (Playwright) en móvil y en ordenador, saca capturas y
comprueba lo que suele fallar. Devuelve un JSON con "errores" (hay que arreglarlos)
y "avisos" (mirarlos). Sale con código 1 si hay errores.

Requiere: pip install playwright (en el entorno del taller ya está con Chromium).
"""
import argparse, json, re, sys
from pathlib import Path


def revisar_html(t: str):
    err, av = [], []
    m = lambda rx: re.search(rx, t, re.S | re.I)
    title = m(r"<title>(.*?)</title>")
    desc = m(r'<meta name="description" content="([^"]*)"')
    if "{{" in t:
        err.append(f"Quedan marcadores de la plantilla sin rellenar: {sorted(set(re.findall(r'{{[A-Z_0-9]+}}', t)))[:8]}")
    if not title or not title[1].strip():
        err.append("Falta <title>")
    elif len(title[1]) > 65:
        av.append(f"El título mide {len(title[1])} caracteres (mejor ≤ 60)")
    if not desc:
        err.append("Falta meta description")
    elif not 70 <= len(desc[1]) <= 160:
        av.append(f"La descripción mide {len(desc[1])} caracteres (mejor 120-155)")
    h1 = re.findall(r"<h1[\s>]", t, re.I)
    if len(h1) != 1:
        err.append(f"Debe haber exactamente un <h1> (hay {len(h1)})")
    if 'name="viewport"' not in t:
        err.append("Falta la etiqueta viewport (móvil)")
    # Datos estructurados
    tipos = []
    for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            j = json.loads(bloque)
            tipos.append(j.get("@type"))
        except Exception as e:
            err.append(f"JSON-LD no válido: {e}")
    if not any(x not in ("FAQPage", "BreadcrumbList", None) for x in tipos):
        err.append("Faltan datos estructurados del negocio (LocalBusiness o tipo concreto)")
    # Contacto
    wa = re.findall(r"https://wa\.me/(\d*)", t)
    if not wa:
        err.append("No hay ningún enlace de WhatsApp")
    elif any(not re.fullmatch(r"34[6-9]\d{8}", n) for n in wa):
        err.append(f"Número de WhatsApp con formato raro: {sorted(set(wa))} (debe ser 34 + 9 cifras)")
    if not re.search(r'href="tel:\+?\d{9,12}"', t):
        av.append("No hay enlace tel: para llamar")
    # Imágenes y textos alternativos
    for img in re.findall(r"<img\b[^>]*>", t, re.I):
        if not re.search(r'\balt="[^"]+"', img):
            err.append("Hay una imagen sin texto alternativo (alt)")
            break
    # Cosas que no deben aparecer
    if re.search(r"lorem ipsum", t, re.I):
        err.append("Queda texto de relleno (lorem ipsum)")
    if re.search(r'"@type":\s*"(Review|AggregateRating)"', t):
        err.append("Hay reseñas o valoraciones en los datos estructurados: no se ponen salvo que sean reales y verificables")
    if re.search(r"(testimonio|opiniones de (nuestros )?clientes|★★★★)", t, re.I):
        av.append("Parece haber testimonios u opiniones: confirma que son reales y que el cliente los ha dado")
    peso = len(t.encode("utf-8"))
    if peso > 1_500_000:
        av.append(f"La página pesa {peso // 1024} KB: comprime las imágenes")
    return err, av, peso


def revisar_navegador(ruta: Path, capturas: Path | None):
    from playwright.sync_api import sync_playwright
    err, av, info = [], [], {}
    url = ruta.resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nombre, ctx_args in (("movil", p.devices["iPhone 13"]), ("ordenador", {"viewport": {"width": 1366, "height": 900}})):
            ctx = b.new_context(**ctx_args)
            pg = ctx.new_page()
            consola = []
            pg.on("pageerror", lambda e: consola.append(str(e)))
            # Fuera de la red solo se permiten las fuentes; el resto (mapas…) no hace falta para revisar
            pg.goto(url, wait_until="load")
            pg.wait_for_timeout(600)
            ancho = pg.evaluate("[document.documentElement.scrollWidth, innerWidth]")
            if ancho[0] > ancho[1] + 1:
                err.append(f"En {nombre} la página se sale por la derecha ({ancho[0]} px de {ancho[1]})")
            # Enlaces internos (#ancla) que no llevan a ningún sitio
            rotos = pg.evaluate("""[...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href')).filter(h => h.length > 1 && !document.getElementById(h.slice(1)))""")
            if rotos:
                err.append(f"Enlaces internos rotos: {sorted(set(rotos))}")
            if nombre == "movil":
                pequenos = pg.evaluate("""[...document.querySelectorAll('a.btn, button, .wa-flota')].filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.height < 40 || r.width < 40); }).length""")
                if pequenos:
                    av.append(f"{pequenos} botones miden menos de 40 px en móvil")
                info["texto_minimo_px"] = pg.evaluate("Math.min(...[...document.querySelectorAll('p, li, td')].map(e => parseFloat(getComputedStyle(e).fontSize)).filter(Boolean))")
                if info["texto_minimo_px"] < 14:
                    av.append(f"Hay texto de {info['texto_minimo_px']} px en móvil (mejor ≥ 15)")
            if consola:
                err.append(f"Errores de JavaScript en {nombre}: {consola[:3]}")
            if capturas:
                capturas.mkdir(parents=True, exist_ok=True)
                pg.screenshot(path=str(capturas / f"{nombre}-inicio.png"))
                pg.screenshot(path=str(capturas / f"{nombre}-completa.png"), full_page=True)
            ctx.close()
        b.close()
    return err, av, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--capturas")
    a = ap.parse_args()
    ruta = Path(a.html)
    t = ruta.read_text(encoding="utf-8")
    e1, a1, peso = revisar_html(t)
    try:
        e2, a2, info = revisar_navegador(ruta, Path(a.capturas) if a.capturas else None)
    except Exception as e:
        e2, a2, info = [], [f"No se pudo abrir en el navegador: {e}"], {}
    res = {"archivo": str(ruta), "peso_kb": peso // 1024, "errores": e1 + e2, "avisos": a1 + a2, **info}
    if a.capturas:
        res["capturas"] = sorted(str(x) for x in Path(a.capturas).glob("*.png"))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(1 if res["errores"] else 0)


if __name__ == "__main__":
    main()
