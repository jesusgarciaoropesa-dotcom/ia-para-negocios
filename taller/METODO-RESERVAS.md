# Taller de iando · Método para "Citas y reservas online"

Una web con reservas es **una landing (METODO-LANDING.md) + el bloque de reservas +
el panel de citas** para el negocio. Todo funciona sobre el sistema de reservas que ya
usan la barbería WTJ y la estética Cristina Blanco (Supabase `gimoqpusrdltlkrwsykr`,
esquema `public`, varios negocios separados por `negocio_id`). No se toca nada de esos
dos negocios.

## Piezas

| Pieza | Dónde | Qué hace |
|---|---|---|
| Tablas | `public.negocios`, `servicios`, `reservas`, `clientes`, `dias_bloqueados`, `negocio_admins` | Datos de cada negocio |
| `huecos_libres(negocio, servicio, fecha)` | función SQL | Horas libres según el horario del negocio, la duración del servicio, las citas y los días cerrados |
| `reservar_hueco(...)` | función SQL | Reserva desde la web comprobando que la hora sigue libre (usa `crear_reserva_web`) |
| `taller/reservas/widget-reservas.html` | bloque para la landing | Formulario: servicio → día → hora libre → nombre y teléfono |
| `taller/reservas/admin.html` | panel del negocio | Ver, confirmar y cancelar citas, servicios y días cerrados. Se publica una sola vez en `https://iando.xyz/citas/` y cada negocio entra con `?n=<negocio_id>` |

## Etapas (además de las de la landing)

1. **Recepcionista**: además de lo de la landing, imprescindible: lista de servicios con
   **duración** (minutos) y horario de atención por días. Precio opcional.
2. **Configurador** (`taller-configurador`): crea el negocio y sus servicios:
   ```sql
   insert into public.negocios (nombre, tipo, canal, config) values ('<Negocio>', '<sector>', 'web',
     '{"demo": true, "slug": "<slug>", "horario": {"1": [["09:30","14:00"],["16:30","20:00"]], "2": [...], …, "7": []},
       "intervalo_min": 30, "antelacion_horas": 2, "dias_max": 60, "zona": "Europe/Madrid"}') returning id;
   insert into public.servicios (negocio_id, nombre, precio_desde, duracion_minutos) values (...);
   ```
   Además, para que **el panel de citas tenga el aspecto del negocio**, añade al `config` la clave `tema`
   (sale de `ficha.estilo` y del logotipo de la demo; sin `tema` el panel se ve con el aspecto genérico):
   ```json
   "tema": {"nombre": "Tu bar",
            "colores": {"fondo": "#…", "tarjeta": "#…", "borde": "#… (suave)", "primario": "#… (botones)", "oscuro": "#… (barra de arriba, con texto blanco)"},
            "fuentes": {"titulos": "Alfa Slab One", "texto": "Karla:wght@400;700"},
            "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" …>…</svg>"}
   ```
   Las fuentes se escriben como en Google Fonts (con `:wght@…` solo si la familia tiene esos pesos). El logo
   va sobre el color `oscuro`: que se lea encima. Si el logo se cambia al maquetar, actualiza también el `tema`.
   `1` = lunes … `7` = domingo; día cerrado = `[]`. `intervalo_min` = cada cuánto empieza
   una cita (normalmente 30, o la duración si todas son iguales). Guarda el `negocio_id`
   en `centro.encargos.ficha.negocio_id`.
3. **Maquetador**: monta la landing normal (con su ficha de estilo y `DISENO.md`, como en la
   landing) y pega el bloque `widget-reservas.html`
   (sustituyendo `{{NEGOCIO_ID}}` y `{{WHATSAPP}}`) como sección `#reservar`, adaptando sus
   colores y tipografías a la ficha de estilo. Los botones
   principales de la landing pasan a "Reservar cita" con `href="#reservar"`, y WhatsApp
   queda como alternativa.
4. **Probador** (`taller-probador`), antes del Revisor:
   - `select * from public.huecos_libres('<negocio>', '<servicio>', '<fecha de un martes de la semana que viene>')`
     debe devolver las horas esperadas según el horario.
   - Reserva de prueba como `anon`: `set role anon; select public.reservar_hueco(..., 'PRUEBA taller', '600000000', ...); reset role;`
     debe dar `ok: true`; repetirla a la misma hora debe dar error.
   - **No borres** la reserva ni el cliente de prueba (el borrado pide confirmación y en las pasadas
     automáticas nadie la responde, y el encargo se queda atascado). Déjalos y apunta en
     `revision.prueba_reservas` sus datos (fecha, hora, teléfono `600000000`) y en `revision.notas`
     que Jesús puede borrarlos desde el panel o con este SQL:
     `delete from public.reservas where negocio_id = '<id>' and cliente_id in (select id from public.clientes where negocio_id = '<id>' and telefono = '600000000'); delete from public.clientes where negocio_id = '<id>' and telefono = '600000000';`
     (decidido por Jesús el 16-11-2026).
5. **Revisor de calidad**: como en la landing (el script no puede llamar a Supabase desde
   el taller; la prueba real es la del Probador).

## Entrega

- Igual que la landing (demo en `iando.xyz/demos/<slug>/`).
- Si no existe todavía, publica el panel genérico: `taller/reservas/admin.html` → `main:citas/index.html`
  (con `<meta name="robots" content="noindex, nofollow">`).
- En `revision.mensaje_cliente` explica las dos direcciones: la web y el panel
  `https://iando.xyz/citas/?n=<negocio_id>`.
- **Acceso del negocio al panel** (lo hace Jesús cuando el cliente acepta): en Supabase →
  Authentication → Add user, con el correo del cliente; después
  `insert into public.negocio_admins (user_id, negocio_id) select id, '<negocio_id>' from auth.users where email = '<correo>';`
  Mientras sea demo, Jesús entra con su propio usuario: el Configurador ya lo añade al crear el negocio con
  `insert into public.negocio_admins (user_id, negocio_id) select user_id, '<negocio_id>' from public.negocio_admins where negocio_id = (select id from public.negocios where nombre = 'WTJ Barber Shop') limit 1;`
- Cuando el cliente paga: quitar `"demo": true` del config y llevar la web a su dominio.

## Correos al cliente (confirmación, recordatorio y reseña)

- El formulario pide **correo obligatorio** (va en `clientes.email` a través de `reservar_hueco`).
- La función `reservas-correos` (código en `taller/reservas/correos/index.ts`) manda, con los colores y el nombre del `tema`:
  confirmación al reservar, recordatorio el día a las 8:00 (la tarde anterior a las 20:00 si la cita es antes de las 10:30)
  y petición de reseña 2 h después de la cita (de 9 a 21 h). Marca lo enviado en `reservas.notificaciones_enviadas`.
- Solo funciona en negocios con `config.correos.activo = true`:
  `"correos": {"activo": true, "telefono": "…", "whatsapp": "34…", "responder_a": "correo del negocio", "direccion": "…", "resena_url": "https://g.page/r/…/review"}`.
  Sin `resena_url` no se pide reseña. En demos ficticias se deja apagado.
- Hace falta la clave `RESEND_API_KEY` en Supabase (y el dominio verificado en Resend); sin ella la función no envía nada.
