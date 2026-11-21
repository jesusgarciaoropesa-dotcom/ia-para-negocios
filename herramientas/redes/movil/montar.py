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
    if not os.path.exists(os.path.join(demo, 'index.html')):
        sys.exit(f'No encuentro {demo}/index.html')
    reels = os.path.join(RAIZ, 'reels'); os.makedirs(reels, exist_ok=True)
    trabajo = os.path.join(reels, f'{slug}-probar' if probar else f'.{slug}-movil'); shutil.rmtree(trabajo, ignore_errors=True); os.makedirs(trabajo)
    # fuentes de la demo
    fams = fuentes_de_la_demo(open(os.path.join(demo, 'index.html'), encoding='utf-8').read())
    faltan = [f for f in fams if not os.path.isdir(os.path.join(AQUI, 'node_modules', '@fontsource', f))]
    if faltan:
        if not os.path.exists(os.path.join(AQUI, 'package.json')):
            open(os.path.join(AQUI, 'package.json'), 'w').write('{"private":true}')
        subprocess.run(['npm', 'i', '--silent', '--no-audit', '--no-fund'] + [f'@fontsource/{f}' for f in faltan], cwd=AQUI, check=False)
    # servidor local de la demo
    puerto = puerto_libre()
    class Callado(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Callado, directory=demo)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', puerto), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
    env = dict(os.environ, PUERTO=str(puerto), NODE_PATH=os.path.join(AQUI, 'node_modules') + os.pathsep + os.environ.get('NODE_PATH', ''))
    r = subprocess.run(['node', os.path.join(AQUI, 'grabar.js'), os.path.abspath(cfgp), demo, trabajo] + (['--probar'] if probar else []), cwd=AQUI, env=env)
    srv.shutdown()
    if r.returncode != 0:
        sys.exit('Falló la grabación')
    if probar:
        print(json.dumps({'capturas': sorted(os.listdir(trabajo))[:40], 'carpeta': trabajo}, ensure_ascii=False)); return
    piezas(cfg, trabajo)
    ff = shutil.which('ffmpeg') or 'ffmpeg'
    run = lambda c: subprocess.run(c, check=True, cwd=trabajo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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


if __name__ == '__main__':
    main()
