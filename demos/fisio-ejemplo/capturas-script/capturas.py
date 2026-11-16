"""Capturas de la demo y del panel con las fuentes y los datos servidos en local
(la máquina del taller no llega a Google Fonts ni a Supabase). Datos de ejemplo ficticios."""
import json, os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "demos/fisio-ejemplo/index.html"
ADMIN = REPO / "taller/reservas/admin.html"
OUT = REPO / "demos/fisio-ejemplo/capturas"
FM = Path(os.environ.get("FONTS_DIR", "fonts/node_modules"))  # npm i @fontsource/young-serif @fontsource/hanken-grotesk
MOCK = Path(__file__).with_name("mock-supabase.js")
NEG = "beeb6aaf-606b-4217-bf45-388965f660ac"

FONTS = {
    "Young Serif": [("ys4", FM / "@fontsource/young-serif/files/young-serif-latin-400-normal.woff2", "400", None)],
    "Hanken Grotesk": [("hg4", FM / "@fontsource/hanken-grotesk/files/hanken-grotesk-latin-400-normal.woff2", "400", None),
                       ("hg6", FM / "@fontsource/hanken-grotesk/files/hanken-grotesk-latin-600-normal.woff2", "600", None),
                       ("hg7", FM / "@fontsource/hanken-grotesk/files/hanken-grotesk-latin-700-normal.woff2", "700", None)],
}
ARCH = {k: p for fam in FONTS.values() for k, p, *_ in fam}
CSS = ""
for fam, items in FONTS.items():
    for k, p, w, st in items:
        CSS += f"@font-face{{font-family:'{fam}';src:url(https://fonts.gstatic.com/local/{k}.woff2) format('woff2');font-weight:{w};{'font-stretch:'+st+';' if st else ''}font-display:block}}\n"

SERVS = [
    {"id": "s1", "nombre": "Primera valoración", "precio_desde": 0, "duracion_minutos": 45},
    {"id": "s2", "nombre": "Sesión de fisioterapia", "precio_desde": 0, "duracion_minutos": 50},
    {"id": "s3", "nombre": "Punción seca", "precio_desde": 0, "duracion_minutos": 30},
    {"id": "s4", "nombre": "Masaje descontracturante", "precio_desde": 0, "duracion_minutos": 45},
]
HORAS = ["09:00:00", "10:30:00", "11:00:00", "12:30:00", "13:00:00", "16:00:00", "17:30:00", "18:00:00", "19:00:00", "19:30:00"]


def rutas(ctx):
    ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=CSS))
    ctx.route("https://fonts.gstatic.com/local/*", lambda r: r.fulfill(status=200, content_type="font/woff2",
              body=ARCH[re.search(r"/local/(\w+)\.woff2", r.request.url)[1]].read_bytes()))
    ctx.route("https://cdn.jsdelivr.net/npm/@supabase/**", lambda r: r.fulfill(status=200, content_type="application/javascript", body=MOCK.read_text()))
    def sb(r):
        u = r.request.url
        if "/rest/v1/servicios" in u: body = SERVS
        elif "huecos_libres" in u: body = HORAS
        elif "reservar_hueco" in u: body = {"ok": True, "reserva_id": "demo"}
        else: body = []
        r.fulfill(status=200, content_type="application/json", body=json.dumps(body), headers={"access-control-allow-origin": "*"})
    ctx.route("https://gimoqpusrdltlkrwsykr.supabase.co/**", sb)
    ctx.route("https://www.google.com/maps**", lambda r: r.fulfill(status=200, content_type="text/html",
              body="<body style='margin:0;background:#fbeaf0;font:15px sans-serif;display:grid;place-items:center;height:100vh;color:#5a6070'>Mapa</body>"))


with sync_playwright() as p:
    b = p.chromium.launch(args=["--lang=es-ES"])
    # Landing en móvil y ordenador
    for nombre, args in (("movil", p.devices["iPhone 13"]), ("ordenador", {"viewport": {"width": 1366, "height": 900}})):
        ctx = b.new_context(**args, locale="es-ES", timezone_id="Europe/Madrid")
        rutas(ctx)
        pg = ctx.new_page()
        pg.goto(DEMO.as_uri(), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / f"{nombre}-inicio.png"))
        pg.screenshot(path=str(OUT / f"{nombre}-completa.png"), full_page=True)
        if nombre == "movil":
            pg.click("#rv-servs button >> nth=0")
            pg.click("#rv-dias button >> nth=1")
            pg.wait_for_selector("#rv-horas button")
            pg.click("#rv-horas button >> nth=2")
            pg.fill("#rv-nombre", "Marta")
            pg.fill("#rv-tel", "600 123 456")
            pg.fill("#rv-email", "marta@ejemplo.com")
            pg.fill("#rv-notas", "Molestia en el hombro derecho desde hace dos semanas")
            pg.check("#rv-ok")
            pg.add_style_tag(content=".wa-flota{display:none!important}")
            pg.locator("#reservar .hoja").scroll_into_view_if_needed()
            bb = pg.locator(".hoja").bounding_box(); sy = pg.evaluate("scrollY")
            pg.screenshot(path=str(OUT / "movil-pedir-cita.png"), full_page=True, clip={"x": 0, "y": bb["y"] + sy - 40, "width": 390, "height": bb["height"] + 64})
            pg.click("#rv-enviar")
            pg.wait_for_selector(".rv-estado.ok")
            bb = pg.locator(".hoja").bounding_box(); sy = pg.evaluate("scrollY")
            pg.screenshot(path=str(OUT / "movil-cita-hecha.png"), full_page=True, clip={"x": 0, "y": bb["y"] + sy - 40, "width": 390, "height": bb["height"] + 64})
        ctx.close()
    # Panel de citas
    for nombre, args in (("movil", p.devices["iPhone 13"]), ("ordenador", {"viewport": {"width": 1366, "height": 900}})):
        ctx = b.new_context(**args, locale="es-ES", timezone_id="Europe/Madrid")
        rutas(ctx)
        pg = ctx.new_page()
        pg.goto(ADMIN.as_uri() + "?n=" + NEG, wait_until="networkidle")
        pg.wait_for_selector(".reserva")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / f"panel-{nombre}.png"), full_page=(nombre == "ordenador"))
        if nombre == "ordenador":
            pg.click('.tab[data-tab="agenda"]')
            pg.fill("#agFecha", pg.evaluate("window.__DEMO_MANANA"))
            pg.dispatch_event("#agFecha", "change")
            pg.wait_for_selector(".slot")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / "panel-agenda.png"), full_page=True)
        ctx.close()
    b.close()
print(sorted(x.name for x in OUT.glob("*.png")))
