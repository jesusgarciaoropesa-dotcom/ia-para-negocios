# Taller de iando · Método para "Automatizaciones con IA a medida"

Cada negocio pide algo distinto, así que aquí no hay una plantilla única: hay un
**catálogo de automatizaciones ya probadas** que se montan con piezas que Jesús ya
tiene funcionando, y un proceso para las que son nuevas.

## Catálogo (piezas que ya existen)

| Automatización | Con qué se monta | Ya funciona en |
|---|---|---|
| Aviso al negocio de cada reserva nueva | Panel de citas (aviso en el navegador) o bot de Telegram | Estética Cristina Blanco, WTJ (Telegram) |
| Recordatorio de cita al cliente (24 h antes) | Supabase pg_cron + email (Resend) | Hostal La Plata (emails automáticos) |
| Petición de reseña en Google tras la visita | pg_cron + email con el enlace de reseñas de su ficha de Google | Hostal La Plata (email de reseña) |
| Confirmación de reserva por email | Función de Supabase + Resend | Hostal La Plata |
| Publicación automática en redes | Fábrica de contenido (ver METODO-REDES.md) | MiHuertoUrbano |
| Informe semanal o mensual que se hace solo | Tarea programada que lee los datos y escribe el informe | MiHuertoUrbano |
| Lectura de Google (Search Console) | Función `leer-search` | MiHuertoUrbano |

**Importante para emails**: cada negocio necesita su remitente verificado en Resend
(su dominio). Con el remitente de pruebas (`onboarding@resend.dev`) los correos no
llegan a los clientes.

## Proceso para un encargo de automatización

1. **Analista de procesos** (Recepcionista): describe la tarea tal como la hace hoy el
   negocio (quién, cuándo, cuánto tiempo le lleva, con qué herramientas) y qué resultado
   espera. Si encaja en el catálogo, se marca la pieza.
2. **Propuesta**: qué se automatiza, qué sigue haciendo una persona, coste mensual (debe
   ser 0 € o casi: planes gratis de Supabase, Resend, Telegram) y precio cerrado.
   Jesús la aprueba antes de construir nada.
3. **Constructor**: monta la automatización en el Supabase compartido, separada por
   `negocio_id`, sin tocar las de otros negocios.
4. **Probador**: la ejecuta con datos de prueba, comprueba que llega lo que tiene que
   llegar y borra los datos de prueba.
5. **Entrega**: explicación de una página para el negocio (qué pasa solo, qué tiene que
   hacer él, a quién avisar si falla) y aviso en el panel si algo deja de funcionar.

## Reglas

- Siempre una salida a una persona: ninguna automatización contesta sola a un cliente
  sin que se pueda hablar con alguien del negocio.
- Si un mensaje lo escribe una IA y lo recibe un cliente, que se sepa (Reglamento
  Europeo de IA, art. 50, desde agosto de 2026).
- Datos personales: solo los necesarios, y explicados en la política de privacidad del negocio.
