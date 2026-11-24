// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(0); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { co: { nombre: "Consulta general" }, va: { nombre: "Vacunación" }, re: { nombre: "Revisión anual" }, pe: { nombre: "Peluquería canina" }, de: { nombre: "Desparasitación" } };
const now = new Date().toISOString();
const H = [["09:30","13:30"],["17:00","20:30"]];
const DATA = {
  negocios: [{ nombre: "Clínica veterinaria de ejemplo", config: { horario: { "1": H, "2": H, "3": H, "4": H, "5": H, "6": [["10:00","13:00"]], "7": [] }, intervalo_min: 15, tema: {"nombre": "Tu clínica", "colores": {"fondo": "#f3f8f6", "tarjeta": "#ffffff", "borde": "#d7e8e1", "primario": "#0b7266", "oscuro": "#0f2f2b"}, "fuentes": {"titulos": "Bricolage Grotesque:wght@700;800", "texto": "Schibsted Grotesk:wght@400;700"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 240 64\" role=\"img\" aria-label=\"Tu clínica · Veterinaria\"><rect x=\"20\" y=\"6\" width=\"20\" height=\"52\" rx=\"6\" fill=\"#f6c453\"/><rect x=\"4\" y=\"22\" width=\"52\" height=\"20\" rx=\"6\" fill=\"#f6c453\"/><ellipse cx=\"30\" cy=\"37.5\" rx=\"6.8\" ry=\"5.6\" fill=\"#0f2f2b\"/><circle cx=\"21.8\" cy=\"30\" r=\"2.7\" fill=\"#0f2f2b\"/><circle cx=\"26.6\" cy=\"25.6\" r=\"2.7\" fill=\"#0f2f2b\"/><circle cx=\"33.4\" cy=\"25.6\" r=\"2.7\" fill=\"#0f2f2b\"/><circle cx=\"38.2\" cy=\"30\" r=\"2.7\" fill=\"#0f2f2b\"/><text x=\"66\" y=\"38\" font-family=\"Bricolage Grotesque,Arial,sans-serif\" font-weight=\"800\" font-size=\"31\" fill=\"#ffffff\" letter-spacing=\"-0.6\">Tu clínica</text><text x=\"67\" y=\"56\" font-family=\"Schibsted Grotesk,Arial,sans-serif\" font-weight=\"700\" font-size=\"10.6\" fill=\"#9fd6c8\" letter-spacing=\"3\">VETERINARIA</text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "09:30:00", estado: "confirmada", notas: "Luna, gata de 2 años", clientes: { nombre: "Ana R.", telefono: "600111222" }, servicios: S.va, servicio_id: "e", cliente_id: "c1" },
    { id: "r2", created_at: now, fecha: F1, hora: "10:15:00", estado: "confirmada", notas: "Toby, caniche. Corte corto", clientes: { nombre: "Carmen S.", telefono: "600123456" }, servicios: S.pe, servicio_id: "c", cliente_id: "c2" },
    { id: "r3", created_at: now, fecha: F1, hora: "12:00:00", estado: "pendiente", notas: "Rocky, cojea un poco de la pata trasera", clientes: { nombre: "Javier M.", telefono: "600333444" }, servicios: S.co, servicio_id: "a", cliente_id: "c3" },
    { id: "r4", created_at: now, fecha: F1, hora: "17:30:00", estado: "pendiente", notas: "Kira, 8 años", clientes: { nombre: "Nerea C.", telefono: "600555666" }, servicios: S.re, servicio_id: "d", cliente_id: "c4" },
    { id: "r5", created_at: now, fecha: F1, hora: "19:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Pedro B.", telefono: "600999000" }, servicios: S.de, servicio_id: "b", cliente_id: "c5" },
    { id: "r6", created_at: now, fecha: F2, hora: "10:00:00", estado: "pendiente", notas: "Cachorro, primera vacuna", clientes: { nombre: "Rosa T.", telefono: "600777888" }, servicios: S.va, servicio_id: "e", cliente_id: "c6" },
  ],
  servicios: [
    { id: "a", nombre: "Consulta general", precio_desde: 0, duracion_minutos: 20 },
    { id: "b", nombre: "Desparasitación", precio_desde: 0, duracion_minutos: 15 },
    { id: "c", nombre: "Peluquería canina", precio_desde: 0, duracion_minutos: 60 },
    { id: "d", nombre: "Revisión anual", precio_desde: 0, duracion_minutos: 30 },
    { id: "e", nombre: "Vacunación", precio_desde: 0, duracion_minutos: 15 },
  ],
  dias_bloqueados: [], clientes: [{ id: "c1", nombre: "Ana R.", telefono: "600111222", created_at: now }, { id: "c2", nombre: "Carmen S.", telefono: "600123456", created_at: now }, { id: "c3", nombre: "Javier M.", telefono: "600333444", created_at: now }, { id: "c4", nombre: "Nerea C.", telefono: "600555666", created_at: now }, { id: "c5", nombre: "Pedro B.", telefono: "600999000", created_at: now }, { id: "c6", nombre: "Rosa T.", telefono: "600777888", created_at: now }],
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
