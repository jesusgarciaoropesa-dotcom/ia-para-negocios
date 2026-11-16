#!/usr/bin/env python3
"""Descarga las fotos libres que pide una demo (demos/<slug>/fotos.json) y las deja en
demos/<slug>/img/<nombre>.jpg, recortadas y comprimidas. Lo ejecuta la acción de GitHub
«Fotos de las demos» (la máquina del taller no puede bajar imágenes de internet).

fotos.json:
{"fotos": [{"nombre": "inicio", "url": "https://unsplash.com/photos/...", "ancho": 1800, "alto": 1100}]}
- url: página de una foto de Unsplash o Pexels (licencia libre, sin atribución obligatoria)
  o la URL directa de la imagen en images.unsplash.com / images.pexels.com.
- ancho/alto (opcionales): tamaño final; si van los dos, recorta centrado a esa proporción.
Deja el resultado de cada foto en demos/<slug>/img/fotos-resultado.json.
"""
import io, json, re, sys, urllib.request, pathlib
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "Accept-Language": "es-ES,es;q=0.9"}

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")

def url_imagen(url, ancho):
    if re.match(r"https://images\.(unsplash|pexels)\.com/", url):
        return url
    m = re.match(r"https://(?:www\.)?pexels\.com/(?:[a-z-]+/)?photo/(?:.*-)?(\d+)/?", url)
    if m:
        i = m.group(1)
        return f"https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&cs=tinysrgb&w={ancho}"
    if "unsplash.com/photos/" in url:
        try:
            html, _ = get(url)
            m = re.search(rb'property="og:image"\s+content="([^"]+)"', html) or re.search(rb'content="([^"]+)"\s+property="og:image"', html)
            if m:
                img = m.group(1).decode().replace("&amp;", "&")
                if "plus.unsplash.com" in img or "premium_photo" in img:
                    raise PermissionError("es de Unsplash+ (de pago): elige otra")
                img = re.sub(r"[?&](w|h|fit|crop|q|fm|ixid|ixlib|auto|cs|mark|blend|txt)[^&]*", "", img.split("?")[0] + "?" + img.split("?",1)[1]) if "?" in img else img
                base = img.split("?")[0]
                return f"{base}?w={ancho}&q=80&fm=jpg&fit=max"
        except PermissionError:
            raise
        except Exception:
            pass
        ident = url.rstrip("/").split("/")[-1]
        ident = ident.split("-")[-1] if len(ident) > 11 else ident
        return f"https://unsplash.com/photos/{ident}/download?force=true&w={ancho}"
    raise ValueError("solo se aceptan fotos de Unsplash o Pexels")

def procesar(slug):
    base = pathlib.Path("demos") / slug
    pedido = json.loads((base / "fotos.json").read_text())
    out = base / "img"; out.mkdir(exist_ok=True)
    resultado = []
    for f in pedido.get("fotos", []):
        nombre = re.sub(r"[^a-z0-9-]", "-", str(f.get("nombre", "")).lower()).strip("-")
        ancho, alto = int(f.get("ancho", 1600)), f.get("alto")
        r = {"nombre": nombre, "url": f.get("url")}
        try:
            if not nombre: raise ValueError("falta nombre")
            src = url_imagen(f["url"], max(ancho, 1200))
            datos, tipo = get(src)
            im = Image.open(io.BytesIO(datos)).convert("RGB")
            if alto:
                alto = int(alto); obj = ancho / alto
                w, h = im.size
                if w / h > obj:
                    nw = int(h * obj); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
                else:
                    nh = int(w / obj); y = int((h - nh) * float(f.get("foco_y", 0.5))); im = im.crop((0, y, w, y + nh))
                im = im.resize((ancho, alto), Image.LANCZOS)
            elif im.width > ancho:
                im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
            dest = out / f"{nombre}.jpg"
            im.save(dest, "JPEG", quality=78, optimize=True, progressive=True)
            r.update(ok=True, archivo=f"img/{nombre}.jpg", tamano=list(im.size), kb=round(dest.stat().st_size / 1024))
        except Exception as e:
            r.update(ok=False, error=str(e)[:200])
        resultado.append(r)
    (out / "fotos-resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1))
    return resultado

if __name__ == "__main__":
    for slug in sys.argv[1:]:
        print(slug, json.dumps(procesar(slug), ensure_ascii=False))
