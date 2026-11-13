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

## Reel con voz (uno por carrusel) · formato «historia»

Cada carrusel tiene también su **reel**, que sale **al día siguiente a las 19:30** (martes, jueves y sábado).
**Formato (decidido por Jesús el 13-11-2026): reel «historia»**, como los reels explicativos que mejor funcionan:
una voz natural cuenta una pequeña historia frase a frase; arriba van subtítulos de 2-3 palabras que se encienden
palabra a palabra (la palabra clave subrayada en amarillo) y debajo, **una escena por frase** que enseña lo que dice
la voz. Generador: `herramientas/redes/generar_historia.py` (tipos de escena explicados al principio del archivo;
ejemplo completo y aprobado: `herramientas/redes/ejemplo-historia.json`).

1. **Escribe el guion como una historia, no como un resumen del carrusel** (`configs/<slug>-historia.json`):
   - **Gancho** en la primera frase: una situación concreta o un dato que choque, sacado del artículo
     («Le pides a la IA que compare los precios de tus cinco competidores»).
   - **Problema o contraste** (cómo se hace hoy, lo que falla) → **cómo funciona**, paso a paso → **remate**
     (la idea que se queda) → **cierre**: «Comenta PALABRA y te paso la guía» (escena `cierre`).
   - **Frases cortas**: 4-12 palabras cada una, una idea por frase. Una frase larga se parte en dos escenas
     (p. ej. la misma `tabla` vacía y luego `completa`).
   - **8-16 escenas, 25-50 s.** El generador avisa si pasa de 60 s.
   - En cada escena, `clave` = la palabra de la frase que se subraya (la importante).
   - Elige el tipo que ENSEÑA la frase: `chat` (pedírselo a la IA / respuesta), `lista` (tareas a mano), `ventanas`
     (la IA recorre webs o herramientas), `tabla` (el resultado que entrega), `cifra` (número que sube), `aviso`
     (notificación), `versus` (antes → ahora), `prompt` (la frase para copiar), `tarjetas`, `pasos`, `frase` (texto
     gigante para un gancho). No repitas el mismo tipo más de dos veces seguidas salvo que la escena continúe
     (chat con `desde`, tabla que se completa). Usa `sello` (1-2 por reel) para remarcar un giro («TÚ HACES LOS PASOS»).
   - **Nada inventado**: lo que dice la voz y lo que sale en pantalla está en el artículo. Nada de precios, tiempos
     o resultados que el artículo no diga; en tablas sin datos del artículo, deja las celdas vacías (salen barras).
2. **Voz** (Gemini «Achird»): `python3 herramientas/redes/generar_historia.py configs/<slug>-historia.json --pedido-voz`
   imprime 1-3 sentencias SQL; ejecútalas con la herramienta SQL de Supabase, espera ~90 s y mira el resultado
   (`select status_code, content from net._http_response where id = <id>`). Si sale `"faltan"` > 0, espera 1 minuto
   y repite la MISMA sentencia. Repite `--pedido-voz` hasta que diga «Ya están todos los audios».
   Puedes ver antes cómo queda sin voz con `--sin-voz` (no lo publiques así).
3. **Genera**: `python3 herramientas/redes/generar_historia.py configs/<slug>-historia.json` → `reels/<slug>.mp4` y
   `reels/<slug>-portada.jpg`. Mira la portada y 4-5 fotogramas (`ffmpeg -ss <segundo> -i reels/<slug>.mp4 -frames:v 1 f.jpg`):
   texto cortado, escenas vacías o que no encajan con la frase → corrige y repite.
4. **Si Gemini no da la voz tras 4 intentos**: haz el reel con el formato anterior (`generar_reel.py`, voz Kokoro de
   respaldo, ver más abajo) y anótalo en `revision` («reel con formato anterior y voz de respaldo»).
5. Sube `reels/` y la config a la rama `redes` y crea la publicación del reel:

| Campo | Valor |
|---|---|
| `tipo` | `reel` |
| `archivos` | `{https://raw.githubusercontent.com/jesusgarciaoropesa-dotcom/ia-para-negocios/redes/reels/<slug>.mp4}` |
| `portada` | la URL raw de `reels/<slug>-portada.jpg` |
| `historia` | vacío |
| `texto` / `texto_facebook` | otra primera línea distinta a la del carrusel (que no parezca repetido) |
| `programada_para` | el día siguiente al carrusel, 19:30 Europe/Madrid |
| resto | igual que el carrusel (`articulo`, `hashtags`, `palabra`, `guia`, `estado='para_revisar'`, `revision`) |

### Formato anterior (solo de respaldo): `generar_reel.py`
El carrusel animado con voz: en cada lámina `punto` añade `"reel": {"texto": "..."}` (una frase de 10-16 palabras)
y quita láminas con `"reel": {"omitir": true}` si pasa de 60 s. `--guion` enseña lo que leerá la voz; `--pedido-voz`
pide la voz de Gemini igual que arriba; sin voz de Gemini usa Kokoro. Genera `reels/<slug>.mp4` y su portada.

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
