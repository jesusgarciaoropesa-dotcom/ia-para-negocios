"""Capturas de la demo y del panel con las fuentes y los datos servidos en local
(la máquina del taller no llega a Google Fonts ni a Supabase). Datos de ejemplo ficticios."""
import json, os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "demos/taller-ejemplo/index.html"
ADMIN = REPO / "taller/reservas/admin.html"
OUT = REPO / "demos/taller-ejemplo/capturas"
FM = Path(os.environ.get("FONTS_DIR", "fonts/node_modules"))  # npm i @fontsource/saira @fontsource/barlow @fontsource/caveat
MOCK = Path(__file__).with_name("mock-supabase.js")
NEG = "cae3656f-c76b-490b-b0e4-4aef72d08952"

F = lambda fam, w: FM / f"@fontsource/{fam}/files/{fam}-latin-{w}-normal.woff2"
FONTS = {
    "Saira": [(f"sa{w}", F("saira", w), str(w), None) for w in (700, 800)],
    "Barlow": [(f"ba{w}", F("barlow", w), str(w), None) for w in (400, 500, 600, 700)],
    "Caveat": [("ca600", F("caveat", 600), "600", None)],
}
ARCH = {k: p for fam in FONTS.values() for k, p, *_ in fam}
CSS = ""
for fam, items in FONTS.items():
    for k, p, w, st in items:
        CSS += f"@font-face{{font-family:'{fam}';src:url(https://fonts.gstatic.com/local/{k}.woff2) format('woff2');font-weight:{w};{'font-stretch:'+st+';' if st else ''}font-display:block}}\n"

SERVS = [
    {"id": "c06ea1cd-01fc-427b-b63f-405c590ddc8d", "nombre": "Revisión de frenos", "precio_desde": 0, "duracion_minutos": 60},
    {"id": "a42d8ed0-fba2-49b3-a62e-b71215bb961c", "nombre": "Cambio de aceite y filtros", "precio_desde": 0, "duracion_minutos": 45},
    {"id": "e2a16e06-d64a-4254-9302-1426764fa8bf", "nombre": "Pre-ITV", "precio_desde": 0, "duracion_minutos": 45},
    {"id": "04c9d630-ffb6-4901-9272-b34900129fad", "nombre": "Diagnosis de avería", "precio_desde": 0, "duracion_minutos": 60},
    {"id": "1d3d5919-d386-4c88-bf6b-1802f452e723", "nombre": "Cambio de neumáticos", "precio_desde": 0, "duracion_minutos": 45},
    {"id": "a4de2131-4eb0-4a18-b695-283e094e4135", "nombre": "Batería", "precio_desde": 0, "duracion_minutos": 30},
    {"id": "ec78d0b2-0596-4eab-85f2-19473f627465", "nombre": "Aire acondicionado", "precio_desde": 0, "duracion_minutos": 60},
]
HORAS = ["08:30:00", "09:00:00", "11:00:00", "11:30:00", "12:00:00", "12:30:00", "15:30:00", "16:30:00", "17:00:00", "18:00:00"]


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
    ctx.route(re.compile(r"https://maps\.google\.com/"), lambda r: r.fulfill(status=200, content_type="text/html",
              body="<body style='margin:0;height:100vh;background:#e8eaed linear-gradient(90deg,transparent 47%,#fff 47%,#fff 53%,transparent 53%),linear-gradient(0deg,transparent 47%,#fde293 47%,#fde293 53%,transparent 53%);display:grid;place-items:center;font:600 15px sans-serif;color:#3c4043'><span style='background:#fff;padding:6px 10px;border-radius:6px;box-shadow:0 1px 4px #0003'>&#128205; Oropesa (Toledo)</span></body>"))
    ctx.route("https://www.google.com/maps**", lambda r: r.fulfill(status=200, content_type="text/html",
              body="<body style='margin:0;background:#dfe5f0;font:15px sans-serif;display:grid;place-items:center;height:100vh;color:#4d5866'>Mapa</body>"))


with sync_playwright() as p:
    b = p.chromium.launch(args=["--lang=es-ES"])
    # Landing en móvil y ordenador
    for nombre, args in (("movil", p.devices["iPhone 13"]), ("ordenador", {"viewport": {"width": 1366, "height": 900}})):
        ctx = b.new_context(**args, locale="es-ES", timezone_id="Europe/Madrid")
        rutas(ctx)
        pg = ctx.new_page()
        pg.goto(DEMO.as_uri(), wait_until="networkidle")
        pg.locator(".mapa").scroll_into_view_if_needed()
        pg.wait_for_timeout(1200)
        pg.evaluate("scrollTo(0, 0)")
        pg.wait_for_timeout(300)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / f"{nombre}-inicio.png"))
        pg.screenshot(path=str(OUT / f"{nombre}-completa.png"), full_page=True)
        if nombre == "movil":
            pg.add_style_tag(content=".wa-flota{display:none!important} header{position:static!important}")
            caja = lambda: pg.locator("#reservar .res-caja")
            def foto(arch):
                bb = caja().bounding_box(); sy = pg.evaluate("scrollY")
                pg.screenshot(path=str(OUT / arch), full_page=True, clip={"x": 0, "y": bb["y"] + sy - 16, "width": 390, "height": bb["height"] + 32})
            pg.click("#rv-servs button >> nth=1")
            foto("movil-servicio.png")
            pg.click("#rv-sig1")
            pg.click("#rv-dias button >> nth=1")
            pg.wait_for_selector("#rv-horas button")
            pg.click("#rv-horas button >> nth=2")
            foto("movil-pedir-cita.png")
            pg.click("#rv-sig2")
            pg.fill("#rv-nombre", "Marta")
            pg.fill("#rv-tel", "600 123 456")
            pg.fill("#rv-email", "marta@ejemplo.com")
            pg.fill("#rv-notas", "Seat Ibiza, chirría la rueda delantera")
            pg.check("#rv-ok")
            foto("movil-datos.png")
            pg.click("#rv-enviar")
            pg.wait_for_selector('.paso[data-paso="4"]:not([hidden])')
            pg.wait_for_timeout(200)
            foto("movil-cita-hecha.png")
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
