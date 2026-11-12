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
3. **Escribir la configuración** `configs/<slug>.json`. Formato completo y ejemplo de todos los tipos:
   `herramientas/redes/ejemplo-visual.json` (es solo un ejemplo de formato: sus datos no valen).

   **Regla principal: cada lámina ENSEÑA la idea, no la cuenta.** La competencia que funciona enseña la
   herramienta funcionando (pantallas, resultados, números). Nada de láminas que sean solo una lista de
   viñetas sobre fondo liso: como mucho **una** lámina de tipo `punto` o `lista` por carrusel (el
   generador avisa si hay más).

   | Si la idea es… | Usa | Qué se ve |
   |---|---|---|
   | Cómo se le pide algo a una IA / cómo contesta un cliente | `chat` | móvil con la conversación (`app`: `asistente` o `whatsapp`) |
   | El resultado que entrega (comparativa, lista de precios, informe) | `tabla` | ventana con la tabla y un `globo` con lo importante |
   | Para qué sirve en un negocio (tareas, casos de uso) | `tarjetas` | 2-4 tarjetas con icono |
   | Cómo empezar / pasos a seguir | `pasos` | línea de 3-5 pasos numerados |
   | La frase exacta para copiar | `prompt` | ventana con el prompt y los [huecos] en color |
   | Un número que impacta (precio, tiempo, %) | `cifra` | número gigante + antes/después |
   | Lo viejo frente a lo nuevo | `versus` | dos columnas con `mensajes`, `pasos` o `items` |

   - 6-8 láminas: `portada` → 4-6 visuales → `cierre`. **Variedad**: no repitas tipo seguido.
   - **Portada**: gancho con un ejemplo concreto, no un tema ("Le pides «búscame 3 proveedores» y te los
     trae comparados", no "Agentes de IA: qué son"). Título ≤ 12 palabras. Si encaja, añade `chat` con la
     conversación que lo demuestra (sale un móvil al lado y es lo que más para el scroll).
   - Títulos ≤ 8 palabras; textos de apoyo ≤ 20 palabras. Usa `destacado` para la palabra clave.
   - Iconos de `tarjetas`: nombres de la lista (`python3 herramientas/redes/generar_carrusel.py --iconos`).
   - **Nada inventado también en lo visual**: los mensajes del chat, las filas de la tabla y las cifras
     tienen que salir del artículo (o ser un ejemplo marcado como tal en el `globo`: "Ejemplo ilustrativo").
     Nunca precios, tiempos o resultados que el artículo no diga. Nombres genéricos ("Proveedor A",
     "Tu negocio"), nunca marcas o personas reales como si fueran clientes.
   - **Cierre con palabra clave**: pon `"palabra": "UNA_PALABRA"` en la lámina `cierre` y también en la
     publicación (campo `palabra`, ver abajo). Palabra corta, en mayúsculas y relacionada con el tema
     (AGENTE, WHATSAPP, RESEÑAS…), distinta de las de las últimas 4 semanas. Sale «Comenta AGENTE y te
     paso la guía por mensaje privado» y la función `comentarios` se la manda a quien comente.
4. **Generar**: `python3 herramientas/redes/generar_carrusel.py configs/<slug>.json`.
   Si avisa de que una lámina se sale, acorta el texto y repite. **Mira las láminas** (Read de los
   JPG) antes de seguir: texto cortado, palabras raras, láminas vacías o repetidas → corregir.
   Antes de diseñar, mira cómo lo hace la competencia: `centro.competencia_imagenes` (columna `analisis`
   del Vigía y las `imagenes`, que puedes abrir con curl + Read) e inspírate en el formato, nunca copies.
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
| `palabra` | la palabra clave del cierre (p. ej. `AGENTE`) |
| `guia` | lo que se manda a quien comenta la palabra: la URL del artículo (con `?utm_source=instagram&utm_medium=dm`) |
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
   Los tipos visuales se animan solos (los mensajes del chat entran uno a uno, las filas de la tabla, las
   tarjetas y los pasos según se leen). Si con todas las láminas pasa de 60 s, quita del vídeo las menos
   importantes con `"reel": {"omitir": true}` (mínimo: portada, 2-3 visuales y cierre).
2. Comprueba lo que va a leer la voz: `python3 herramientas/redes/generar_reel.py configs/<slug>.json --guion`.
   - **Duración: 45-60 s.** Si pasa de 60 s, acorta más los `"reel"`.
   - Si alguna palabra se va a leer mal (siglas, marcas, inglés), añade en la lámina `"voz"` con cómo
     se dice (`{"titulo": "...", "texto": "..."}`) o amplía `DICCIONARIO` en `generar_reel.py`.
   **Voz (decidido por Jesús el 12-11-2026): voz natural de Gemini "Achird"**, no la de Kokoro. Esta máquina
   no llega a Google, así que la voz se pide a Supabase:
   - `python3 herramientas/redes/generar_reel.py configs/<slug>.json --pedido-voz` imprime 1-2 sentencias SQL.
   - Ejecútalas con la herramienta SQL de Supabase (cada una devuelve un id de `net.http_post`). Espera ~90 s
     y mira el resultado: `select status_code, content from net._http_response where id = <id>`. Si sale
     `"faltan"` > 0 o no hay respuesta, vuelve a ejecutar la MISMA sentencia (lo ya hecho no se repite;
     Google limita unos pocos audios por minuto, así que espera 1 minuto entre intentos).
   - Vuelve a lanzar `--pedido-voz`: cuando diga "Ya están todos los audios", genera el reel.
   - Si el texto cambia, cambian los audios: repite el pedido. Si tras 4 intentos sigue fallando, el
     generador usa Kokoro solo; anótalo en `revision` ("reel con voz de respaldo").
   - El JSON final del generador dice `"voz": "gemini"` o `"kokoro"`. Con Gemini, la voz pronuncia bien
     ChatGPT, WhatsApp, etc.: no hace falta escribirlo "como se dice".
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
  Después 3-5 frases cortas con lo que se aprende en el carrusel y el cierre con la palabra clave:
  "Comenta «AGENTE» y te paso la guía por mensaje privado 📩" (y, debajo, "O en el enlace de la bio 👉
  iando.xyz"). Máximo ~1.200 caracteres.
  En Instagram los enlaces no funcionan en el texto: no pongas URLs.
- **Facebook (`texto_facebook`)**: el mismo mensaje más corto (3-4 frases) y el **enlace directo al
  artículo**. Si encaja, una línea final: "¿Prefieres que te lo monten? https://iando.xyz/servicios.html".
- Correcciones de Jesús: `centro.reglas` del proyecto (ámbitos `general`, `texto`, `imagen`) son
  obligatorias. Si Jesús rechaza una publicación con comentario, léelo y no repitas el fallo.

## Registro

Cada paso a `centro.registro` con `fabrica = 'iando-redes'` (`ok`, `aviso` o `error`) y, al acabar,
un informe corto en `centro.informes` (agente `iando-redes`) con los 3 carruseles y sus fechas.
