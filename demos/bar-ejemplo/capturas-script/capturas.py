"""Capturas de la demo con fuentes locales y Supabase simulado (la máquina del taller no llega a la red).
Fuentes: npm pack @fontsource/alfa-slab-one @fontsource/karla y descomprimir en fonts/ junto al script.
Uso: python3 capturas.py <index.html> <admin.html> <carpeta_capturas> [solo_landing]"""
import json, sys, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

S = Path(__file__).parent
F = S / "fonts"
landing, admin, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
NEG = "f3dee622-cdc7-4dab-ae76-5c05eaca225c"
SERV = [{"id": "1281996e-b98b-47f2-9260-0ab5e9618afe", "nombre": "Mesa para comer", "precio_desde": 0, "duracion_minutos": 90},
        {"id": "3e270bcb-cec7-419f-8693-26c10b7d78ba", "nombre": "Mesa para cenar", "precio_desde": 0, "duracion_minutos": 90}]

FONT_CSS = f"""
@font-face {{ font-family: 'Alfa Slab One'; font-weight: 400; src: url('https://local.fonts/alfa.woff2') format('woff2'); }}
@font-face {{ font-family: 'Karla'; font-weight: 400; src: url('https://local.fonts/karla400.woff2') format('woff2'); }}
@font-face {{ font-family: 'Karla'; font-weight: 700; src: url('https://local.fonts/karla700.woff2') format('woff2'); }}
"""
FONTS = {"alfa.woff2": F / "fontsource-alfa-slab-one-5.3.0/package/files/alfa-slab-one-latin-400-normal.woff2",
         "karla400.woff2": F / "fontsource-karla-5.3.0/package/files/karla-latin-400-normal.woff2",
         "karla700.woff2": F / "fontsource-karla-5.3.0/package/files/karla-latin-700-normal.woff2"}

hoy = datetime.date.today()
def d(n): return (hoy + datetime.timedelta(days=n)).isoformat()
RES = [  # reservas de ejemplo para el panel (ficticias)
    {"id": "r1", "fecha": d(1), "hora": "14:00:00", "estado": "confirmada", "notas": "4 personas", "created_at": d(0) + "T10:00:00Z", "clientes": {"nombre": "Lucía (ejemplo)", "telefono": "600000001"}, "servicios": {"nombre": "Mesa para comer"}},
    {"id": "r2", "fecha": d(1), "hora": "21:00:00", "estado": "pendiente", "notas": "6 personas · una trona", "created_at": d(0) + "T11:00:00Z", "clientes": {"nombre": "Antonio (ejemplo)", "telefono": "600000002"}, "servicios": {"nombre": "Mesa para cenar"}},
    {"id": "r3", "fecha": d(2), "hora": "13:30:00", "estado": "pendiente", "notas": "2 personas", "created_at": d(0) + "T12:00:00Z", "clientes": {"nombre": "Marta (ejemplo)", "telefono": "600000003"}, "servicios": {"nombre": "Mesa para comer"}},
    {"id": "r4", "fecha": d(4), "hora": "20:30:00", "estado": "confirmada", "notas": "8 personas · cumpleaños", "created_at": d(0) + "T13:00:00Z", "clientes": {"nombre": "Javier (ejemplo)", "telefono": "600000004"}, "servicios": {"nombre": "Mesa para cenar"}},
]
TEMA = {'nombre': 'Tu bar', 'colores': {'fondo': '#fdfcf9', 'tarjeta': '#ffffff', 'borde': '#ead5d8', 'primario': '#7b1f2e', 'oscuro': '#3a1c20'}, 'fuentes': {'titulos': 'Alfa Slab One', 'texto': 'Karla:wght@400;700'}, 'logo_svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 54" role="img" aria-label="Tu bar"> <rect x="2" y="2" width="146" height="50" rx="8" fill="#fdfcf9"/> <rect x="7" y="7" width="136" height="40" rx="5" fill="none" stroke="#1e3f94" stroke-width="2"/> <text x="75" y="37" text-anchor="middle" font-family="Alfa Slab One, Rockwell, Georgia, serif" font-size="25" fill="#7b1f2e">Tu bar</text> </svg>'}
CFG = {"horario": {"1": [], **{str(i): [["13:30", "16:00"], ["20:30", "23:00"]] for i in range(2, 8)}}, "intervalo_min": 30, "tema": TEMA}

FAKE_SB = """
const DATA = %s;
function q(table){ let rows = (DATA[table]||[]).slice(); const b = {
  select(){return b}, eq(){return b}, neq(){return b}, gte(){return b}, lte(){return b}, lt(){return b}, gt(){return b}, in(){return b},
  order(){return b}, limit(){return b}, range(){return b}, not(){return b}, or(){return b}, filter(){return b}, match(){return b}, is(){return b},
  insert(){return b}, update(){return b}, delete(){return b}, upsert(){return b},
  maybeSingle(){ rows = rows[0]||null; return b }, single(){ rows = rows[0]||null; return b },
  then(res, rej){ return Promise.resolve({data: rows, error: null, count: Array.isArray(rows)?rows.length:1}).then(res, rej) } }; return b; }
export function createClient(){ return {
  from: q, rpc: async () => ({data: [], error: null}),
  channel(){ const c = {on(){return c}, subscribe(){return c}}; return c }, removeChannel(){},
  auth: { getSession: async () => ({data: {session: {user: {id: "u1", email: "demo@iando.xyz"}}}}),
          getUser: async () => ({data: {user: {id: "u1", email: "demo@iando.xyz"}}}),
          onAuthStateChange(){ return {data: {subscription: {unsubscribe(){}}}} }, signOut: async () => ({}), signInWithPassword: async () => ({data:{}, error:null}) } } }
""" % json.dumps({"negocios": [{"nombre": "Bar de ejemplo", "config": CFG}], "reservas": RES, "servicios": SERV, "dias_bloqueados": [], "clientes": []})

def huecos(fecha, servicio):
    wd = datetime.date.fromisoformat(fecha).isoweekday()
    if wd == 1: return []
    h = ["13:30:00", "14:00:00", "14:30:00", "20:30:00", "21:00:00", "21:30:00"]
    return h

def rutas(page):
    def h(route):
        u = route.request.url
        if "fonts.googleapis.com" in u: return route.fulfill(status=200, content_type="text/css", body=FONT_CSS)
        if "local.fonts/" in u: return route.fulfill(status=200, content_type="font/woff2", body=FONTS[u.rsplit("/", 1)[1]].read_bytes())
        if "supabase.co/rest/v1/servicios" in u: return route.fulfill(status=200, content_type="application/json", body=json.dumps(SERV))
        if "rpc/huecos_libres" in u:
            b = json.loads(route.request.post_data or "{}"); return route.fulfill(status=200, content_type="application/json", body=json.dumps(huecos(b["p_fecha"], b["p_servicio_id"])))
        if "rpc/reservar_hueco" in u: return route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "reserva_id": "x"}))
        if "supabase-js" in u: return route.fulfill(status=200, content_type="application/javascript", body=FAKE_SB)
        if "google.com/maps" in u: return route.fulfill(status=200, content_type="text/html", body="<body style='margin:0;background:#e8edf7;display:grid;place-items:center;height:100vh;font:16px sans-serif;color:#4a5470'>Mapa de Oropesa (Toledo)</body>")
        if u.startswith("file:") or u.startswith("data:"): return route.continue_()
        return route.abort()
    page.route("**/*", h)

with sync_playwright() as p:
    b = p.chromium.launch()
    for nombre, args in (("movil", p.devices["iPhone 13"]), ("ordenador", {"viewport": {"width": 1366, "height": 900}})):
        ctx = b.new_context(**args); pg = ctx.new_page(); rutas(pg)
        pg.goto(landing.as_uri(), wait_until="load"); pg.wait_for_timeout(900)
        pg.screenshot(path=str(out / f"{nombre}-inicio.png"))
        pg.screenshot(path=str(out / f"{nombre}-completa.png"), full_page=True)
        if nombre == "movil":
            # recorrido de reserva
            pg.click('[data-turno="cenar"]'); pg.click('[data-p="4"]')
            dias = pg.locator("#rv-dias .opc"); dias.nth(min(3, dias.count() - 1)).click(); pg.wait_for_timeout(400)
            pg.click('#rv-horas [data-h="21:30"]')
            pg.fill("#rv-nombre", "Lucía (ejemplo)"); pg.fill("#rv-tel", "600 000 000"); pg.check("#rv-ok")
            pg.locator("#rv-form legend").first.scroll_into_view_if_needed(); pg.evaluate("window.scrollBy(0,-20)")
            pg.wait_for_timeout(300); pg.screenshot(path=str(out / "movil-reserva.png"))
            pg.locator("#rv-dias").scroll_into_view_if_needed(); pg.evaluate("window.scrollBy(0, 120)"); pg.wait_for_timeout(200)
            pg.screenshot(path=str(out / "movil-reserva-hora.png"))
            pg.locator("#rv-enviar").scroll_into_view_if_needed(); pg.wait_for_timeout(200)
            pg.screenshot(path=str(out / "movil-reserva-datos.png"))
            pg.click("#rv-enviar"); pg.wait_for_timeout(500)
            pg.locator("#rv-hecha").scroll_into_view_if_needed(); pg.evaluate("window.scrollBy(0,-120)"); pg.wait_for_timeout(200)
            pg.screenshot(path=str(out / "movil-reserva-hecha.png"))
        ctx.close()
    if len(sys.argv) < 5:
        for nombre, args in (("panel-movil", p.devices["iPhone 13"]), ("panel-ordenador", {"viewport": {"width": 1366, "height": 900}})):
            ctx = b.new_context(**args); pg = ctx.new_page(); rutas(pg)
            errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(admin.as_uri() + "?n=" + NEG, wait_until="load"); pg.wait_for_timeout(1500)
            pg.screenshot(path=str(out / f"{nombre}.png"))
            if errs: print(nombre, "errores JS:", errs[:3])
            ctx.close()
    b.close()
print("ok")
