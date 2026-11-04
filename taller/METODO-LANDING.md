# Taller de iando · Método para fabricar una landing

El taller convierte un encargo de un negocio local en una landing lista para
enseñar al cliente. Es el método que Jesús ya ha usado con clientes reales
(estética, barbería, cervecería, láser…), escrito para que lo sigan los agentes.

Datos del encargo: tabla `centro.encargos` (Supabase `gimoqpusrdltlkrwsykr`).
Archivos: rama `demos` de este repo → `demos/<slug>/index.html` (+ `capturas/`).


> **Publicar de verdad**: GitHub Pages sirve iando.xyz desde la rama `claude/ia-negocios-category-pages-df349r`, no desde `main`. Después de cada `git push origin main`, haz también `git push origin main:claude/ia-negocios-category-pages-df349r` (si dice que no es fast-forward, primero `git fetch origin claude/ia-negocios-category-pages-df349r` y avisa en el registro en vez de forzar).

## Etapas y quién hace qué

| Etapa | Agente | Sale de aquí |
|---|---|---|
| 1 | Recepcionista | `ficha` (JSON) y, si falta algo imprescindible, `preguntas` → estado `preguntas` |
| 2 | Investigador | `investigacion` (JSON) |
| 3 | Redactor de textos | `textos` (JSON) |
| 4 | Maquetador | `demos/<slug>/index.html` |
| 5 | Revisor de calidad | `revision` (JSON) + capturas → estado `para_revisar` |
| — | Jesús | aprueba o pide cambios (`comentario`) en el panel |
| 6 | Entrega | publica en `main` → `https://iando.xyz/demos/<slug>/` y deja el mensaje para el cliente |

### 1. Ficha (Recepcionista)

Campos: `negocio`, `sector`, `tipo_schema` (LocalBusiness más concreto: HairSalon,
BeautySalon, Restaurant, BarOrPub, Store, HardwareStore, LodgingBusiness, Dentist…),
`localidad`, `direccion`, `telefono`, `whatsapp` (formato 34XXXXXXXXX), `email`,
`horario` (por días), `servicios` [{nombre, descripcion, precio?}], `publico`,
`diferencias` (lo que el cliente dice que le hace distinto), `tono`, `colores`
(si los tiene, o propuesta por sector), `redes`, `fotos` (si hay), `objetivo`
(llamadas, WhatsApp, reservas, visitas).

**Imprescindible para seguir**: nombre, sector, localidad, al menos un contacto
(teléfono o WhatsApp) y al menos 3 servicios o productos. Si falta, preguntas
concretas y cortas (máximo 6), pensadas para que Jesús se las mande por WhatsApp.
Lo que no sea imprescindible se deja marcado como "a confirmar" y se sigue.

### 2. Investigación

- Busca el negocio (WebSearch): ficha de Google, web o redes que ya tenga, dirección,
  horario y valoraciones **solo para entender** (nunca se copian reseñas a la web).
- 3-5 competidores de la zona: qué ofrecen, cómo se presentan, qué les falta.
- Búsquedas locales probables: "<servicio> en <localidad>", "<servicio> cerca de mí"…
- Resultado: `{"negocio_en_google": ..., "competidores": [...], "palabras_clave": [...],
  "oportunidades": [...], "fuentes": [...]}`.

### 3. Textos

- Español de España, de tú (o de usted si el tono del negocio lo pide), cercano y claro.
- `seo`: `title` (≤60 caracteres, "<Servicio> en <Localidad> | <Negocio>"),
  `description` (≤155), `h1` con servicio + localidad.
- `hero` (titular corto + subtítulo + botón), `servicios`, `por_que` (3-4 puntos que
  sean **ciertos** según la ficha), `sobre`, `faq` (4-6 preguntas reales del sector),
  `cta_final`.
- **Prohibido inventar**: reseñas, testimonios, años de experiencia, premios, cifras
  de clientes, certificaciones o precios que el cliente no haya dado. Si se quiere un
  dato y no está, se pone en `preguntas` para el cliente.

### 4. Maquetación

Parte de `taller/plantilla-landing.html` y adáptala al negocio (no la dejes con
aspecto de plantilla):

- **Un solo archivo HTML** autocontenido (CSS y JS dentro). Fuentes de Google Fonts
  como mucho 2 familias. Sin librerías externas pesadas.
- Paleta del negocio en las variables `--c-*`; titulares y cuerpo con tipografías que
  encajen con el sector.
- Secciones: cabecera con nombre y botón WhatsApp → hero → servicios → por qué
  elegirnos → sobre el negocio → (galería solo si hay fotos reales) → horario y mapa →
  preguntas frecuentes → contacto → pie (aviso legal y privacidad mínimos).
- **Botón flotante de WhatsApp** en móvil y enlaces `tel:`; mapa con iframe de Google
  Maps por dirección.
- Imágenes: fotos del cliente si las hay; si no, **ilustraciones SVG** propias del
  sector (nunca fotos de banco que parezcan del negocio). Cada imagen con `alt`.
- Datos estructurados: `LocalBusiness` (tipo concreto) con dirección, teléfono,
  horario y `areaServed`, y `FAQPage`.
- Mientras es demo: `<meta name="robots" content="noindex, nofollow">`.
- Móvil primero: legible a 360 px sin desplazamiento horizontal, botones ≥44 px.

### 5. Control de calidad

`python3 taller/qa_landing.py demos/<slug>/index.html --capturas demos/<slug>/capturas`

Comprueba y saca capturas (móvil y ordenador). Además, el Revisor lee las capturas y
revisa a mano: que nada sea inventado, que los textos encajen con la ficha, que el
diseño no parezca de plantilla y que el botón de WhatsApp funcione con el número bueno.
Errores pequeños se arreglan directamente; si hay algo grave, vuelve a la etapa que toque.

### 6. Entrega

Con el encargo `aprobado`: copia `demos/<slug>/` (sin `capturas/`) de la rama `demos`
a `main`, push, `demo_url = https://iando.xyz/demos/<slug>/`, estado `entregado`, y
deja en `revision.mensaje_cliente` un mensaje corto de WhatsApp para que Jesús se lo
mande al cliente con el enlace. La versión definitiva (dominio del cliente, sin
noindex) la monta Jesús cuando el cliente acepta.
