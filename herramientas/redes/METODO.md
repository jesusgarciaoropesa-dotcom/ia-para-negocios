# Redes de iando · Método del agente de redes

Instagram **@iando.xyz** y la página de Facebook **iando · IA para negocios**.
Objetivo: llevar gente a las guías de iando.xyz y, de ahí, a [servicios](../../servicios.html).

Datos: Supabase `gimoqpusrdltlkrwsykr`, esquema `centro`, tabla `centro.publicaciones`
(proyecto `ia-para-negocios`). Archivos: rama **`redes`** de este repo.
Jesús aprueba cada publicación en el panel "Centro de mando" (pestaña Revisar). La función
`publicar` (cada 15 min) solo sube lo **aprobado**, cuando llega su hora, a las cuentas de iando.

## Qué se hace cada semana

**3 carruseles**, programados para **lunes, miércoles y viernes a las 13:15 (Madrid)** de la semana
siguiente, y **su reel con voz** al día siguiente de cada uno a las 19:30 (ver más abajo).
Cada carrusel nace de **un artículo publicado** en iando.xyz:

1. **Elegir artículos** (ninguno repetido de las últimas 12 semanas en `centro.publicaciones.articulo`):
   - Primero los que Google ya enseña: `centro.search_paginas` (indexada) y búsquedas de
     `centro.search_semanal.consultas` del proyecto.
   - Luego los recién publicados (`centro.articulos` con estado `publicado`).
   - Variedad: no dos de la misma categoría en la semana. Al menos uno muy práctico para un
     negocio pequeño (reservas, WhatsApp, redes, facturas, atención al cliente…), que es donde
     encaja mejor "te lo monto".
2. **Leer el artículo entero** (en `main`) y sacar de él las ideas. **Nada inventado**: cada dato,
   precio, nombre de plan o cifra tiene que estar en el artículo (y si es un precio o una función de
   una herramienta, comprobarlo con WebFetch en la web oficial; si no cuadra, no se pone).
   Nada de casos de clientes, testimonios, ejemplos con nombre de persona ni experiencia de Jesús.
3. **Escribir la configuración** `configs/<slug>.json` (ver tipos de lámina en `generar_carrusel.py`):
   - 6-9 láminas: `portada` → 4-6 de `punto`/`lista`/`versus` → `cierre`.
   - Portada: promesa clara y concreta (número, beneficio o error a evitar). Título ≤ 8 palabras.
   - Una idea por lámina, frases cortas: título ≤ 6 palabras, texto ≤ 25 palabras.
   - `dato` solo con algo que ayude a actuar (herramienta, precio comprobado, paso).
   - Cierre: "La guía completa está en iando.xyz" (u otro título) + el recuadro de "te lo monto".
4. **Generar**: `python3 herramientas/redes/generar_carrusel.py configs/<slug>.json`.
   Si avisa de que una lámina se sale, acorta el texto y repite. **Mira las láminas** (Read de los
   JPG) antes de seguir: texto cortado, palabras raras, láminas vacías o repetidas → corregir.
5. **Subir** `configs/` y `carruseles/<slug>/` a la rama `redes` (commit + push).
6. **Crear la publicación** en `centro.publicaciones` (una por carrusel):

| Campo | Valor |
|---|---|
| `proyecto_id` | id del proyecto `ia-para-negocios` |
| `tipo` | `carrusel` |
| `redes` | `{instagram,facebook}` |
| `archivos` | URLs `https://raw.githubusercontent.com/jesusgarciaoropesa-dotcom/ia-para-negocios/redes/carruseles/<slug>/01.jpg`… en orden |
| `historia` | la misma URL con `historia.jpg` |
| `texto` | Instagram (ver abajo) |
| `texto_facebook` | Facebook (ver abajo) |
| `hashtags` | 5-8, en español, del tema (`#inteligenciaartificial`, `#pymes`, `#autonomos`, `#automatizacion`…) |
| `articulo` | `https://iando.xyz/articulos/<slug>.html` |
| `programada_para` | lunes/miércoles/viernes 13:15 Europe/Madrid de la semana siguiente |
| `estado` | `para_revisar` |
| `revision` | `{"comprobado": [...], "dudas": [...], "fuentes": [...]}` |

## Reel con voz (uno por carrusel)

Cada carrusel tiene también su **reel**: el mismo contenido animado, con voz en off y sin música,
que sale **al día siguiente a las 19:30** (martes, jueves y sábado).

La voz lee el título y el texto de cada lámina (no los números ni el recuadro del dato, que se
quedan en pantalla); en la portada, título y subtítulo; en el cierre, solo el título y "enlace en la bio".

1. **Escribe la versión corta para el vídeo**: en cada lámina de tipo `punto`, añade
   `"reel": {"texto": "..."}` con el texto resumido en **una frase de 10-16 palabras** (la misma
   idea, sin datos nuevos). Se ve y se lee en el reel en lugar del texto del carrusel.
2. Comprueba lo que va a leer la voz: `python3 herramientas/redes/generar_reel.py configs/<slug>.json --guion`.
   - **Duración: 45-60 s.** Si pasa de 60 s, acorta más los `"reel"`.
   - Si alguna palabra se va a leer mal (siglas, marcas, inglés), añade en la lámina `"voz"` con cómo
     se dice (`{"titulo": "...", "texto": "..."}`) o amplía `DICCIONARIO` en `generar_reel.py`.
3. Genera: `python3 herramientas/redes/generar_reel.py configs/<slug>.json` → `reels/<slug>.mp4` y
   `reels/<slug>-portada.jpg`. Tarda unos minutos. Mira la portada y 3-4 fotogramas
   (`ffmpeg -ss <segundo> -i reels/<slug>.mp4 -frames:v 1 f.jpg`) antes de seguir.
4. Sube `reels/` a la rama `redes` y crea otra publicación:

| Campo | Valor |
|---|---|
| `tipo` | `reel` |
| `archivos` | `{https://raw.githubusercontent.com/jesusgarciaoropesa-dotcom/ia-para-negocios/redes/reels/<slug>.mp4}` |
| `portada` | la URL raw de `reels/<slug>-portada.jpg` |
| `historia` | vacío |
| `texto` / `texto_facebook` | otra primera línea distinta a la del carrusel (que no parezca repetido) |
| `programada_para` | el día siguiente al carrusel, 19:30 Europe/Madrid |
| resto | igual que el carrusel (`articulo`, `hashtags`, `estado='para_revisar'`, `revision`) |

## Textos

- Español de España, de tú, claro, sin tecnicismos ni promesas exageradas ("multiplica tus ventas"…).
- **Instagram (`texto`)**: primera línea = gancho (es lo único que se ve sin pulsar "más").
  Después 3-5 frases cortas con lo que se aprende en el carrusel, una pregunta para comentar y el
  cierre: "La guía completa, con el enlace de la bio 👉 iando.xyz". Máximo ~1.200 caracteres.
  En Instagram los enlaces no funcionan en el texto: no pongas URLs.
- **Facebook (`texto_facebook`)**: el mismo mensaje más corto (3-4 frases) y el **enlace directo al
  artículo**. Si encaja, una línea final: "¿Prefieres que te lo monten? https://iando.xyz/servicios.html".
- Correcciones de Jesús: `centro.reglas` del proyecto (ámbitos `general`, `texto`, `imagen`) son
  obligatorias. Si Jesús rechaza una publicación con comentario, léelo y no repitas el fallo.

## Registro

Cada paso a `centro.registro` con `fabrica = 'iando-redes'` (`ok`, `aviso` o `error`) y, al acabar,
un informe corto en `centro.informes` (agente `iando-redes`) con los 3 carruseles y sus fechas.
