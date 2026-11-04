#!/usr/bin/env python3
"""
Da de alta (o actualiza) un artículo en iando.xyz, que es HTML estático sin compilador.

El artículo ya tiene que estar en articulos/<slug>.html (copiado de la plantilla, ver
AGENTES.md). Este script deja todo lo demás enlazado para que Google y los lectores lo
encuentren:
  - lo añade a su página de categoría (lista, enlaces del lateral y datos estructurados),
  - lo añade o actualiza en sitemap.xml (con fecha),
  - lo añade o actualiza en search-index.json (buscador de la web).

Uso:
    python3 herramientas/publicar_articulo.py articulos/<slug>.html            # nuevo
    python3 herramientas/publicar_articulo.py articulos/<slug>.html --actualizado  # revisado
    python3 herramientas/publicar_articulo.py ... --comprobar   # solo dice lo que haría

Es idempotente: si el artículo ya está en un sitio, no lo duplica.
"""
import argparse, datetime, html, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOMINIO = "https://iando.xyz"
CATEGORIAS = {
    "chatgpt-empresas": "ChatGPT", "automatizacion-ia": "Automatización",
    "herramientas-ia": "Herramientas", "ia-marketing": "Marketing",
    "ia-por-sector": "Por Sector", "productividad-ia": "Productividad",
    "ia-ecommerce": "eCommerce", "legal-privacidad-ia": "Legal",
}


def leer_articulo(ruta: Path):
    t = ruta.read_text(encoding="utf-8")
    m = lambda rx: (re.search(rx, t, re.S) or [None, None])[1]
    titulo = m(r"<title>(.*?)\s*\|\s*IA para Negocios</title>") or m(r"<title>(.*?)</title>")
    desc = m(r'<meta name="description" content="([^"]*)"')
    h1 = re.sub(r"<[^>]+>", "", m(r"<h1[^>]*>(.*?)</h1>") or titulo or "").strip()
    # La categoría es la primera enlazada en las migas de pan (antes del menú no hay otra)
    migas = m(r'"@type":\s*"BreadcrumbList"(.*?)\]') or ""
    cat = (re.search(r"categorias/([a-z-]+)\.html", migas) or re.search(r'class="breadcrumb.*?categorias/([a-z-]+)\.html', t, re.S))
    if not (titulo and desc and cat):
        sys.exit(f"ERROR: a {ruta.name} le falta <title>, meta description o la categoría en las migas de pan")
    cat = cat[1]
    if cat not in CATEGORIAS:
        sys.exit(f"ERROR: categoría desconocida '{cat}'. Válidas: {', '.join(CATEGORIAS)}")
    cuerpo = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", m(r"<article[^>]*>(.*?)</article>") or t, flags=re.S)
    minutos = max(3, round(len(cuerpo.split()) / 200))
    return dict(slug=ruta.stem, titulo=html.unescape(titulo), h1=html.unescape(h1), desc=html.unescape(desc), cat=cat, min=minutos)


def fichas(t):
    """Posiciones (inicio, fin) de cada ficha <article|div class="article-item"> con su comentario previo."""
    out = []
    for m in re.finditer(r'<(article|div) class="article-item">', t):
        tag, prof, i = m[1], 0, m.start()
        for x in re.finditer(rf'<{tag}\b|</{tag}>', t[m.start():]):
            prof += -1 if x[0].startswith("</") else 1
            if prof == 0:
                fin = m.start() + x.end()
                break
        ini = t.rfind("\n", 0, m.start()) + 1
        prev = t.rfind("\n", 0, ini - 1) + 1
        if t[prev:ini].strip().startswith("<!--"):
            ini = prev
        out.append((ini, fin))
    return out


def en_categoria(a, comprobar):
    p = RAIZ / "categorias" / f"{a['cat']}.html"
    t = p.read_text(encoding="utf-8")
    href = f"../articulos/{a['slug']}.html"
    cambios = []
    fs = fichas(t)
    if not fs:
        sys.exit(f"ERROR: no encuentro fichas de artículos en {p.name}")
    if not any(href in t[i:f] for i, f in fs):
        i, f = fs[-1]
        nuevo = re.sub(r"<!--[^>]*-->", f"<!-- {a['slug']} -->", t[i:f], count=1)
        nuevo = re.sub(r'href="\.\./articulos/[^"]+"', f'href="{href}"', nuevo)
        nuevo = re.sub(r'(<a href="[^"]+">)[^<]*(</a>)', lambda x: x[1] + html.escape(a["h1"], quote=False) + x[2], nuevo, count=1)
        nuevo = re.sub(r"<span>\d+ min( de lectura)?</span>", lambda x: f"<span>{a['min']} min{x[1] or ''}</span>", nuevo, count=1)
        nuevo = re.sub(r"(<span>\d+ min[^<]*</span>)\s*<span>[^<]*</span>", r"\1", nuevo, count=1)
        nuevo = re.sub(r'(class="article-item-excerpt">)[^<]*(<)', lambda x: x[1] + html.escape(a["desc"], quote=False) + x[2], nuevo, count=1)
        t = t[:f] + "\n\n" + nuevo + t[f:]
        cambios.append("lista")
        fs = fichas(t)
    # Enlaces del lateral: líneas sueltas que enlazan a un artículo fuera de las fichas
    fuera = [m for m in re.finditer(r'^([ \t]*)<a href="\.\./articulos/[^"]+">[^<]*</a>\n', t, re.M)
             if not any(i <= m.start() < f for i, f in fs)]
    if fuera and f'<a href="{href}">' not in "".join(m.group(0) for m in fuera):
        u = fuera[-1]
        t = t[:u.end()] + f'{u[1]}<a href="{href}">{html.escape(a["h1"], quote=False)}</a>\n' + t[u.end():]
        cambios.append("lateral")
    # Datos estructurados (solo si la categoría ya tiene ItemList)
    lds = list(re.finditer(r'^([ \t]*)\{ "@type": "Article", "name": "[^"]*", "url": "[^"]*" \}', t, re.M))
    url = f"{DOMINIO}/articulos/{a['slug']}.html"
    if lds and url not in t:
        u = lds[-1]
        t = t[:u.end()] + f',\n{u[1]}{{ "@type": "Article", "name": {json.dumps(a["h1"], ensure_ascii=False)}, "url": "{url}" }}' + t[u.end():]
        cambios.append("datos estructurados")
    if cambios and not comprobar:
        p.write_text(t, encoding="utf-8")
    return cambios


def en_sitemap(a, hoy, comprobar):
    p = RAIZ / "sitemap.xml"
    t = p.read_text(encoding="utf-8")
    loc = f"<loc>{DOMINIO}/articulos/{a['slug']}.html</loc>"
    if loc in t:
        t2 = re.sub(re.escape(loc) + r"\s*<lastmod>[^<]*</lastmod>", f"{loc}\n    <lastmod>{hoy}</lastmod>", t)
        accion = "fecha"
    else:
        entrada = f"  <url>\n    {loc}\n    <lastmod>{hoy}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n"
        t2 = t.replace("</urlset>", entrada + "</urlset>")
        accion = "alta"
    if not comprobar:
        p.write_text(t2, encoding="utf-8")
    return accion


def en_buscador(a, comprobar):
    p = RAIZ / "search-index.json"
    datos = json.loads(p.read_text(encoding="utf-8"))
    url = f"articulos/{a['slug']}.html"
    fila = {"title": a["h1"], "desc": a["desc"], "cat": CATEGORIAS[a["cat"]], "url": url}
    previa = next((d for d in datos if d.get("url") == url), None)
    if previa:
        previa.update(fila); accion = "actualizado"
    else:
        datos.append(fila); accion = "alta"
    if not comprobar:
        p.write_text("[\n" + ",\n".join(json.dumps(d, ensure_ascii=False, indent=0) for d in datos) + "\n]\n", encoding="utf-8")
    return accion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("articulo")
    ap.add_argument("--actualizado", action="store_true", help="artículo revisado: solo fecha y buscador")
    ap.add_argument("--comprobar", action="store_true")
    ap.add_argument("--fecha", default=datetime.date.today().isoformat())
    x = ap.parse_args()
    ruta = (RAIZ / x.articulo) if not Path(x.articulo).is_absolute() else Path(x.articulo)
    a = leer_articulo(ruta)
    res = {"articulo": a["slug"], "categoria": a["cat"]}
    if not x.actualizado:
        res["categoria_cambios"] = en_categoria(a, x.comprobar)
    res["sitemap"] = en_sitemap(a, x.fecha, x.comprobar)
    res["buscador"] = en_buscador(a, x.comprobar)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
