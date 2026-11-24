#!/usr/bin/env python3
"""Reel «demo en el móvil» de iando: una demo real de iando.xyz usada en un teléfono, con un titular arriba,
música suave y un cierre con la palabra clave. Sin voz y sin que salga nadie (decidido por Jesús el 21-11-2026).

Uso:
  python3 herramientas/redes/movil/montar.py configs/<slug>-movil.json --demo <carpeta de la demo> [--probar]

  <carpeta de la demo>: la carpeta demos/<demo>/ de la rama main (p. ej. `git worktree add /tmp/main origin/main`
  y luego --demo /tmp/main/demos/bar-ejemplo). Tiene que tener su index.html y su img/.
  --probar: no hace vídeo; guarda una captura después de cada acción en reels/<slug>-probar/ para revisarlas con Read.

Config (ver ejemplo-movil.json):
  slug, sector (texto de la píldora), titular (1-2 líneas), palabra, musica ("suave" | "animada"),
  colores {arriba, abajo, tinta} (opcional), mocks {servicios, huecos} (datos de mentira para el formulario de reservas),
  acciones: lista de pasos que hace el «dedo» (ver grabar.js). Que dure 12-22 s.
Salida: reels/<slug>.mp4 (1080x1920) y reels/<slug>-portada.jpg.

Modo «sistema completo» (si la config trae "pasos", ver ejemplo-sistema.json): el reel cuenta el paquete entero en
4 pasos (web → citas online → panel privado → avisos por WhatsApp). Arriba sale una barra «Paso X de 4», el título
del paso, una frase con la palabra clave resaltada y 1-2 «chips» de beneficio pegados al móvil; cada paso empieza
donde la lista de acciones tiene {"paso": n}. Se sirve la raíz de la rama main (la demo y el panel citas/), así que
la acción {"ir": "citas/index.html?n=demo"} abre el panel privado con las tablas de mentira de mocks.tablas, y
{"whatsapp": "#hojaCont a.wa", "nombre": "Lucía"} enseña el recordatorio como conversación de ejemplo.
El cierre es «Para tu negocio» con 4 sectores ("sectores") y la caja de comentarios escribiendo la palabra.
Voz (opcional, añadida el 24-11-2026 a petición de Jesús): "voz" en cada paso y "voz_cierre" (frases cortas que caben en
lo que dura cada paso; si la voz es más larga, se congela el último fotograma del paso). Se pide como en los reels
«historia»: --pedido-voz imprime la sentencia SQL (UN audio Gemini «Achird» para todo); --sin-voz hace una vista previa muda.
Necesita: node + playwright (ya instalados), ffmpeg, y `pip install --break-system-packages fonttools brotli pillow`.
"""
import json, os, re, subprocess, sys, shutil, socket, time, http.server, threading, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
REDES = os.path.dirname(AQUI)
RAIZ = os.path.dirname(os.path.dirname(REDES))
W, H = 1080, 1920
SW, SH = 620, 1342
X, Y = (W - SW) // 2, 470
B, R = 22, 74


def ttf(nombre):
    from fontTools.ttLib import TTFont
    src = os.path.join(REDES, 'fuentes', f'inter-latin-{nombre}-normal.woff2')
    dst = os.path.join(AQUI, f'.inter-{nombre}.ttf')
    if not os.path.exists(dst):
        f = TTFont(src); f.flavor = None; f.save(dst)
    return dst


def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fuentes_de_la_demo(html):
    fams = set()
    for url in re.findall(r'https://fonts\.googleapis\.com/css2\?[^"\']+', html):
        for fam in re.findall(r'family=([^:&"\']+)', url):
            fams.add(fam.replace('+', '-').lower())
    return sorted(fams)


def puerto_libre():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


def chip_img(texto, fuente, tinta, acento, h=78):
    tmp = ImageDraw.Draw(Image.new('RGB', (1, 1))); tw = tmp.textlength(texto, font=fuente)
    w = int(tw) + 120
    sh = Image.new('L', (w + 40, h + 40), 0); ImageDraw.Draw(sh).rounded_rectangle([22, 28, 18 + w, 24 + h], radius=39, fill=110)
    im = Image.new('RGBA', sh.size, (10, 20, 40, 0)); im.putalpha(sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=39, fill=(255, 255, 255, 255))
    cx, cy = 20 + 44, 20 + h // 2; r = int(h * 0.27)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=acento + (255,))
    d.line([(cx - r * .48, cy + 1), (cx - r * .14, cy + r * .38), (cx + r * .52, cy - r * .33)], fill=(255, 255, 255, 255), width=max(4, r // 4), joint='curve')
    d.text((20 + 80, cy - fuente.size * 0.62), texto, font=fuente, fill=tinta + (255,))
    return im


def frase_con_clave(d, y, frase, clave, fuente, tinta, marcador):
    palabras = frase.split(' '); esp = d.textlength(' ', font=fuente)
    total = d.textlength(frase, font=fuente); x = (W - total) / 2
    for pw in palabras:
        lw = d.textlength(pw, font=fuente)
        if clave and pw.strip('.,;:¡!¿?«»').lower() in [c.lower() for c in clave.split(' ')]:
            d.rounded_rectangle([x - 8, y + fuente.size * 0.22, x + lw + 8, y + fuente.size * 1.18], radius=10, fill=marcador)
        x += lw + esp
    x = (W - total) / 2
    for pw in palabras:
        d.text((x, y), pw, font=fuente, fill=tinta); x += d.textlength(pw, font=fuente) + esp


def piezas_sistema(cfg, carpeta):
    col = cfg.get('colores', {})
    top, bot, tinta = hex2rgb(col.get('arriba', '#eef4fb')), hex2rgb(col.get('abajo', '#d6e3f5')), hex2rgb(col.get('tinta', '#0d2b57'))
    acento, marcador = hex2rgb(col.get('acento', '#1552c0')), hex2rgb(col.get('marcador', '#ffd84d'))
    s6, s8 = ttf('600'), ttf('800')
    pasos = cfg['pasos']; n = len(pasos)
    fp, ft, ff, fchip = ImageFont.truetype(s8, 30), ImageFont.truetype(s8, 84), ImageFont.truetype(s6, 46), ImageFont.truetype(s8, 31)
    for i, ps in enumerate(pasos):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        # barra «Paso X de N»
        bw, gap = 540, 14; seg = (bw - gap * (n - 1)) / n; x0 = (W - bw) / 2
        for k in range(n):
            xa = x0 + k * (seg + gap)
            d.rounded_rectangle([xa, 112, xa + seg, 126], radius=7, fill=(acento + (255,)) if k <= i else (tinta + (45,)))
        et = f'PASO {i + 1} DE {n}'; d.text(((W - d.textlength(et, font=fp)) / 2, 146), et, font=fp, fill=acento + (255,))
        t = ps['titulo']; fti = ft if d.textlength(t, font=ft) < W - 120 else ImageFont.truetype(s8, 68)
        d.text(((W - d.textlength(t, font=fti)) / 2, 196), t, font=fti, fill=tinta + (255,))
        if ps.get('frase'):
            fr = ff if d.textlength(ps['frase'], font=ff) < W - 100 else ImageFont.truetype(s6, 38)
            frase_con_clave(d, 318, ps['frase'], ps.get('clave', ''), fr, tinta + (255,), marcador + (255,))
        # chips en fila entre la frase y el móvil: así no tapan nada de la pantalla (pedido por Jesús el 24-11-2026)
        chips = [chip_img(t, fchip, tinta, acento, h=70) for t in ps.get('chips', [])[:2]]
        if chips:
            gap = 22; anchos = [c.width - 40 for c in chips]; x = (W - (sum(anchos) + gap * (len(chips) - 1))) / 2
            for c, aw in zip(chips, anchos):
                im.alpha_composite(c, (int(x) - 20, 392 - 20)); x += aw + gap
        im.save(os.path.join(carpeta, f'cabecera-{i + 1}.png'))
    # fondo sin titular
    bg = Image.new('RGB', (W, H)); d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3)))
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([X - B + 18, Y - B + 40, X + SW + B - 18, Y + SH + B + 40], radius=R + B, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(38)); bg.paste((20, 35, 60), (0, 0), sh)
    bg.save(os.path.join(carpeta, 'fondo.png'))
    marco_y_mascara(carpeta)
    cierre_sistema(cfg, carpeta, s6, s8)


def cierre_sistema(cfg, carpeta, s6, s8):
    pal = cfg.get('palabra', 'YO'); sectores = cfg.get('sectores', ['Fisios', 'Peluquerías', 'Talleres', 'Bares'])[:4]
    lila, blanco, gris = (163, 163, 245), (255, 255, 255), (220, 220, 235)
    def base():
        c = Image.new('RGB', (W, H)); cd = ImageDraw.Draw(c)
        for y in range(H):
            t = y / H; cd.line([(0, y), (W, y)], fill=(int(20 + 10 * t), int(20 + 8 * t), int(34 + 40 * t)))
        f1 = ImageFont.truetype(s8, 96); t = 'Para tu negocio'; cd.text(((W - cd.textlength(t, font=f1)) / 2, 300), t, font=f1, fill=blanco)
        fs = ImageFont.truetype(s6, 42)
        for k, sct in enumerate(sectores):
            cx = W / 2 + (-1 if k % 2 == 0 else 1) * 215; cy = 500 + (k // 2) * 112
            tw = cd.textlength(sct, font=fs)
            cd.rounded_rectangle([cx - 190, cy, cx + 190, cy + 88], radius=44, outline=lila, width=3)
            cd.text((cx - tw / 2, cy + 18), sct, font=fs, fill=gris)
        f3 = ImageFont.truetype(s6, 48)
        for k, l in enumerate([f'Comenta {pal} y te enseño', 'cómo sería la tuya']):
            cd.text(((W - cd.textlength(l, font=f3)) / 2, 1190 + k * 64), l, font=f3, fill=gris)
        f5 = ImageFont.truetype(s8, 50); l = '@iando.xyz'; cd.text(((W - cd.textlength(l, font=f5)) / 2, 1440), l, font=f5, fill=lila)
        return c
    fcaja, fpub, fcom = ImageFont.truetype(s6, 44), ImageFont.truetype(s8, 40), ImageFont.truetype(s8, 46)
    def caja(texto, cursor, pulsado=False, publicado=False):
        c = base(); cd = ImageDraw.Draw(c)
        x0, x1, y0, y1 = 90, W - 90, 930, 1060
        if publicado:
            # el comentario ya publicado, encima de la caja
            cd.ellipse([x0, 820, x0 + 70, 890], fill=(90, 90, 120)); cd.text((x0 + 92, 812), 'tú', font=ImageFont.truetype(s6, 32), fill=(170, 170, 190))
            cd.text((x0 + 92, 846), pal, font=fcom, fill=blanco)
        cd.rounded_rectangle([x0, y0, x1, y1], radius=65, fill=(255, 255, 255))
        cd.ellipse([x0 + 26, y0 + 30, x0 + 96, y0 + 100], fill=(205, 205, 222))
        tx = x0 + 120
        if texto:
            cd.text((tx, y0 + 40), texto, font=fcaja, fill=(20, 20, 34)); tx += cd.textlength(texto, font=fcaja) + 4
        else:
            cd.text((tx, y0 + 40), 'Añade un comentario…', font=fcaja, fill=(150, 150, 165))
        if cursor:
            cd.rectangle([tx, y0 + 36, tx + 4, y0 + 96], fill=(40, 90, 230))
        pc = (40, 90, 230) if texto else (170, 190, 235); pw = cd.textlength('Publicar', font=fpub)
        if pulsado:
            cd.rounded_rectangle([x1 - pw - 60, y0 + 24, x1 - 20, y1 - 24], radius=40, fill=(225, 233, 255))
        cd.text((x1 - pw - 40, y0 + 42), 'Publicar', font=fpub, fill=pc)
        return c
    cuadros = [(caja('', True), 0.45), (caja('', False), 0.4), (caja('', True), 0.3), (caja(pal[:1], True), 0.28)]
    for k in range(2, len(pal) + 1):
        cuadros.append((caja(pal[:k], True), 0.28))
    cuadros += [(caja(pal, False), 0.3), (caja(pal, True), 0.3), (caja(pal, False, pulsado=True), 0.35), (caja('', True, publicado=True), 0.45),
                (caja('', False, publicado=True), 0.45), (caja('', True, publicado=True), 0.45), (caja('', False, publicado=True), 0.45)]
    lista = ''
    for k, (im, dur) in enumerate(cuadros):
        nom = f'cierre-{k:02d}.png'; im.save(os.path.join(carpeta, nom)); lista += f"file '{nom}'\nduration {dur}\n"
    lista += f"file 'cierre-{len(cuadros) - 1:02d}.png'\n"
    open(os.path.join(carpeta, 'cierre.txt'), 'w').write(lista)
    return sum(d for _, d in cuadros)


def marco_y_mascara(carpeta):
    body = Image.new('L', (W, H), 0); ImageDraw.Draw(body).rounded_rectangle([X - B, Y - B, X + SW + B, Y + SH + B], radius=R + B, fill=255)
    hole = Image.new('L', (W, H), 0); ImageDraw.Draw(hole).rounded_rectangle([X, Y, X + SW, Y + SH], radius=R, fill=255)
    alpha = Image.composite(Image.new('L', (W, H), 0), body, hole)
    m = Image.new('RGBA', (W, H), (18, 18, 20, 0)); m.putalpha(alpha); md = ImageDraw.Draw(m)
    md.rounded_rectangle([X - B + 3, Y - B + 3, X + SW + B - 3, Y + SH + B - 3], radius=R + B - 3, outline=(70, 70, 74, 255), width=3)
    md.rounded_rectangle([W // 2 - 62, Y + 12, W // 2 + 62, Y + 46], radius=17, fill=(18, 18, 20, 255))
    m.save(os.path.join(carpeta, 'marco.png'))
    mk = Image.new('L', (SW, SH), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, SW, SH], radius=R, fill=255); mk.save(os.path.join(carpeta, 'mascara.png'))


def piezas(cfg, carpeta):
    col = cfg.get('colores', {})
    top, bot, tinta = hex2rgb(col.get('arriba', '#f7ece0')), hex2rgb(col.get('abajo', '#eccbb4')), hex2rgb(col.get('tinta', '#2b1e16'))
    s6, s8 = ttf('600'), ttf('800')
    bg = Image.new('RGB', (W, H)); d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    fc = ImageFont.truetype(s6, 30); chip = cfg.get('sector', '')
    if chip:
        cw = d.textlength(chip, font=fc); cx = (W - cw) // 2
        d.rounded_rectangle([cx - 26, 150, cx + cw + 26, 206], radius=28, fill=tinta); d.text((cx, 157), chip, font=fc, fill=top)
    lineas = cfg['titular'] if isinstance(cfg['titular'], list) else [cfg['titular']]
    tam = 92 if max(len(l) for l in lineas) <= 18 else 76
    fh = ImageFont.truetype(s8, tam)
    for i, l in enumerate(lineas[:2]):
        lw = d.textlength(l, font=fh); d.text(((W - lw) // 2, 236 + i * (tam + 10)), l, font=fh, fill=tinta)
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([X - B + 18, Y - B + 40, X + SW + B - 18, Y + SH + B + 40], radius=R + B, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(38)); bg.paste((60, 35, 20), (0, 0), sh)
    bg.save(os.path.join(carpeta, 'fondo.png'))
    body = Image.new('L', (W, H), 0); ImageDraw.Draw(body).rounded_rectangle([X - B, Y - B, X + SW + B, Y + SH + B], radius=R + B, fill=255)
    hole = Image.new('L', (W, H), 0); ImageDraw.Draw(hole).rounded_rectangle([X, Y, X + SW, Y + SH], radius=R, fill=255)
    alpha = Image.composite(Image.new('L', (W, H), 0), body, hole)
    m = Image.new('RGBA', (W, H), (18, 18, 20, 0)); m.putalpha(alpha); md = ImageDraw.Draw(m)
    md.rounded_rectangle([X - B + 3, Y - B + 3, X + SW + B - 3, Y + SH + B - 3], radius=R + B - 3, outline=(70, 70, 74, 255), width=3)
    md.rounded_rectangle([W // 2 - 62, Y + 12, W // 2 + 62, Y + 46], radius=17, fill=(18, 18, 20, 255))
    m.save(os.path.join(carpeta, 'marco.png'))
    # máscara de esquinas redondeadas para la pantalla
    mk = Image.new('L', (SW, SH), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, SW, SH], radius=R, fill=255); mk.save(os.path.join(carpeta, 'mascara.png'))
    # cierre
    c = Image.new('RGB', (W, H)); cd = ImageDraw.Draw(c)
    for y in range(H):
        t = y / H; cd.line([(0, y), (W, y)], fill=(int(20 + 10 * t), int(20 + 8 * t), int(34 + 40 * t)))
    fl = ImageFont.truetype(s8, 150); t = 'iando'; tw = cd.textlength(t, font=fl); cd.text(((W - tw) // 2, 520), t, font=fl, fill=(255, 255, 255))
    cd.ellipse([(W + tw) // 2 + 6, 655, (W + tw) // 2 + 30, 679], fill=(163, 163, 245))
    f2 = ImageFont.truetype(s6, 46)
    for i, l in enumerate(cfg.get('cierre', ['Webs con reservas', 'para negocios de tu zona'])):
        lw = cd.textlength(l, font=f2); cd.text(((W - lw) // 2, 750 + i * 62), l, font=f2, fill=(220, 220, 235))
    pal = cfg.get('palabra')
    if pal:
        f3 = ImageFont.truetype(s6, 48); l1 = 'Comenta'; cd.text(((W - cd.textlength(l1, font=f3)) // 2, 980), l1, font=f3, fill=(220, 220, 235))
        f4 = ImageFont.truetype(s8, 110); pw = cd.textlength(pal, font=f4)
        cd.rounded_rectangle([(W - pw) // 2 - 40, 1060, (W + pw) // 2 + 40, 1210], radius=40, fill=(163, 163, 245))
        cd.text(((W - pw) // 2, 1072), pal, font=f4, fill=(20, 20, 34))
        l2 = 'y te enseño cómo sería la tuya'; cd.text(((W - cd.textlength(l2, font=f3)) // 2, 1250), l2, font=f3, fill=(220, 220, 235))
    f5 = ImageFont.truetype(s8, 50); l = '@iando.xyz'; cd.text(((W - cd.textlength(l, font=f5)) // 2, 1450), l, font=f5, fill=(163, 163, 245))
    c.save(os.path.join(carpeta, 'cierre.png'))


def main():
    args = sys.argv[1:]
    if '--demo' not in args:
        sys.exit(__doc__)
    cfgp = args[0]; demo = os.path.abspath(args[args.index('--demo') + 1]); probar = '--probar' in args
    cfg = json.load(open(cfgp, encoding='utf-8')); slug = cfg['slug']
    if '--pedido-voz' in args:   # voz Gemini «Achird» de los pasos y el cierre (un solo audio), como en generar_historia.py
        sys.path.insert(0, REDES); import generar_historia as GH
        print(GH.pedido_voz([f for g in frases_voz(cfg) for f in g])); return
    cfg['_sin_voz'] = '--sin-voz' in args
    if not os.path.exists(os.path.join(demo, 'index.html')):
        sys.exit(f'No encuentro {demo}/index.html')
    sistema = bool(cfg.get('pasos'))
    servir = os.path.dirname(os.path.dirname(demo)) if sistema else demo
    inicio = f'demos/{os.path.basename(demo)}/index.html' if sistema else 'index.html'
    reels = os.path.join(RAIZ, 'reels'); os.makedirs(reels, exist_ok=True)
    trabajo = os.path.join(reels, f'{slug}-probar' if probar else f'.{slug}-movil'); shutil.rmtree(trabajo, ignore_errors=True); os.makedirs(trabajo)
    # fuentes de la demo
    fams = fuentes_de_la_demo(open(os.path.join(demo, 'index.html'), encoding='utf-8').read())
    if sistema:
        panel = os.path.join(servir, 'citas', 'index.html')
        if os.path.exists(panel): fams = sorted(set(fams) | set(fuentes_de_la_demo(open(panel, encoding='utf-8').read())))
        for neg in cfg.get('mocks', {}).get('tablas', {}).get('negocios', []):
            for v in ((neg.get('config') or {}).get('tema') or {}).get('fuentes', {}).values():
                fams = sorted(set(fams) | {v.split(':')[0].strip().replace(' ', '-').lower()})
    faltan = [f for f in fams if not os.path.isdir(os.path.join(AQUI, 'node_modules', '@fontsource', f))]
    if faltan:
        if not os.path.exists(os.path.join(AQUI, 'package.json')):
            open(os.path.join(AQUI, 'package.json'), 'w').write('{"private":true}')
        subprocess.run(['npm', 'i', '--silent', '--no-audit', '--no-fund'] + [f'@fontsource/{f}' for f in faltan], cwd=AQUI, check=False)
    # servidor local de la demo
    puerto = puerto_libre()
    class Callado(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Callado, directory=servir)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', puerto), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    env = dict(os.environ, PUERTO=str(puerto), INICIO=inicio, NODE_PATH=os.path.join(AQUI, 'node_modules') + os.pathsep + os.environ.get('NODE_PATH', ''))
    r = subprocess.run(['node', os.path.join(AQUI, 'grabar.js'), os.path.abspath(cfgp), demo, trabajo] + (['--probar'] if probar else []), cwd=AQUI, env=env)
    srv.shutdown()
    if r.returncode != 0:
        sys.exit('Falló la grabación')
    if probar:
        print(json.dumps({'capturas': sorted(os.listdir(trabajo))[:40], 'carpeta': trabajo}, ensure_ascii=False)); return
    ff = shutil.which('ffmpeg') or 'ffmpeg'
    run = lambda c: subprocess.run(c, check=True, cwd=trabajo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if sistema:
        return montar_sistema(cfg, trabajo, reels, slug, ff, run)
    piezas(cfg, trabajo)
    run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', 'cuadros.txt', '-vf', f'scale={SW}:{SH}:flags=lanczos,fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', 'pantalla.mp4'])
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(trabajo, 'pantalla.mp4')]).decode().strip())
    cierre = 2.8
    total = dur + cierre
    musica = os.path.join(REDES, 'musica', f"{cfg.get('musica', 'suave')}.wav")
    filtro = (f"[1:v]format=rgba[p];[p][3:v]alphamerge[pr];[0:v][pr]overlay={X}:{Y}[a];[a][2:v]overlay=0:0,format=yuv420p,setsar=1[demo];"
              f"[4:v]loop=loop=-1:size=1,trim=duration={cierre},fps=30,format=yuv420p,setsar=1,fade=t=in:st=0:d=0.35[fin];"
              f"[demo][fin]concat=n=2:v=1:a=0[v];"
              f"[5:a]atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={total - 1.2:.2f}:d=1.2,volume=0.55[m]")
    run([ff, '-y', '-loop', '1', '-t', f'{dur:.2f}', '-i', 'fondo.png', '-i', 'pantalla.mp4', '-loop', '1', '-t', f'{dur:.2f}', '-i', 'marco.png',
         '-loop', '1', '-t', f'{dur:.2f}', '-i', 'mascara.png', '-i', 'cierre.png', '-stream_loop', '-1', '-i', musica,
         '-filter_complex', filtro, '-map', '[v]', '-map', '[m]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-t', f'{total:.2f}', os.path.join(reels, f'{slug}.mp4')])
    run([ff, '-y', '-ss', '1.2', '-i', os.path.join(reels, f'{slug}.mp4'), '-frames:v', '1', '-q:v', '2', os.path.join(reels, f'{slug}-portada.jpg')])
    shutil.rmtree(trabajo, ignore_errors=True)
    print(json.dumps({'reel': f'reels/{slug}.mp4', 'portada': f'reels/{slug}-portada.jpg', 'segundos': round(total, 1)}, ensure_ascii=False))
    if total > 30:
        print('Aviso: dura más de 30 s; quita esperas o acciones.')


def geometria_sistema():
    """En el modo sistema el móvil es un poco más pequeño para dejar sitio a la fila de chips encima."""
    global SW, SH, X, Y, R
    SW, SH = 574, 1242
    X, Y, R = (W - SW) // 2, 500, 68


def frases_voz(cfg):
    """Frases que lee la voz: las de cada paso ("voz") y las del cierre ("voz_cierre"), partidas por frases."""
    def partir(t):
        return [f.strip() for f in re.split(r'(?<=[.!?])\s+', (t or '').strip()) if f.strip()]
    grupos = [partir(ps.get('voz')) for ps in cfg['pasos']] + [partir(cfg.get('voz_cierre'))]
    return grupos


def voces_sistema(cfg):
    """Devuelve [(pcm, sr) por grupo (cada paso y el cierre)] o None si aún no está la voz."""
    sys.path.insert(0, REDES)
    import generar_historia as GH
    grupos = frases_voz(cfg)
    if not any(grupos):
        return None, grupos
    todas = [f for g in grupos for f in g]
    voces = GH.voces_reel(todas)
    if not all(voces):
        return None, grupos
    out, k, sr = [], 0, voces[0][1]
    for g in grupos:
        trozo = b''
        for _ in g:
            pcm = GH.G.recortar(voces[k][0], sr)
            trozo += pcm + bytes(int(0.16 * sr) * 2); k += 1
        out.append((trozo, sr))
    return out, grupos


def montar_sistema(cfg, trabajo, reels, slug, ff, run):
    geometria_sistema()
    piezas_sistema(cfg, trabajo)
    run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', 'cuadros.txt', '-vf', f'scale={SW}:{SH}:flags=lanczos,fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', 'pantalla0.mp4'])
    run([ff, '-y', '-f', 'concat', '-safe', '0', '-i', 'cierre.txt', '-vf', 'fps=30,format=yuv420p,setsar=1', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', 'cierre0.mp4'])
    dura = lambda f: float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(trabajo, f)]).decode().strip())
    dur0, cierre0 = dura('pantalla0.mp4'), dura('cierre0.mp4')
    marcas = json.load(open(os.path.join(trabajo, 'pasos.json')))
    n = len(cfg['pasos'])
    inicios = {}
    for m in marcas: inicios.setdefault(int(m['paso']), float(m['t']))
    t0 = [inicios.get(k + 1, 0.0 if k == 0 else None) for k in range(n)]
    for k in range(n):
        if t0[k] is None: t0[k] = t0[k - 1]
    t0[0] = 0.0
    voces, grupos = voces_sistema(cfg)
    if any(grupos) and not voces and not cfg.get('_sin_voz'):
        sys.exit('Falta la voz. Pídela con --pedido-voz (o usa --sin-voz para una vista previa).')
    ANTES, DESPUES = 0.3, 0.45
    # cada paso dura lo que su trozo de demo o lo que tarda la voz (si la voz es más larga, se congela el último fotograma)
    seg0 = [(t0[k], t0[k + 1] if k + 1 < n else dur0) for k in range(n)]
    largos, extra = [], []
    for k, (a, b) in enumerate(seg0):
        v = len(voces[k][0]) / 2 / voces[k][1] if voces else 0
        L = max(b - a, ANTES + v + DESPUES if v else 0); largos.append(L); extra.append(max(0.0, L - (b - a)))
    vc = len(voces[n][0]) / 2 / voces[n][1] if voces and len(voces) > n else 0
    cierre = max(cierre0, ANTES + vc + 1.0)
    fc = ''.join(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={e:.3f}[s{k}];" for k, ((a, b), e) in enumerate(zip(seg0, extra)))
    fc += ''.join(f'[s{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[v]'
    run([ff, '-y', '-i', 'pantalla0.mp4', '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', 'pantalla.mp4'])
    run([ff, '-y', '-i', 'cierre0.mp4', '-vf', f'tpad=stop_mode=clone:stop_duration={max(0, cierre - cierre0):.3f},fade=t=in:st=0:d=0.3', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', 'cierre.mp4'])
    dur, cierre = dura('pantalla.mp4'), dura('cierre.mp4')
    tiempos = [sum(largos[:k]) for k in range(n)]
    total = dur + cierre
    musica = os.path.join(REDES, 'musica', f"{cfg.get('musica', 'suave')}.wav")
    audio_in = []
    if voces:
        import wave
        sr = voces[0][1]; buf = bytearray(int((total + 0.5) * sr) * 2)
        inicios_voz = [tiempos[k] + ANTES for k in range(n)] + [dur + ANTES]
        for (pcm, _), ti in zip(voces, inicios_voz):
            i0 = int(ti * sr) * 2; buf[i0:i0 + len(pcm)] = pcm[:max(0, len(buf) - i0)]
        with wave.open(os.path.join(trabajo, 'voz.wav'), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(buf))
        audio_in = ['-i', 'voz.wav']
    ent = [ff, '-y', '-loop', '1', '-t', f'{dur:.2f}', '-i', 'fondo.png', '-i', 'pantalla.mp4', '-loop', '1', '-t', f'{dur:.2f}', '-i', 'marco.png',
           '-loop', '1', '-t', f'{dur:.2f}', '-i', 'mascara.png']
    for k in range(n):
        ent += ['-loop', '1', '-t', f'{dur:.2f}', '-i', f'cabecera-{k + 1}.png']
    ent += ['-i', 'cierre.mp4', '-stream_loop', '-1', '-i', musica] + audio_in
    filtro = f"[1:v]format=rgba[p];[p][3:v]alphamerge[pr];[0:v][pr]overlay={X}:{Y}[a];[a][2:v]overlay=0:0[b0];"
    for k in range(n):
        ini = tiempos[k]; fin = tiempos[k + 1] if k + 1 < n else dur + 1
        filtro += (f"[{4 + k}:v]format=rgba,fade=t=in:st={ini:.2f}:d=0.3:alpha=1[c{k}];"
                   f"[b{k}][c{k}]overlay=0:0:enable='between(t,{ini:.2f},{fin - 0.001:.3f})'[b{k + 1}];")
    filtro += f"[b{n}]format=yuv420p,setsar=1[demo];[{4 + n}:v]format=yuv420p,setsar=1[fin];[demo][fin]concat=n=2:v=1:a=0[v];"
    if voces:   # música baja que se aparta cuando habla la voz (como en los reels «historia»)
        filtro += (f"[{6 + n}:a]aresample=44100,apad,atrim=0:{total:.2f},asplit=2[vz][sc];"
                   f"[{5 + n}:a]aresample=44100,atrim=0:{total:.2f},volume=0.22,afade=t=in:d=0.6,afade=t=out:st={total - 1.2:.2f}:d=1.2[mu];"
                   "[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[vz][md]amix=inputs=2:duration=first:normalize=0[m]")
    else:
        filtro += f"[{5 + n}:a]atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={total - 1.2:.2f}:d=1.2,volume=0.55[m]"
    run(ent + ['-filter_complex', filtro, '-map', '[v]', '-map', '[m]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30',
               '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-t', f'{total:.2f}', os.path.join(reels, f'{slug}.mp4')])
    run([ff, '-y', '-ss', '1.2', '-i', os.path.join(reels, f'{slug}.mp4'), '-frames:v', '1', '-q:v', '2', os.path.join(reels, f'{slug}-portada.jpg')])
    shutil.rmtree(trabajo, ignore_errors=True)
    print(json.dumps({'reel': f'reels/{slug}.mp4', 'portada': f'reels/{slug}-portada.jpg', 'segundos': round(total, 1),
                      'pasos': [round(t, 1) for t in tiempos], 'voz': 'gemini' if voces else 'ninguna'}, ensure_ascii=False))
    if total > 40:
        print('Aviso: dura más de 40 s; quita esperas o acciones.')


if __name__ == '__main__':
    main()
