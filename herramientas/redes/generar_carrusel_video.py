"""
Carrusel en vídeo: cada diapositiva es un vídeo corto (1080x1350, 4:5) en vez de una imagen fija.
Prueba de MiHuertoUrbano pedida por Jesús el 27-11-2026 («carrusel pero vídeo en cada diapositiva»).

Usa el mismo motor que los reels (generar_historia.py) en modo "formato": "4:5" y sin voz: el texto de cada
escena ("voz") sale como subtítulo que se enciende palabra a palabra y la escena se anima debajo.
Instagram acepta vídeos de 3 a 60 s dentro de un carrusel; aquí cada diapositiva dura 4-7 s.

Uso:
  python3 herramientas/redes/generar_carrusel_video.py configs/mihuerto/<slug>.json
Config: {"slug", "tema", "marca", "palabra", "diapositivas": [{"escenas": [ ...escenas de generar_historia, con "dur"... ]}]}
Salida: reels/<slug>-1.mp4 … reels/<slug>-N.mp4 y reels/<slug>-N.jpg (miniatura de cada diapositiva).
"""
import json, pathlib, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent


def main():
    ruta = pathlib.Path(sys.argv[1]).resolve()
    cfg = json.load(open(ruta))
    salida = RAIZ / "reels"
    salida.mkdir(exist_ok=True)
    hechos = []
    for i, dia in enumerate(cfg["diapositivas"], 1):
        sub = {k: v for k, v in cfg.items() if k != "diapositivas"}
        sub.update({"slug": f"{cfg['slug']}-{i}", "formato": "4:5", "escenas": dia["escenas"]})
        # la config temporal va junto a la original para que las rutas relativas de las imágenes sigan valiendo
        with tempfile.NamedTemporaryFile("w", suffix=".json", dir=ruta.parent, delete=False) as f:
            json.dump(sub, f, ensure_ascii=False)
            tmp = pathlib.Path(f.name)
        try:
            r = subprocess.run([sys.executable, str(AQUI / "generar_historia.py"), str(tmp), "--sin-voz", "--salida", str(salida)],
                               check=True, capture_output=True, text=True)
        finally:
            tmp.unlink()
        info = json.loads(r.stdout.strip().splitlines()[-1])
        if info["segundos"] < 3:
            sys.exit(f"La diapositiva {i} dura {info['segundos']} s; Instagram pide al menos 3 s (sube \"dur\").")
        (salida / f"{cfg['slug']}-{i}-portada.jpg").rename(salida / f"{cfg['slug']}-{i}.jpg")
        hechos.append({"video": f"reels/{cfg['slug']}-{i}.mp4", "miniatura": f"reels/{cfg['slug']}-{i}.jpg", "segundos": info["segundos"]})
    print(json.dumps(hechos, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
