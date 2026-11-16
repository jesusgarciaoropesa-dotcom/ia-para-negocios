# Taller de iando · Guía de diseño

## 0. Estilo «escaparate» (decidido por Jesús el 17-11-2026) — MANDA sobre el resto de la guía

Jesús ha visto este estilo y le gusta más que el anterior. Míralo con Read antes de diseñar:
`taller/ejemplos/escaparate-taller.jpg`, `escaparate-bar.jpg` y `escaparate-pelu-fisio.jpg`.
Lo que hace que funcione: **fotos reales y grandes del sector**, todo lo importante en la
primera página (servicios, reserva, opiniones y dónde está) y un aspecto de negocio serio.
Inspirarse en esa estructura; nunca copiar sus textos, logotipos ni imágenes.

### 0.1 Estructura de la página (de arriba abajo)
1. **Cabecera**: logotipo (SVG con el nombre y debajo una línea de qué es: «Mecánica y servicio
   del automóvil»), menú corto (4-6 enlaces) y el botón principal en el color de acento
   («Reservar cita», «Reservar mesa»).
2. **Inicio a sangre con una foto grande del sector** (todo el ancho, 75-90 % del alto de la
   pantalla en ordenador), con un degradado oscuro (o claro, según la paleta) hacia el lado del
   texto para que se lea. Titular grande en dos líneas que diga lo que gana el cliente
   (se permite una parte del titular en el color de acento, como en las referencias), una frase
   de qué hace el negocio y que se reserva online, y dos botones: el principal (reservar) y uno
   secundario con borde (llamar, ver la carta).
3. **Franja de 3 garantías** con icono SVG y dos líneas cada una («Reserva online 24 horas»,
   «Cocina casera»…). Solo cosas ciertas del negocio o del servicio de reservas.
4. **Servicios / carta**: rejilla de 5-8 tarjetas, cada una con **una foto de ese servicio**, el
   nombre encima de la foto sobre un degradado y, si cabe, una línea («Pastillas, discos y
   líquido»). En móvil, 2 columnas o carrusel horizontal.
5. **Bloque de reserva en la propia página de inicio**: a la izquierda título («Reserva tu cita
   sin llamar»), una frase y una firma manuscrita corta (fuente tipo Caveat/Kalam); a la
   derecha el widget de reservas con los pasos numerados (Servicio · Fecha y hora · Tus datos ·
   Confirmación — aquí los números sí son pasos de verdad). Fondo que contraste con lo de
   alrededor (bloque oscuro sobre fondo claro o al revés).
6. **Opiniones + dónde estamos + mapa** en una misma franja: nota media y número de reseñas de
   Google, una o tres reseñas cortas, dirección, teléfono, botón «Ver en Google Maps» y el mapa
   (iframe sin clave: `https://maps.google.com/maps?q=<dirección codificada>&z=15&output=embed`,
   con `loading="lazy"`).
7. **Pie**: logotipo, Aviso legal · Privacidad · Cookies, redes que tenga, y el botón flotante
   de WhatsApp abajo a la derecha en todas las pantallas.
En negocios de comida, añade una franja final con llamada a reservar («¿Te apetece una buena
tapa?») como en `escaparate-bar.jpg`.

### 0.2 Paleta y letra por sector (punto de partida; los colores de la marca del cliente mandan)
- Taller, motor: grafito casi negro + naranja; sans de rótulo gruesa (Barlow, Archivo, Saira).
- Bar, restaurante: crema cálido + teja + verde oliva; titulares con serifa (Playfair, DM Serif,
  Fraunces) y texto sans.
- Peluquería, estética: negro + dorado suave, o blanco + rosa empolvado; sans elegante.
- Fisio, clínica, salud: blanco + azul intenso; sans limpia (Manrope, Figtree, Plus Jakarta).
- Gimnasio: negro + un color vivo (amarillo, rojo); sans condensada.
- Autoescuela: blanco + un color fuerte de marca (rojo, verde); sans redonda.
Que dos demos seguidas del mismo sector no salgan iguales: cambia al menos acento y tipografía.

### 0.3 Fotos (libres, gratis y sin pedirle nada a Jesús)
Si el encargo trae fotos del cliente, mandan esas. Si no, **fotos de Unsplash con licencia
Unsplash (libre, uso comercial, sin atribución obligatoria)**. Nunca Unsplash+ (de pago), ni
Getty, ni Shutterstock, ni fotos sacadas de webs de otros negocios.
1. Busca con WebSearch `unsplash.com/photos <tema en inglés>` (p. ej. «mechanic brake disc»,
   «spanish tapas croquetas», «physiotherapist knee»). Hace falta 1 foto de inicio + 1 por
   servicio (+ 1 del local si la estructura la usa).
2. Abre cada página con WebFetch pidiendo: la URL completa de la imagen
   (`https://images.unsplash.com/photo-…`), si es Unsplash+ y la descripción. Descarta las de
   `plus.unsplash.com` o `premium_photo`, las que tengan marcas o matrículas muy visibles,
   texto en otro idioma o un ambiente que no pegue con un negocio de pueblo de España.
3. Escribe `demos/<slug>/fotos.json`:
   `{"fotos": [{"nombre": "inicio", "url": "https://images.unsplash.com/photo-…", "ancho": 1800, "alto": 1000},
   {"nombre": "frenos", "url": "…", "ancho": 640, "alto": 480}]}`
   (`foco_y` opcional, de 0 a 1, para elegir qué parte vertical se queda al recortar).
4. Commit y push a `demos`. La acción de GitHub «Fotos de las demos» las baja, recorta y sube a
   `demos/<slug>/img/<nombre>.jpg` en 1-2 minutos. Espera con un bucle (`until git fetch -q origin
   demos && git show origin/demos:demos/<slug>/img/fotos-resultado.json; do sleep 10; done`, máximo
   5 minutos), haz `git pull --rebase` y lee `fotos-resultado.json`: las que tengan `ok: false`,
   cámbialas por otras y repite.
5. **Mira cada foto con Read** (reducida con Pillow si pesa) y comprueba que enseña lo que dice
   la tarjeta (regla de Jesús: las imágenes tienen que corresponder a lo que se dice). Si no,
   cámbiala.
6. En el HTML: rutas relativas `img/<nombre>.jpg`, `width`/`height`, `alt` descriptivo, la del
   inicio con `fetchpriority="high"` y el resto con `loading="lazy"`.

### 0.4 Opiniones: nunca inventadas
- Negocio real: solo la nota media y el número de reseñas reales de su ficha de Google y 1-3
  reseñas reales cortas (nombre de pila e inicial). Si la investigación no las tiene, pon la
  nota real con «Ver reseñas en Google», o quita las reseñas y deja solo dónde estamos y el mapa.
- Demos ficticias («… de ejemplo», para reels): se pueden poner reseñas de ejemplo, con
  «Reseñas de ejemplo» en letra pequeña bajo el bloque.
- Sin fotos de caras en las reseñas: círculo con las iniciales.

### 0.5 Qué cambia del resto de la guía
- La ficha de estilo (parte 1) se sigue haciendo, pero su `estructura` es la de 0.1 y su
  `inicio` es siempre la foto grande; las webs de referencia sirven para colores, letra y fotos.
- De la lista «Lo que delata una web hecha con IA» (parte 2) ya no se aplican: tarjetas con foto
  para los servicios, pasos numerados en la reserva, una parte del titular en color de acento y
  la flecha en el botón «Continuar». El resto sigue (nada de relleno, textos ciertos, móvil
  primero, contraste, un solo color de acento).
- En la revisión visual (parte 3), la nota «Sin rasgos de IA» pasa a ser **«Como las
  referencias escaparate»** (fotos grandes y bien elegidas, todo lo importante en la primera
  página, aspecto de negocio serio). Añade una nota más: **«Fotos que corresponden»**.
- El ejemplo de Mk Racing (final de la guía) queda como referencia de fuerza de color, no de
  estructura.

---


Decidido por Jesús el 13-11-2026: las demos no pueden tener «aspecto de web hecha con IA».
Cada negocio tiene que parecer **suyo**: si tapas el nombre, se tiene que notar que es una
peluquería de Lagartera y no un bar de Talavera. La guía tiene tres partes, que van en este orden:

1. **Ficha de estilo** a partir de webs de referencia (antes de maquetar).
2. **Criterios de diseño** al maquetar.
3. **Revisión visual en rondas** con las capturas (antes de dar la demo por buena).

Lo de abajo es la guía de antes (13-11-2026); vale salvo donde la parte 0 diga otra cosa.
Léela entera antes de maquetar (etapa Maquetador) y otra vez antes de revisar.

---

## 1. Ficha de estilo (Diseñador, antes del Maquetador)

### 1.1 Webs de referencia
Busca **2 webs reales y bien hechas del mismo sector** (mejor de negocios pequeños o de
cadenas cuidadas; en España o fuera), con WebSearch («mejor web peluquería pequeña», «web
restaurante de carretera diseño», sitios de premios como Awwwards o Land-book filtrando por
sector…). Ábrelas con WebFetch y saca de cada una, en texto:

- **Colores**: los 4-6 que más se repiten en su CSS (fondo, texto, acento, secundarios).
- **Tipografías**: familias de titulares y de texto (mira `font-family` y los `<link>` de
  Google Fonts o `@font-face`).
- **Espacios**: si es una web aireada (mucho margen, secciones altas) o compacta; tamaño
  aproximado del texto base y de los titulares.
- **Estructura del inicio**: qué enseña primero (foto grande, carta, titular, horario…).
- **Un detalle** que la haga memorable (una foto a sangre, un menú escrito como pizarra, un
  sello, una forma de presentar los precios…).

Nota: desde la máquina del taller el navegador (Playwright) solo abre páginas locales; las
webs de referencia se leen con WebFetch. Si una no se deja leer, prueba otra.

**Inspirarse, nunca copiar**: ni textos, ni imágenes, ni logotipos, ni la maqueta exacta.
De la referencia se toma el criterio (proporciones, tipo de letra, ritmo), no el diseño.

### 1.2 La ficha
Mezcla lo aprendido con lo que es el negocio (su local, sus fotos, su sector, su público,
sus colores si los tiene; mira `ficha` e `investigacion`). Guárdala en
`centro.encargos.ficha` → clave `estilo`:

```json
{
  "referencias": [{"url": "...", "que_tomo": "ritmo aireado y precios en columna"}],
  "concepto": "Una frase: qué sensación debe dar (p. ej. «barbería de barrio, oficio y madera, sin postureo»)",
  "colores": {"fondo": "#...", "texto": "#...", "acento": "#...", "secundario": "#...", "suave": "#..."},
  "tipografias": {"titulos": "Familia (Google Fonts)", "texto": "Familia (Google Fonts)", "por_que": "..."},
  "inicio": "Qué se ve nada más entrar y por qué es lo más característico del negocio",
  "detalle_memorable": "El único elemento atrevido de la página",
  "estructura": "Esquema en una línea por sección (orden y forma)",
  "evitar": ["lo que en este sector queda a plantilla"]
}
```

Antes de dar la ficha por buena, **compárala con la de las demos anteriores** (`demos/*/`
de esta rama): si se parece a otra en colores, tipografías o estructura del inicio, cámbiala.

---

## 2. Criterios de diseño (Maquetador)

### Lo que da personalidad
- **El inicio enseña lo más característico del negocio**: la foto del local o de un plato, la
  carta del día, el sillón de barbero, el horario si es lo que más se busca… No un titular
  genérico con dos botones porque sí.
- **Tipografía con carácter**: 1 o 2 familias elegidas para ESTE negocio (nunca las de
  siempre: Inter, Roboto, Open Sans, Poppins, Montserrat, Lato salvo que haya un motivo
  claro). Escala clara (p. ej. 17 → 22 → 30 → 44 px), líneas de texto de menos de 80 caracteres.
  Con serifa, algo más de interlineado.
- **Paleta de la ficha**, con contraste suficiente (texto ≥ 4,5:1). Un solo color de acento.
- **Un único elemento atrevido** (el «detalle memorable» de la ficha). Todo lo demás, sobrio.
  Antes de terminar, quita un adorno («mírate al espejo y quítate un complemento»).

### Lo que delata una web hecha con IA (evitar salvo motivo concreto del negocio)
- Etiquetas pequeñas en MAYÚSCULAS con letras separadas encima de cada titular (la clase
  `.eyebrow` de la plantilla: úsala como mucho una vez, o quítala).
- Una palabra del titular en otro color o en cursiva para «destacarla».
- Todo metido en tarjetas iguales con la misma sombra gris y el mismo redondeo.
- Números 01 / 02 / 03 en cosas que no son pasos de verdad.
- Degradados morados o azules de adorno; fondo crema con acento terracota; fondo casi negro
  con un solo acento verde ácido. Son los estilos por defecto de la IA.
- Animaciones de entrada en cada sección y efecto al pasar el ratón en todas las tarjetas.
  Como mucho, un momento animado en toda la página.
- Flechas «→» pegadas a todos los botones y textos tipo «A · B · C».

### Textos dentro del diseño
- Los botones dicen lo que pasa: «Pedir cita por WhatsApp», «Llamar al 925…», no «Enviar».
- Nada de relleno ni frases de folleto («experiencia única», «calidad y profesionalidad»).
  Mejor algo concreto que sea cierto («Abrimos los domingos por la mañana»).

### Suelo de calidad (sin anunciarlo)
Móvil primero (360 px sin desplazamiento horizontal), foco de teclado visible, respeta
`prefers-reduced-motion`, imágenes con `alt`, botones ≥ 44 px.

---

## 3. Revisión visual en rondas (Revisor de calidad)

`qa_landing.py` saca las capturas y da **errores** (técnicos, se arreglan siempre) y
**avisos de diseño** (rasgos de plantilla detectados en el código). Después:

1. Mira con Read `movil-inicio.png`, `movil-completa.png`, `ordenador-inicio.png` y
   `ordenador-completa.png`.
2. Puntúa de 1 a 5, con una frase cada una:
   - **Parece de este negocio** (si tapas el nombre, ¿se adivina el sector y el tipo de sitio?)
   - **Fiel a la ficha de estilo** (colores, tipografías, inicio, detalle memorable)
   - **Jerarquía** (se ve en 3 segundos qué es, dónde está y cómo contactar)
   - **Espacios y ritmo** (ni apelotonado ni vacío; alineaciones limpias)
   - **Sin rasgos de IA** (la lista de arriba y los avisos del script)
3. Si alguna nota es menor de 4: corrige el HTML y repite desde el paso 1.
   **Máximo 3 rondas.** Si tras 3 rondas algo sigue por debajo de 4, déjalo dicho en
   `revision.notas` para Jesús.
4. Guarda en `revision.diseno`: `{"rondas": n, "notas": {"negocio": 4, "ficha": 5,
   "jerarquia": 4, "espacios": 4, "sin_ia": 5}, "cambios": ["qué corregiste en cada ronda"]}`.

Apunta en `demos/NOTAS-DISENO.md` (una línea por demo: negocio, concepto, tipografías,
colores, detalle memorable) para que la siguiente demo no repita lo mismo.

---

## Ejemplo aprobado por Jesús (13-11-2026)

`taller/ejemplos/mk-racing-antes-despues.png` (míralo con Read antes de diseñar). A la izquierda,
la demo de Mk Racing hecha con la plantilla; a la derecha, la versión que le gustó. Lo que aprendimos:

- **Una primera versión sobria (gris hormigón, sin moto) le pareció apagada.** Quiere fuerza:
  un bloque grande con el color de la marca del cliente (si tiene logo, sus colores mandan),
  sin miedo a usarlo a toda potencia.
- **Que se vea lo que hace el negocio en grande**: la moto ocupaba medio inicio. Si hay fotos
  reales del cliente, una foto grande; si no, una ilustración SVG propia, grande y con detalle
  del negocio (su nombre o sus colores en ella).
- Formas con movimiento cuando el sector lo pide (el corte en diagonal en un taller de motos).
- Tipografía de rótulo con carácter para el titular, texto sencillo y legible.
- El detalle memorable (el «parte de trabajo» con los servicios marcados) va en segundo plano,
  no compite con la imagen principal.
