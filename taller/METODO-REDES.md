# Taller de iando · Método para "Redes sociales en piloto automático"

Es la misma fábrica que ya funciona con MiHuertoUrbano (Analista → Estratega →
Fotógrafo → Productor → Revisor → Jesús aprueba → Publicador), montada para un negocio
cliente. Este servicio no se fabrica en una hora: es una **puesta en marcha** (1 semana)
y luego una **cuota mensual**.

## 1. Lo que hace falta del cliente (checklist de arranque)

- Página de Facebook del negocio e Instagram **profesional** vinculado a ella.
- Que añada a Jesús como **administrador de la página** (Configuración de la página →
  Acceso a la página → Añadir persona → control total). Así no hace falta su contraseña.
- Logo, colores, 10-20 fotos reales del negocio (local, productos, equipo) y, si quiere,
  cuentas de la competencia que le gustan o le preocupan.
- Tono (de tú o de usted, cercano o serio), lo que **no** quiere que se publique y cuántas
  publicaciones por semana (recomendado: 3).

## 2. Puesta en marcha (lo hace el taller + Jesús)

| Paso | Quién | Qué |
|---|---|---|
| Ficha | Recepcionista | Ficha de marca: tono, público, servicios, temporadas fuertes, prohibiciones |
| Investigación | Investigador | 4-6 competidores con Instagram profesional (usuario exacto) y qué les funciona |
| Proyecto | Configurador | Fila en `centro.proyectos` (grupo Clientes, `automatico = true`), `centro.competidores` y reglas de marca en `centro.reglas` |
| Token | Jesús | Desde la app de Meta "Centro de mando", token de página permanente del cliente → secreto de Supabase `META_TOKEN_<SLUG>` (como con MiHuerto). Nunca se pega en el chat |
| Agentes | Claude | Copia de las tareas programadas de MiHuerto con la ficha del cliente (temas, tono, fotos del cliente en vez de escenarios de huerto) |
| Primera semana | Fábrica | 3 publicaciones de prueba para que Jesús y el cliente las aprueben antes de activar la publicación automática |

**Pendiente técnico** (se hace con el primer cliente real, ~30 min): el Publicador hoy
publica solo en la página e Instagram de MiHuerto. Hay que darle a cada proyecto sus
propios identificadores (`page_id`, `ig_id`) y el nombre de su secreto, para que cada
publicación salga en la cuenta de su negocio.

## 3. Cada mes

- Informe mensual (ya existe para MiHuerto) enviado al cliente: seguidores, alcance,
  mejores publicaciones y 2-3 recomendaciones.
- Revisión de reglas con lo que el cliente haya pedido cambiar.

## Reglas

- Las fotos del negocio son las del cliente; las ilustraciones o imágenes generadas se
  marcan como tales y nunca se hacen pasar por el local o el equipo real.
- Nada de reseñas, cifras o promociones que el cliente no haya confirmado.
- Nada se publica sin aprobación hasta que el cliente dé el visto bueno a la primera semana.
