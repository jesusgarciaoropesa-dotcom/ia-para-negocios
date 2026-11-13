#!/usr/bin/env python3
"""
Genera las láminas de un carrusel de iando (Instagram/Facebook) a partir de un JSON.

    python3 herramientas/redes/generar_carrusel.py configs/<slug>.json [--salida carruseles]
    python3 herramientas/redes/generar_carrusel.py --iconos        # lista los iconos disponibles

Crea carruseles/<slug>/01.jpg, 02.jpg… (1080x1350, 4:5) y carruseles/<slug>/historia.jpg (1080x1920).
Láminas de diseño sin fotos: cada una ENSEÑA la idea con una pieza visual (móvil con chat, tabla de
resultado, tarjetas con icono, prompt para copiar…) en vez de solo texto. Ver METODO.md.

Tipos de lámina (campo "tipo"); "destacado" = palabras del título en color:
  portada  {kicker, titulo, destacado?, subtitulo?, chat?}        → 1ª lámina. Con "chat" sale un móvil con la conversación
  chat     {titulo, texto?, chat:{app?, nombre?, mensajes:[{de:"yo"|"ia", texto, hora?}], botones?}, globo?}
  tabla    {titulo, archivo?, columnas:[..], filas:[[..]], globo?}  celda = "texto" o {"t": "texto", "bien"|"mal": true}
  tarjetas {titulo, texto?, tarjetas:[{icono, titulo, texto?}] (2-4)}
  pasos    {titulo, texto?, pasos:[{titulo, texto?}] (3-5)}
  prompt   {titulo, app?, prompt, consejo?}                         [huecos] entre corchetes salen resaltados
  cifra    {titulo, cifra, unidad?, texto?, compara?:{antes, despues, antes_titulo?, despues_titulo?}}
  versus   {titulo, izquierda:{titulo, etiqueta?, mensajes?|pasos?|items?}, derecha:{…}, conclusion?}
  punto    {num?, icono?, titulo, texto, dato?}                     (solo texto: úsalo poco)
  lista    {titulo, items:[..] (3-5)}                               (solo texto: úsalo poco)
  cierre   {titulo, texto?, palabra?, cta?}                         → última. Con "palabra": «Comenta PALABRA y te paso la guía»

Historias (opcional, a nivel de configuración): "historia": {texto?, pregunta, opciones?:[2-3]} pone en
historia.jpg una caja de pregunta/encuesta; "historia_reel" (mismo formato) crea además historia-reel.jpg
("Nuevo reel") para la publicación del reel. Regla de Jesús: toda publicación lleva historia con pregunta.
"""
import argparse, base64, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import componentes as C  # noqa: E402
from componentes import e, negrita, icono  # noqa: E402

AQUI = Path(__file__).resolve().parent
F = AQUI / "fuentes"


def fuente(peso):
    b = base64.b64encode((F / f"inter-latin-{peso}-normal.woff2").read_bytes()).decode()
    return f"@font-face{{font-family:Inter;font-weight:{peso};src:url(data:font/woff2;base64,{b}) format('woff2')}}"


CSS = "".join(fuente(p) for p in (400, 600, 800)) + """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;height:1350px;font-family:Inter,sans-serif;overflow:hidden}
.l{position:relative;width:1080px;height:1350px;background:#f6f5fb;color:#17162b;overflow:hidden}
.osc{background:radial-gradient(circle at 82% 12%,#7b6ff0 0,#4338ca 46%,#1e1b4b 100%);color:#fff}
.negro{background:#17162b;color:#fff}
.red{position:absolute;inset:0;opacity:.10;pointer-events:none}
.marca{position:absolute;top:56px;left:64px;display:flex;align-items:center;gap:14px;font-weight:800;font-size:28px;color:#4f46e5;z-index:3}
.marca i{width:46px;height:46px;border-radius:13px;background:#5b5bd6;display:grid;place-items:center}
.osc .marca,.negro .marca{color:#fff}.osc .marca i,.negro .marca i{background:rgba(255,255,255,.18)}
.pag{position:absolute;top:62px;right:64px;font-size:26px;color:#8a88a6;font-weight:600;z-index:3}
.osc .pag{color:#c7c3ff}
.pie{position:absolute;bottom:50px;left:64px;right:64px;display:flex;justify-content:space-between;font-size:26px;color:#8a88a6;font-weight:600}
.pie b{color:#5b5bd6}
.zona{position:absolute;left:64px;right:64px;top:150px;bottom:120px;display:flex;flex-direction:column}
.vis{flex:1;display:flex;flex-direction:column;justify-content:center;gap:30px;min-height:0;padding-top:34px}
.vis.centro{align-items:center}
h1{font-size:96px;line-height:1.02;letter-spacing:-.035em;font-weight:800}
h2{font-size:70px;line-height:1.05;letter-spacing:-.03em;font-weight:800}
.dest{color:#5b5bd6}
.osc .dest,.negro .dest{color:#ffd45c}
.sub{font-size:34px;color:#55537a;margin-top:22px;line-height:1.32;font-weight:400}
.osc .sub,.negro .sub{color:#d9d6ff}
.kick{display:inline-block;align-self:flex-start;background:#ffd45c;color:#1e1b4b;font-weight:800;font-size:28px;padding:11px 24px;border-radius:40px;margin-bottom:28px;letter-spacing:.06em;text-transform:uppercase}
.desliza{position:absolute;bottom:56px;left:64px;font-size:30px;font-weight:700;color:#fff;background:rgba(255,255,255,.15);border-radius:40px;padding:12px 26px}
.num{width:120px;height:120px;border-radius:32px;background:#5b5bd6;color:#fff;font-weight:800;font-size:64px;display:grid;place-items:center;margin-bottom:40px}
.txt{font-size:42px;line-height:1.38;color:#3f3d66;margin-top:34px}
.dato{white-space:pre-line;background:#fff;border-left:12px solid #5b5bd6;border-radius:24px;padding:32px 36px;font-size:36px;line-height:1.35;color:#17162b;box-shadow:0 10px 30px rgba(40,30,120,.08);margin-top:44px}
ul.lis{list-style:none;display:flex;flex-direction:column;gap:22px}
ul.lis li{display:flex;gap:24px;align-items:center;font-size:38px;line-height:1.28;background:#fff;border-radius:26px;padding:24px 28px;box-shadow:0 10px 30px rgba(40,30,120,.07)}
ul.lis li i{flex:none;width:56px;height:56px;border-radius:50%;background:#22a06b;display:grid;place-items:center}
.cta{background:#ffd45c;color:#17162b;border-radius:36px;padding:38px 42px}
.cta b{font-size:56px;display:block;letter-spacing:-.02em;line-height:1.1}
.cta span{font-size:30px;font-weight:600;display:block;margin-top:8px}
.otro{font-size:28px;color:#a9a6d6;margin-top:26px;line-height:1.35}
.guardar{display:flex;align-items:center;gap:22px;color:#c7c3ff;font-size:30px;font-weight:600;margin-top:44px}
body.h{height:1920px}.h .l{height:1920px}
""" + C.CSS

OK_B = C.OK.format(c="#fff")


def red(alto=1350):
    r = random.Random(11)
    d = []
    for _ in range(26):
        x, y, L = r.randint(0, 1080), r.randint(0, alto), r.randint(60, 220)
        v = r.choice([-1, 1]) * r.randint(30, 90)
        d.append(f'<path d="M{x} {y}h{L}v{v}"/><circle cx="{x}" cy="{y}" r="6"/>')
    return f'<svg class="red" viewBox="0 0 1080 {alto}"><g stroke="#fff" stroke-width="3" fill="none">{"".join(d)}</g></svg>'


def resaltar(titulo, destacado):
    t = e(titulo)
    if destacado and e(destacado) in t:
        t = t.replace(e(destacado), f'<span class="dest">{e(destacado)}</span>', 1)
    return t


def marco(i, n):
    return f'<div class="marca"><i>{icono("sparkles", 26, "#fff", 2.4)}</i>iando.xyz</div><div class="pag">{i}/{n}</div>'


def pie(i, n):
    return f'<div class="pie"><span>IA para negocios</span><b>{"Desliza →" if i < n else "Guárdalo 🔖"}</b></div>'


def cabeza(s, tam=70):
    h = f'<h2 style="font-size:{tam}px">{resaltar(s["titulo"], s.get("destacado"))}</h2>'
    if s.get("texto") and s.get("tipo") not in ("punto",):
        h += f'<p class="sub">{negrita(s["texto"])}</p>'
    return h


def lamina(s, i, n):
    """Devuelve (clase de fondo, html)."""
    t = s.get("tipo", "punto")
    m = marco(i, n)
    if t == "portada":
        if s.get("chat"):
            cuerpo = f"""{red()}{m}
            <div style="position:absolute;left:64px;right:430px;top:200px;bottom:150px;display:flex;flex-direction:column;justify-content:center">
              <span class="kick">{e(s.get('kicker'))}</span>
              <h1 style="font-size:88px">{resaltar(s['titulo'], s.get('destacado'))}</h1>
              {f'<p class="sub">{negrita(s["subtitulo"])}</p>' if s.get('subtitulo') else ''}</div>
            {C.movil(s['chat'], estilo='position:absolute;right:-50px;top:230px;transform:rotate(6deg)')}
            <span class="desliza">Desliza →</span>"""
        elif s.get("duelo"):
            def ficha(d, giro):
                return (f'<div style="width:330px;height:330px;border-radius:56px;background:{d.get("color", "#fff")};'
                        f'box-shadow:0 30px 70px rgba(10,6,50,.45);transform:rotate({giro}deg);display:flex;flex-direction:column;'
                        f'align-items:center;justify-content:center;gap:26px">{icono(d.get("icono", "message-circle"), 120, d.get("tinta", "#1e1b4b"), 1.6)}'
                        f'<b style="font-size:52px;letter-spacing:-1px;color:{d.get("tinta", "#1e1b4b")}">{e(d["nombre"])}</b></div>')
            a, b = s["duelo"][:2]
            cuerpo = f"""{red()}{m}
            <div style="position:absolute;left:0;right:0;top:170px;display:flex;justify-content:center;align-items:center;gap:0">
              {ficha(a, -6)}
              <div style="width:130px;height:130px;margin:0 -34px;z-index:2;border-radius:50%;background:#ffd45c;color:#1e1b4b;font-weight:900;font-size:50px;display:flex;align-items:center;justify-content:center;box-shadow:0 14px 34px rgba(0,0,0,.35)">VS</div>
              {ficha(b, 6)}</div>
            <div style="position:absolute;left:64px;right:64px;top:180px;bottom:170px;display:flex;flex-direction:column;justify-content:flex-end">
              <span class="kick">{e(s.get('kicker'))}</span>
              <h1>{resaltar(s['titulo'], s.get('destacado'))}</h1>
              {f'<p class="sub">{negrita(s["subtitulo"])}</p>' if s.get('subtitulo') else ''}</div>
            <span class="desliza">Desliza →</span>"""
        else:
            cuerpo = f"""{red()}{m}
            <div style="position:absolute;left:64px;right:64px;top:180px;bottom:170px;display:flex;flex-direction:column;justify-content:flex-end">
              {f'<div style="margin-bottom:auto;align-self:flex-end;opacity:.9">{icono(s["icono"], 260, "#ffd45c", 1.4)}</div>' if s.get('icono') else ''}
              <span class="kick">{e(s.get('kicker'))}</span>
              <h1>{resaltar(s['titulo'], s.get('destacado'))}</h1>
              {f'<p class="sub">{negrita(s["subtitulo"])}</p>' if s.get('subtitulo') else ''}</div>
            <span class="desliza">Desliza →</span>"""
        return "osc", cuerpo
    if t == "cierre":
        if s.get("palabra"):
            caja = f'<div class="cta"><b>Comenta «{e(s["palabra"].upper())}»</b><span>{e(s.get("cta") or "y te paso la guía por mensaje privado")}</span></div>'
            caja += '<p class="otro">¿Prefieres que te lo monten en tu negocio? Enlace en la bio.</p>'
        else:
            caja = f'<div class="cta"><b>Enlace en la bio</b><span>{e(s.get("cta") or "¿Prefieres que te lo monten? Webs, reservas y automatizaciones para tu negocio.")}</span></div>'
        cuerpo = f"""{red()}{m}<div class="zona" style="justify-content:flex-end;bottom:80px">
          <h1 style="font-size:88px">{resaltar(s['titulo'], s.get('destacado'))}</h1>
          {f'<p class="sub" style="margin-bottom:10px">{negrita(s["texto"])}</p>' if s.get('texto') else ''}
          <div class="guardar">{icono("bookmark", 54, "#ffd45c", 2)}<span>Guárdalo para cuando lo vayas a probar</span></div>
          <div style="height:40px"></div>{caja}</div>"""
        return "negro", cuerpo
    if t == "chat":
        vis = f'<div class="vis centro">{C.movil(s["chat"], estilo="transform:scale(.98)")}{C.globo(s.get("globo"))}</div>'
        return "", m + f'<div class="zona">{cabeza(s, 64)}{vis}</div>' + pie(i, n)
    if t == "tabla":
        vis = f'<div class="vis">{C.tabla(s)}{C.globo(s.get("globo"))}</div>'
        return "", m + f'<div class="zona">{cabeza(s)}{vis}</div>' + pie(i, n)
    if t == "tarjetas":
        return "", m + f'<div class="zona">{cabeza(s)}<div class="vis">{C.tarjetas(s.get("tarjetas"))}</div></div>' + pie(i, n)
    if t == "pasos":
        return "", m + f'<div class="zona">{cabeza(s)}<div class="vis">{C.pasos(s.get("pasos"))}</div></div>' + pie(i, n)
    if t == "prompt":
        vis = f'<div class="vis">{C.caja_prompt(s)}{C.globo(s.get("consejo"), lila=True, ic="wand-sparkles")}</div>'
        return "", m + f'<div class="zona">{cabeza(s)}{vis}</div>' + pie(i, n)
    if t == "cifra":
        vis = f'<div class="vis">{C.cifra(s)}{C.compara(s.get("compara"))}</div>'
        return "", m + f'<div class="zona">{cabeza(s)}{vis}</div>' + pie(i, n)
    if t == "versus":
        conclu = f'<div class="conclu">{negrita(s["conclusion"])}</div>' if s.get("conclusion") else ""
        vis = f'<div class="vis"><div class="vs">{C.columna(s.get("izquierda", {}), "izquierda")}{C.columna(s.get("derecha", {}), "derecha")}</div>{conclu}</div>'
        return "", m + f'<div class="zona">{cabeza(s)}{vis}</div>' + pie(i, n)
    if t == "lista":
        its = "".join(f"<li><i>{OK_B}</i><span>{negrita(x)}</span></li>" for x in s.get("items", [])[:6])
        return "", m + f'<div class="zona">{cabeza(s)}<div class="vis"><ul class="lis">{its}</ul></div></div>' + pie(i, n)
    # punto
    arriba = ""
    if s.get("icono"):
        arriba = f'<div class="num">{icono(s["icono"], 64, "#fff")}</div>'
    elif s.get("num"):
        arriba = f'<div class="num">{e(s["num"])}</div>'
    dato = f'<div class="dato">{negrita(s["dato"])}</div>' if s.get("dato") else ""
    cuerpo = f"""<div class="zona" style="justify-content:center">{arriba}
      <h2>{resaltar(s['titulo'], s.get('destacado'))}</h2><p class="txt">{negrita(s.get('texto'))}</p>{dato}</div>"""
    return "", m + cuerpo + pie(i, n)


def encuesta(h):
    """Caja de pregunta/encuesta para la historia (campo "historia" de la configuración)."""
    if not h or not h.get("pregunta"):
        return ""
    ops = "".join(f'<div style="flex:1;background:#fff;color:#17162b;border-radius:24px;padding:22px 10px;text-align:center;font-size:36px;font-weight:800">{e(o)}</div>' for o in (h.get("opciones") or [])[:3])
    return f'''<div style="position:absolute;left:80px;right:80px;bottom:250px;background:#ffd45c;color:#17162b;border-radius:40px;padding:40px 44px">
      {f'<div style="font-size:30px;font-weight:700;margin-bottom:10px">{e(h["texto"])}</div>' if h.get("texto") else ''}
      <div style="font-size:50px;font-weight:800;line-height:1.12;letter-spacing:-.02em">{e(h["pregunta"])}</div>
      {f'<div style="display:flex;gap:20px;margin-top:28px">{ops}</div>' if ops else ''}</div>'''


def historia(p, h=None, aviso="Nuevo post · míralo 👆"):
    movil = ""
    if h and h.get("pregunta"):
        p = {**p, "chat": None, "subtitulo": None}
    if p.get("chat"):
        movil = C.movil(p["chat"], estilo="transform:scale(1.1) rotate(4deg);margin:120px auto 0 170px")
    return f"""{red(1920)}<div class="marca" style="top:110px"><i>{icono("sparkles", 26, "#fff", 2.4)}</i>iando.xyz</div>
    <div style="position:absolute;left:80px;right:80px;top:230px;bottom:200px;display:flex;flex-direction:column;justify-content:center">
      <span class="kick">{e(p.get('kicker'))}</span>
      <h1 style="font-size:{86 if movil else 110}px">{resaltar(p['titulo'], p.get('destacado'))}</h1>
      {'' if movil else (f'<p class="sub" style="font-size:44px">{negrita(p["subtitulo"])}</p>' if p.get('subtitulo') else '')}
      {movil}</div>
    {encuesta(h)}
    <span class="desliza" style="left:80px;bottom:150px;font-size:36px">{e(aviso)}</span>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?")
    ap.add_argument("--salida", default="carruseles")
    ap.add_argument("--iconos", action="store_true")
    a = ap.parse_args()
    if a.iconos:
        print(" ".join(C.iconos_disponibles()))
        return
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    slides = cfg["slides"]
    if not 3 <= len(slides) <= 10:
        sys.exit("Un carrusel necesita entre 3 y 10 láminas")
    if slides[0].get("tipo") != "portada":
        sys.exit("La primera lámina tiene que ser de tipo 'portada'")
    solo_texto = sum(1 for s in slides[1:-1] if s.get("tipo", "punto") in ("punto", "lista"))
    if solo_texto > 1:
        print(f"AVISO: {solo_texto} láminas son solo texto (punto/lista). Cambia alguna por chat, tabla, tarjetas, pasos, prompt, cifra o versus.", file=sys.stderr)
    out = Path(a.salida) / cfg["slug"]
    out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    hechos, avisos = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            clase, cuerpo = lamina(s, i, len(slides))
            pg.set_content(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='l {clase}'>{cuerpo}</div></body></html>")
            pg.wait_for_timeout(150)
            desborda = pg.evaluate("""(() => {
              const l = document.querySelector('.l'), L = l.getBoundingClientRect();
              const z = document.querySelector('.zona, .vis');
              if (z && (z.scrollHeight > z.clientHeight + 2)) return true;
              const v = document.querySelector('.vis');
              if (v && v.scrollHeight > v.clientHeight + 2) return true;
              const pie = document.querySelector('.pie');
              const ult = [...document.querySelectorAll('.vis > *, .zona > *')].map(x => x.getBoundingClientRect().bottom);
              if (pie && ult.length && Math.max(...ult) > pie.getBoundingClientRect().top - 6) return true;
              if (l.classList.contains('osc')) return false;
              return [...l.querySelectorAll('h1,h2,.sub,.movil,.ven,.tarjetas,.pasos,.vs,.cta')].some(x => { const r = x.getBoundingClientRect(); return r.bottom > L.bottom + 1 || r.right > L.right + 60; });
            })()""")
            if desborda:
                avisos += 1
                print(f"AVISO: la lámina {i} ({s.get('tipo')}) tiene demasiado contenido y se sale; acórtalo", file=sys.stderr)
            ruta = out / f"{i:02d}.jpg"
            pg.screenshot(path=str(ruta), type="jpeg", quality=92)
            hechos.append(str(ruta))
        pg.set_viewport_size({"width": 1080, "height": 1920})
        # Historias: la del carrusel y, si la configuración trae "historia_reel", otra para el reel
        for nombre, h, aviso in (("historia.jpg", cfg.get("historia"), "Nuevo post · míralo 👆"),
                                 ("historia-reel.jpg", cfg.get("historia_reel"), "Nuevo reel · míralo 👆")):
            if nombre == "historia-reel.jpg" and not h:
                continue
            pg.set_content(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body class='h'><div class='l osc'>{historia(slides[0], h, aviso)}</div></body></html>")
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / nombre), type="jpeg", quality=92)
        b.close()
    print(json.dumps({"laminas": hechos, "historia": str(out / "historia.jpg"), "avisos": avisos}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
