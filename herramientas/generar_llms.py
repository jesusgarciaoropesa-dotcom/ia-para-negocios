#!/usr/bin/env python3
"""Genera llms.txt (resumen de la web para asistentes de IA, formato llmstxt.org) a partir de search-index.json.
Lo llama publicar_articulo.py cada vez que publica; también se puede lanzar a mano: python3 herramientas/generar_llms.py"""
import json
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

def main():
    arts = json.loads((RAIZ / "search-index.json").read_text(encoding="utf-8"))
    por_cat = defaultdict(list)
    for a in arts:
        por_cat[a.get("cat") or "Otros"].append(a)
    out = ["# IA para Negocios (iando.xyz)", "",
           "> Guías prácticas y en español de España sobre cómo usar la inteligencia artificial en pymes, autónomos y negocios locales "
           "(ChatGPT, automatizaciones, marketing, legalidad), y servicios para montar webs con reservas online, redes y automatizaciones.", "",
           "## Servicios", "",
           "- [Servicios: webs, citas online, redes y automatizaciones](https://iando.xyz/servicios.html): qué se monta, para quién y cómo se trabaja.",
           "- [Sobre nosotros](https://iando.xyz/sobre-nosotros.html): quién hay detrás de iando.", ""]
    for cat in sorted(por_cat):
        out += [f"## {cat}", ""]
        for a in sorted(por_cat[cat], key=lambda x: x["title"]):
            out.append(f"- [{a['title']}](https://iando.xyz/{a['url']}): {a.get('desc', '').strip()}")
        out.append("")
    (RAIZ / "llms.txt").write_text("\n".join(out), encoding="utf-8")
    return len(arts)

if __name__ == "__main__":
    print(f"llms.txt con {main()} artículos")
