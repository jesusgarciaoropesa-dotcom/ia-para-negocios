// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(0); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { pv: { nombre: "Primera visita y revisión" }, li: { nombre: "Limpieza dental" }, bl: { nombre: "Blanqueamiento (valoración)" }, or: { nombre: "Ortodoncia invisible (valoración)" }, ur: { nombre: "Urgencia dental" } };
const now = new Date().toISOString();
const H = [["09:30","14:00"],["16:00","20:30"]];
const DATA = {
  negocios: [{ nombre: "Clínica dental de ejemplo", config: { sanitario: true, horario: { "1": H, "2": H, "3": H, "4": H, "5": [["09:30","14:00"]], "6": [], "7": [] }, intervalo_min: 15, tema: {"nombre": "Tu clínica dental", "colores": {"fondo": "#f3f8fa", "tarjeta": "#ffffff", "borde": "#d4e5ec", "primario": "#0a6587", "oscuro": "#0b2233"}, "fuentes": {"titulos": "Sora:wght@700;800", "texto": "Instrument Sans:wght@400;700"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 250 64\" role=\"img\" aria-label=\"Tu clínica dental\"><path d=\"M14 8C8 8 5 14 5 21c0 8 4 13 5 21 1 8 2 16 7.5 16 4.5 0 4.5-10 6.5-14 1-3 3-4.5 6-4.5s5 1.5 6 4.5c2 4 2 14 6.5 14 5.5 0 6.5-8 7.5-16 1-8 5-13 5-21 0-7-3-13-9-13-6 0-10 3.5-16 3.5S20 8 14 8Z\" fill=\"#ffffff\"/><path d=\"M13 16c-3 2-3.5 7-2.5 11\" fill=\"none\" stroke=\"#8fd8ec\" stroke-width=\"3.2\" stroke-linecap=\"round\"/><path d=\"M50 4l1.6 4.4L56 10l-4.4 1.6L50 16l-1.6-4.4L44 10l4.4-1.6Z\" fill=\"#8fd8ec\"/><text x=\"68\" y=\"37\" font-family=\"Sora,Arial,sans-serif\" font-weight=\"800\" font-size=\"29\" fill=\"#ffffff\" letter-spacing=\"-1\">Tu clínica</text><text x=\"69.5\" y=\"55\" font-family=\"Instrument Sans,Arial,sans-serif\" font-weight=\"700\" font-size=\"11\" fill=\"#8fd8ec\" letter-spacing=\"5.2\">DENTAL</text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "09:30:00", estado: "confirmada", notas: "Prefiere a primera hora", clientes: { nombre: "Lucía G.", telefono: "600111222" }, servicios: S.li, servicio_id: "b", cliente_id: "c1" },
    { id: "r2", created_at: now, fecha: F1, hora: "10:30:00", estado: "confirmada", notas: null, clientes: { nombre: "Pablo M.", telefono: "600123456" }, servicios: S.pv, servicio_id: "a", cliente_id: "c2" },
    { id: "r3", created_at: now, fecha: F1, hora: "12:00:00", estado: "pendiente", notas: "Es para mi hija, 9 años", clientes: { nombre: "Rosa S.", telefono: "600333444" }, servicios: S.pv, servicio_id: "a", cliente_id: "c3" },
    { id: "r4", created_at: now, fecha: F1, hora: "13:15:00", estado: "pendiente", notas: null, clientes: { nombre: "Nerea C.", telefono: "600555666" }, servicios: S.ur, servicio_id: "e", cliente_id: "c4" },
    { id: "r5", created_at: now, fecha: F2, hora: "10:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Pedro B.", telefono: "600999000" }, servicios: S.or, servicio_id: "d", cliente_id: "c5" },
    { id: "r6", created_at: now, fecha: F2, hora: "12:30:00", estado: "pendiente", notas: null, clientes: { nombre: "Marta T.", telefono: "600777888" }, servicios: S.bl, servicio_id: "c", cliente_id: "c6" },
  ],
  servicios: [
    { id: "a", nombre: "Primera visita y revisión", precio_desde: 0, duracion_minutos: 30 },
    { id: "b", nombre: "Limpieza dental", precio_desde: 0, duracion_minutos: 45 },
    { id: "c", nombre: "Blanqueamiento (valoración)", precio_desde: 0, duracion_minutos: 30 },
    { id: "d", nombre: "Ortodoncia invisible (valoración)", precio_desde: 0, duracion_minutos: 30 },
    { id: "e", nombre: "Urgencia dental", precio_desde: 0, duracion_minutos: 30 },
  ],
  dias_bloqueados: [], clientes: [{ id: "c1", nombre: "Lucía G.", telefono: "600111222", created_at: now }, { id: "c2", nombre: "Pablo M.", telefono: "600123456", created_at: now }, { id: "c3", nombre: "Rosa S.", telefono: "600333444", created_at: now }, { id: "c4", nombre: "Nerea C.", telefono: "600555666", created_at: now }, { id: "c5", nombre: "Pedro B.", telefono: "600999000", created_at: now }, { id: "c6", nombre: "Marta T.", telefono: "600777888", created_at: now }],
};
class Q {
  constructor(t) { this.t = t; this.f = []; this.o = []; this.one = false; this.lim = null; }
  select() { return this; } insert() { this.w = 1; return this; } update() { this.w = 1; return this; } delete() { this.w = 1; return this; }
  eq(c, v) { this.f.push(r => !(c in r) || String(r[c]) === String(v)); return this; }
  neq(c, v) { this.f.push(r => !(c in r) || String(r[c]) !== String(v)); return this; }
  gte(c, v) { this.f.push(r => !(c in r) || r[c] >= v); return this; }
  lte(c, v) { this.f.push(r => !(c in r) || r[c] <= v); return this; }
  gt(c, v) { this.f.push(r => !(c in r) || r[c] > v); return this; }
  lt(c, v) { this.f.push(r => !(c in r) || r[c] < v); return this; }
  in() { return this; } or() { return this; } is() { return this; }
  order(c, o) { this.o.push([c, o && o.ascending === false ? -1 : 1]); return this; }
  limit(n) { this.lim = n; return this; }
  maybeSingle() { this.one = true; return this; } single() { this.one = true; return this; }
  then(ok, ko) {
    let rows = this.w ? [] : (DATA[this.t] || []).filter(r => this.f.every(fn => fn(r)));
    rows = rows.slice().sort((a, b) => { for (const [c, s] of this.o) { if (a[c] < b[c]) return -s; if (a[c] > b[c]) return s; } return 0; });
    if (this.lim) rows = rows.slice(0, this.lim);
    return Promise.resolve({ data: this.one ? (rows[0] || null) : rows, error: null }).then(ok, ko);
  }
}
export function createClient() {
  const user = { email: "clinica@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
