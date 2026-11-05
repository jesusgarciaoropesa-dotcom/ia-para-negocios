# Equipo de agentes de iando.xyz

iando.xyz es **a la vez un blog y el escaparate de los servicios de Jesús García**
(webs, reservas online, redes con agentes de IA y automatizaciones para negocios).
Cada artículo tiene que ser útil por sí mismo y, cuando encaje, acercar al lector
a la página [servicios.html](servicios.html) ("Te lo monto").

El trabajo se coordina en Supabase (proyecto `gimoqpusrdltlkrwsykr`, esquema `centro`,
tabla `centro.articulos`) y Jesús aprueba cada artículo en su panel "Centro de mando".

| Agente | Cuándo | Qué hace |
|---|---|---|
| Analista (`iando-analista`) | Lunes | Datos de Google, actualidad de la IA y competencia → ideas de artículos (`estado='idea'`) y propuestas |
| Redactor (`iando-redactor`) | Martes | Escribe 2 nuevos + actualiza 1 antiguo en la rama `borradores` → `para_revisar` |
| Revisor (`iando-revisor`) | Martes | Comprueba datos, precios, enlaces y HTML → notas en `revision` |
| Jesús | Cuando quiera | Aprueba (`aprobado`) o rechaza con comentario en el panel |
| Publicador web (`iando-publicador`) | Cada día | Pasa los aprobados de `borradores` a `main` y los enlaza (`publicado`) |


> **Publicar**: GitHub Pages sirve iando.xyz desde `main` (cambiado el 5-11-2026). Basta con `git push origin main`; copiar también a `claude/ia-negocios-category-pages-df349r` ya no hace falta, aunque no hace daño.

## Ramas

- `main` → lo que se ve en iando.xyz (GitHub Pages publica la raíz de `main`).
- `borradores` → artículos pendientes de aprobar. Vista previa de cada uno:
  `https://raw.githack.com/jesusgarciaoropesa-dotcom/ia-para-negocios/borradores/articulos/<slug>.html`
- Nunca se escribe directamente en `main` salvo el Publicador con artículos aprobados.

## Cómo se escribe un artículo

1. **Plantilla**: copia la estructura completa de un artículo reciente
   (`articulos/agentes-voz-ia-llamadas.html`): misma cabecera, menú, migas de pan,
   datos estructurados (`BreadcrumbList` y `Article`), barra de autor, índice,
   lateral (artículos relacionados + widget "Te lo monto"), recuadro final
   `data-cta-servicios` y pie. Cambia solo lo que es del artículo.
2. **Obligatorio en la cabecera**: `<title>Título | IA para Negocios</title>`,
   meta description (unos 155 caracteres), canonical `https://iando.xyz/articulos/<slug>.html`,
   y la categoría en las migas de pan (una de: `chatgpt-empresas`, `automatizacion-ia`,
   `herramientas-ia`, `ia-marketing`, `ia-por-sector`, `productividad-ia`,
   `ia-ecommerce`, `legal-privacidad-ia`). `datePublished`/`dateModified` con la fecha real.
3. **Contenido**:
   - En español de España, de tú, claro y práctico, pensado para pymes y autónomos.
   - **Datos actuales y comprobados**: cada precio, fecha, ley o función de una
     herramienta sale de una página abierta con WebFetch (web oficial, BOE, documentación).
     Fuentes al final en una sección "Fuentes" con enlaces. Si no se puede comprobar, no se pone.
   - **Nada inventado**: ni casos de clientes, ni testimonios, ni cifras de suscriptores,
     ni experiencias personales de Jesús que no haya contado él.
   - Enlaza 3-5 artículos propios relacionados y, si encaja de forma natural, `../servicios.html`.
   - Sin años desfasados en el título (estamos en el año en curso; revisa la fecha).
4. **Dar de alta** (lo hace el Publicador al publicar):
   `python3 herramientas/publicar_articulo.py articulos/<slug>.html` (nuevo) o
   `... --actualizado` (revisado). Enlaza en categoría, sitemap y buscador.

## Actualizar artículos antiguos

Muchos artículos se escribieron en 2025 y los precios, nombres de planes y
funciones de las herramientas cambian rápido. Cada semana se actualiza uno: se
comprueba todo con fuentes, se corrige, se cambia `dateModified` y el título si
llevaba un año viejo (sin cambiar el slug ni la URL).
