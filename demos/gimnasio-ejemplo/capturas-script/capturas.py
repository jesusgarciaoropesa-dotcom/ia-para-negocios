"""Capturas de la demo y del panel con las fuentes y los datos servidos en local
(la máquina del taller no llega a Google Fonts ni a Supabase). Datos de ejemplo ficticios."""
import json, os, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "demos/gimnasio-ejemplo/index.html"
ADMIN = REPO / "taller/reservas/admin.html"
OUT = REPO / "demos/gimnasio-ejemplo/capturas"
FM = Path(os.environ.get("FONTS_DIR", "fonts/node_modules"))  # npm i @fontsource/teko @fontsource/libre-franklin @fontsource/caveat
MOCK = Path(__file__).with_name("mock-supabase.js")
NEG = "aeedc47b-13f6-43b6-8883-61281aa68453"

F = lambda fam, w: FM / f"@fontsource/{fam}/files/{fam}-latin-{w}-normal.woff2"
FONTS = {
    "Teko": [(f"tk{w}", F("teko", w), str(w), None) for w in (500, 600)],
    "Libre Franklin": [(f"lf{w}", F("libre-franklin", w), str(w), None) for w in (400, 600, 700)],
    "Caveat": [("ca600", F("caveat", 600), "600", None)],
}
ARCH = {k: p for fam in FONTS.values() for k, p, *_ in fam}
CSS = ""
for fam, items in FONTS.items():
    for k, p, w, st in items:
        CSS += f"@font-face{{font-family:'{fam}';src:url(https://fonts.gstatic.com/local/{k}.woff2) format('woff2');font-weight:{w};{'font-stretch:'+st+';' if st else ''}font-display:block}}\n"

SERVS = [
    {"id": "f2b80a68-0f6c-4e77-94a5-af5ecf3efbee", "nombre": "Primera visita y valoración", "precio_desde": 0, "duracion_minutos": 30},
    {"id": "047d3b5a-5301-4df4-aa07-c0c9b58bec71", "nombre": "Entrenamiento personal", "precio_desde": 0, "duracion_minutos": 60},
    {"id": "f43169b6-0cc1-49e6-859e-f207f9345667", "nombre": "Clase de funcional", "precio_desde": 0, "duracion_minutos": 45},
]
HORAS = ["07:00:00", "07:30:00", "09:00:00", "10:30:00", "12:00:00", "17:00:00", "18:00:00", "19:30:00", "20:30:00"]


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
    ctx.route(re.compile(r"https://(www|maps)\.google\.com/maps.*"), lambda r: r.fulfill(status=200, content_type="text/html",
              body="<body style='margin:0;background:#dfe3e6;font:15px sans-serif;display:grid;place-items:center;height:100vh;color:#4d5866'>Mapa</body>"))


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
            pg.add_style_tag(content=".wa-flota{display:none!important} header{position:static!important}")
            caja = lambda: pg.locator("#reservar .reserva")
            def foto(arch):
                bb = caja().bounding_box(); sy = pg.evaluate("scrollY")
                pg.screenshot(path=str(OUT / arch), full_page=True, clip={"x": 0, "y": bb["y"] + sy - 16, "width": 390, "height": bb["height"] + 32})
            pg.select_option("#rv-serv", index=1)
            pg.select_option("#rv-fecha", index=1)
            foto("movil-servicio.png")
            pg.click("#rv-sig1")
            pg.wait_for_selector("#rv-horas button")
            pg.click("#rv-horas button >> nth=0")
            foto("movil-pedir-cita.png")
            pg.click("#rv-sig2")
            pg.fill("#rv-nombre", "Pablo")
            pg.fill("#rv-tel", "600 123 456")
            pg.fill("#rv-email", "pablo@ejemplo.com")
            pg.fill("#rv-notas", "Es mi primera vez en un gimnasio")
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
