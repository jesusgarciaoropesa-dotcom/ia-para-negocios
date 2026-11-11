"""
Piezas visuales de las láminas de iando (las usan generar_carrusel.py y generar_reel.py).

Cada pieza es una función que devuelve HTML. El parámetro `ap` (opcional) recibe el índice de cada
elemento animable y devuelve atributos extra (en el reel: clase de aparición y retardo; en el
carrusel no se usa y todo sale quieto).

Iconos: nombres de Lucide (ISC) guardados en iconos/ (p. ej. "receipt", "calendar", "star").
Si el nombre no existe se usa tal cual (vale un emoji) y, si está vacío, "sparkles".
"""
import html
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ICONOS = AQUI / "iconos"


def e(t):
    return html.escape(str(t if t is not None else ""))


def negrita(t):
    """**negrita** y [hueco] resaltado."""
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(t))
    return re.sub(r"\[(.+?)\]", r'<b class="hueco">[\1]</b>', t)


def nada(_i):
    return ""


def iconos_disponibles():
    return sorted(p.stem for p in ICONOS.glob("*.svg"))


def icono(nombre, tam=56, color="currentColor", grosor=2):
    nombre = (nombre or "sparkles").strip()
    f = ICONOS / f"{nombre}.svg"
    if not f.exists():
        return f'<span class="emo" style="font-size:{tam}px;line-height:1">{e(nombre)}</span>'
    s = f.read_text(encoding="utf-8")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()
    s = re.sub(r'\swidth="24"', f' width="{tam}"', s, count=1)
    s = re.sub(r'\sheight="24"', f' height="{tam}"', s, count=1)
    s = s.replace('stroke="currentColor"', f'stroke="{color}"').replace('stroke-width="2"', f'stroke-width="{grosor}"')
    return s


CSS = """
.hueco{color:#5b5bd6;font-weight:800}
.emo{display:inline-block}
/* ---------- móvil con chat ---------- */
.movil{width:470px;border-radius:66px;background:#141327;padding:16px;box-shadow:0 40px 90px rgba(40,30,120,.30);flex:none}
.movil .pant{border-radius:52px;overflow:hidden;background:#efe7dc;display:flex;flex-direction:column;color:#17162b;min-height:760px}
.movil.asistente .pant{background:#fff}
.movil .cab{background:#1f5f4f;color:#fff;padding:54px 26px 20px;font-size:25px;font-weight:700;display:flex;gap:14px;align-items:center}
.movil.asistente .cab{background:#17162b}
.movil .av{width:50px;height:50px;border-radius:50%;background:#f3c27a;display:grid;place-items:center;color:#5a3a10;font-size:20px;font-weight:800;flex:none}
.movil.asistente .av{background:#5b5bd6;color:#fff}
.movil .cab small{display:block;font-weight:400;font-size:18px;opacity:.8}
.chat{padding:22px 18px 26px;display:flex;flex-direction:column;gap:13px;font-size:23px;line-height:1.32}
.bur{max-width:84%;padding:13px 17px;border-radius:20px;box-shadow:0 1px 1px rgba(0,0,0,.08);white-space:pre-line}
.bur.in{background:#fff;align-self:flex-start;border-top-left-radius:5px}
.bur.out{background:#d7f8c8;align-self:flex-end;border-top-right-radius:5px}
.asistente .bur.in{background:#f1f0fb}
.asistente .bur.out{background:#5b5bd6;color:#fff}
.bur small{display:block;text-align:right;font-size:15px;color:#8a8a8a;margin-top:4px}
.asistente .bur.out small{color:#d9d6ff}
.botones{display:flex;flex-wrap:wrap;gap:8px}
.boton{background:#fff;border:2px solid #1f5f4f;color:#1f5f4f;border-radius:30px;padding:8px 18px;font-size:21px;font-weight:600}
.asistente .boton{border-color:#5b5bd6;color:#5b5bd6}
/* ---------- ventana (tabla / prompt) ---------- */
.ven{background:#fff;border-radius:30px;box-shadow:0 30px 80px rgba(40,30,120,.16);overflow:hidden;width:100%}
.ven .vbar{height:60px;background:#eceaf6;display:flex;align-items:center;gap:10px;padding:0 22px}
.ven .vbar i{width:16px;height:16px;border-radius:50%;background:#d2cfe6;display:block}
.ven .vbar span{margin-left:16px;background:#fff;border-radius:14px;padding:7px 18px;font-size:20px;color:#8a88a6;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tabla{width:100%;border-collapse:collapse;font-size:30px}
.tabla th{background:#f3f2ff;text-align:left;padding:20px 22px;font-size:21px;color:#55537a;text-transform:uppercase;letter-spacing:.04em;font-weight:700}
.tabla td{padding:24px 22px;border-top:1px solid #eeedf5;color:#17162b}
.tabla td.bien{color:#1f8a5b;font-weight:800}.tabla td.mal{color:#d64545;font-weight:800}
.tabla td:first-child{font-weight:700}
.prompt{padding:46px 50px 52px;font-size:48px;line-height:1.42;font-weight:500;color:#17162b}
.prompt .quien{display:block;color:#8a88a6;font-size:28px;font-weight:700;margin-bottom:12px}
.globo{background:#17162b;color:#fff;border-radius:28px;padding:30px 34px;font-size:33px;line-height:1.32;font-weight:600;box-shadow:0 20px 50px rgba(0,0,0,.18);display:flex;gap:20px;align-items:flex-start}
.globo b{color:#ffd45c}
.globo.lila{background:#5b5bd6}
.globo svg{flex:none;margin-top:2px}
/* ---------- tarjetas ---------- */
.tarjetas{display:flex;flex-direction:column;gap:24px}
.tj{background:#fff;border-radius:30px;padding:30px 32px;box-shadow:0 10px 34px rgba(40,30,120,.08);display:flex;gap:28px;align-items:center}
.tj .ic{width:104px;height:104px;border-radius:28px;background:#eeedff;color:#4f46e5;display:grid;place-items:center;flex:none}
.tj b{display:block;font-size:38px;line-height:1.15;letter-spacing:-.01em;color:#17162b;margin-bottom:8px}
.tj span{font-size:29px;color:#55537a;line-height:1.32;display:block}
.tarjetas.rejilla{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.tarjetas.rejilla .tj{flex-direction:column;align-items:flex-start;gap:18px}
/* ---------- pasos ---------- */
.pasos{display:flex;flex-direction:column;gap:0;position:relative}
.ps{display:flex;gap:34px;align-items:flex-start;padding-bottom:46px;position:relative}
.ps:not(:last-child)::before{content:"";position:absolute;left:46px;top:100px;bottom:6px;width:4px;background:#dcdaf3;border-radius:4px}
.ps .n{width:96px;height:96px;border-radius:50%;background:#5b5bd6;color:#fff;font-weight:800;font-size:44px;display:grid;place-items:center;flex:none}
.ps b{display:block;font-size:46px;line-height:1.15;color:#17162b;margin-top:18px}
.ps span{display:block;font-size:34px;color:#55537a;line-height:1.32;margin-top:8px}
/* ---------- cifra ---------- */
.cifra{font-size:250px;font-weight:900;letter-spacing:-.06em;line-height:.9;color:#5b5bd6}
.cifra small{font-size:90px;letter-spacing:-.03em;margin-left:10px}
.compara{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.compara div{border-radius:28px;padding:30px 30px;font-size:30px;line-height:1.3;color:#17162b;background:#fff;box-shadow:0 10px 30px rgba(40,30,120,.08)}
.compara small{display:block;font-size:21px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px}
.compara .antes small{color:#d64545}.compara .despues small{color:#1f8a5b}
.compara .despues{outline:4px solid #22a06b}
/* ---------- versus ---------- */
.vs{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.col{background:#fff;border-radius:34px;padding:30px;box-shadow:0 10px 40px rgba(40,30,120,.08);display:flex;flex-direction:column}
.col h3{font-size:40px;margin-bottom:12px;color:#17162b;letter-spacing:-.01em}
.col .et{align-self:flex-start;font-size:21px;font-weight:800;padding:7px 15px;border-radius:20px;margin-bottom:20px}
.col.mal .et{background:#fde8e8;color:#c53030}.col.bien .et{background:#dcf5e8;color:#1f8a5b}
.col .mini{background:#efe7dc;border-radius:22px;padding:16px;display:flex;flex-direction:column;gap:10px;font-size:22px;line-height:1.3;flex:1}
.col .mini .bur{max-width:92%}
.col ul{list-style:none;display:flex;flex-direction:column;gap:16px}
.col li{display:flex;gap:14px;align-items:flex-start;font-size:33px;line-height:1.28;color:#17162b}
.col li i{flex:none;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;margin-top:1px}
.col.mal li i{background:#fbd5d5}.col.bien li i{background:#c9f0dc}
.paso{display:flex;gap:14px;align-items:center;background:#f3f2ff;border-radius:18px;padding:15px 16px;font-size:24px;font-weight:600;color:#17162b}
.paso .n{width:40px;height:40px;border-radius:50%;background:#22a06b;color:#fff;display:grid;place-items:center;flex:none}
.paso.pend .n{background:#5b5bd6;font-size:20px;font-weight:800}
.conclu{font-size:36px;font-weight:800;text-align:center;color:#17162b;letter-spacing:-.01em}
"""

OK = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
NO = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'


def burbujas(mensajes, ap=nada, i0=0):
    out = []
    for k, m in enumerate(mensajes or []):
        lado = "out" if m.get("de", "ia") in ("yo", "tu", "tú", "cliente") else "in"
        hora = f"<small>{e(m['hora'])}</small>" if m.get("hora") else ""
        out.append(f'<div class="bur {lado}" {ap(i0 + k)}>{negrita(m.get("texto"))}{hora}</div>')
    return "".join(out)


def movil(c, ap=nada, estilo=""):
    """c = {app?: whatsapp|asistente, nombre?, estado?, mensajes:[{de: yo|ia, texto, hora?}], botones?:[..]}"""
    app = c.get("app", "whatsapp")
    nombre = c.get("nombre") or ("Asistente de IA" if app == "asistente" else "Tu negocio")
    ini = c.get("inicial") or ("IA" if app == "asistente" else nombre[:1].upper())
    estado = c.get("estado") or "en línea"
    n = len(c.get("mensajes") or [])
    bot = ""
    if c.get("botones"):
        bot = f'<div class="botones" {ap(n)}>' + "".join(f'<span class="boton">{e(b)}</span>' for b in c["botones"][:3]) + "</div>"
    return (f'<div class="movil {"asistente" if app == "asistente" else ""}" style="{estilo}"><div class="pant">'
            f'<div class="cab"><div class="av">{e(ini)}</div><div>{e(nombre)}<small>{e(estado)}</small></div></div>'
            f'<div class="chat">{burbujas(c.get("mensajes"), ap)}{bot}</div></div></div>')


def celda(x):
    if isinstance(x, dict):
        cls = "bien" if x.get("bien") else "mal" if x.get("mal") else ""
        return f'<td class="{cls}">{e(x.get("t"))}</td>'
    return f"<td>{e(x)}</td>"


def tabla(s, ap=nada):
    cab = "".join(f"<th>{e(c)}</th>" for c in s.get("columnas", []))
    filas = "".join(f'<tr {ap(k)}>' + "".join(celda(x) for x in f) + "</tr>" for k, f in enumerate(s.get("filas", [])[:6]))
    return (f'<div class="ven"><div class="vbar"><i></i><i></i><i></i><span>{e(s.get("archivo") or "resultado")}</span></div>'
            f'<table class="tabla"><tr>{cab}</tr>{filas}</table></div>')


def globo(texto, ap_attr="", lila=False, ic="lightbulb"):
    if not texto:
        return ""
    return f'<div class="globo {"lila" if lila else ""}" {ap_attr}>{icono(ic, 40, "#ffd45c", 2.4)}<div>{negrita(texto)}</div></div>'


def tarjetas(lista, ap=nada):
    lista = (lista or [])[:4]
    rej = len(lista) == 4 and all(len(str(t.get("texto", ""))) <= 60 for t in lista)
    out = []
    for k, t in enumerate(lista):
        out.append(f'<div class="tj" {ap(k)}><div class="ic">{icono(t.get("icono"), 56, "#4f46e5")}</div>'
                   f'<div><b>{e(t.get("titulo"))}</b>{f"<span>{negrita(t.get("texto"))}</span>" if t.get("texto") else ""}</div></div>')
    return f'<div class="tarjetas {"rejilla" if rej else ""}">{"".join(out)}</div>'


def caja_prompt(s, ap_attr=""):
    return (f'<div class="ven" {ap_attr}><div class="vbar"><i></i><i></i><i></i><span>{e(s.get("app") or "Tu asistente de IA")}</span></div>'
            f'<div class="prompt"><span class="quien">Tú:</span>«{negrita(s.get("prompt"))}»</div></div>')


def pasos(lista, ap=nada):
    out = []
    for k, p in enumerate((lista or [])[:5], 1):
        p = p if isinstance(p, dict) else {"titulo": p}
        out.append(f'<div class="ps" {ap(k - 1)}><div class="n">{k}</div><div><b>{e(p.get("titulo"))}</b>'
                   f'{f"<span>{negrita(p.get("texto"))}</span>" if p.get("texto") else ""}</div></div>')
    return f'<div class="pasos">{"".join(out)}</div>'


def cifra(s, ap_attr=""):
    u = f"<small>{e(s['unidad'])}</small>" if s.get("unidad") else ""
    return f'<div class="cifra" {ap_attr}>{e(s.get("cifra"))}{u}</div>'


def compara(c, ap=nada):
    if not c:
        return ""
    return (f'<div class="compara"><div class="antes" {ap(0)}><small>{e(c.get("antes_titulo") or "Sin IA")}</small>{negrita(c.get("antes"))}</div>'
            f'<div class="despues" {ap(1)}><small>{e(c.get("despues_titulo") or "Con IA")}</small>{negrita(c.get("despues"))}</div></div>')


def columna(c, lado, ap=nada, i0=0):
    """Una columna del versus: con 'mensajes' (mini chat), 'pasos' (pasos hechos) o 'items' (lista)."""
    tono = c.get("tono") or ("mal" if lado == "izquierda" else "bien")
    et = f'<span class="et">{e(c["etiqueta"])}</span>' if c.get("etiqueta") else ""
    if c.get("mensajes"):
        cuerpo = f'<div class="mini">{burbujas(c["mensajes"], ap, i0)}</div>'
    elif c.get("pasos"):
        ps = []
        for k, p in enumerate(c["pasos"][:6]):
            hecho = not str(p).startswith("…")
            marca = OK.format(c="#fff") if hecho else str(k + 1)
            ps.append(f'<div class="paso {"" if hecho else "pend"}" {ap(i0 + k)}><span class="n">{marca}</span>{e(str(p).lstrip("…"))}</div>')
        cuerpo = f'<div style="display:flex;flex-direction:column;gap:12px">{"".join(ps)}</div>'
    else:
        ico = OK.format(c="#1f8a5b") if tono == "bien" else NO.format(c="#c53030")
        cuerpo = "<ul>" + "".join(f'<li {ap(i0 + k)}><i>{ico}</i><span>{e(x)}</span></li>' for k, x in enumerate(c.get("items", [])[:5])) + "</ul>"
    return f'<div class="col {tono}"><h3>{e(c.get("titulo"))}</h3>{et}{cuerpo}</div>'
