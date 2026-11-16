// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(1); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0 || d2.getDay() === 6) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { fr: { nombre: "Revisión de frenos" }, ac: { nombre: "Cambio de aceite y filtros" }, itv: { nombre: "Pre-ITV" }, dg: { nombre: "Diagnosis de avería" } };
const now = new Date().toISOString();
const DATA = {
  negocios: [{ nombre: "Taller de ejemplo", config: { horario: { "1": [["08:30","13:30"],["15:30","19:00"]], "2": [["08:30","13:30"],["15:30","19:00"]], "3": [["08:30","13:30"],["15:30","19:00"]], "4": [["08:30","13:30"],["15:30","19:00"]], "5": [["08:30","13:30"],["15:30","19:00"]], "6": [], "7": [] }, intervalo_min: 30, tema: {"nombre": "Tu taller", "colores": {"fondo": "#f1f3f2", "tarjeta": "#ffffff", "borde": "#d5dceb", "primario": "#1d3b84", "oscuro": "#151a22"}, "fuentes": {"titulos": "Archivo:wght@700;800", "texto": "Atkinson Hyperlegible:wght@400;700"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 168 44\" role=\"img\" aria-label=\"Tu taller\"> <path d=\"M6 9h22l10 10v16a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V12a3 3 0 0 1 3-3Z\" fill=\"#f2c230\"/> <circle cx=\"29\" cy=\"19\" r=\"3.6\" fill=\"#1d3b84\"/> <path d=\"M29 15.4C31 9 26 3 20 4\" fill=\"none\" stroke=\"#dfe6f5\" stroke-width=\"2.2\" stroke-linecap=\"round\"/> <path d=\"M9 24h14M9 30h10\" stroke=\"#151a22\" stroke-width=\"2.4\" stroke-linecap=\"round\"/> <text x=\"48\" y=\"30\" fill=\"#fff\" font-family=\"Archivo, Arial Black, sans-serif\" font-weight=\"800\" font-size=\"21\" style=\"font-stretch:125%\">Tu taller</text> </svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "08:30:00", estado: "confirmada", notas: "Seat León, chirría la rueda delantera", clientes: { nombre: "Antonio R.", telefono: "600111222" }, servicios: S.fr },
    { id: "r2", created_at: now, fecha: F1, hora: "09:30:00", estado: "pendiente", notas: "Le toca la ITV a final de mes", clientes: { nombre: "Marta G.", telefono: "600123456" }, servicios: S.itv },
    { id: "r3", created_at: now, fecha: F1, hora: "11:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Luis P.", telefono: "600333444" }, servicios: S.ac },
    { id: "r4", created_at: now, fecha: F1, hora: "16:00:00", estado: "pendiente", notas: "Se ha encendido el testigo del motor", clientes: { nombre: "Carmen S.", telefono: "600555666" }, servicios: S.dg },
    { id: "r5", created_at: now, fecha: F2, hora: "10:00:00", estado: "pendiente", notas: null, clientes: { nombre: "José M.", telefono: "600777888" }, servicios: S.ac },
  ],
  servicios: [
    { id: "a", nombre: "Cambio de aceite y filtros", precio_desde: 0, duracion_minutos: 45 },
    { id: "b", nombre: "Diagnosis de avería", precio_desde: 0, duracion_minutos: 60 },
    { id: "c", nombre: "Pre-ITV", precio_desde: 0, duracion_minutos: 45 },
    { id: "d", nombre: "Revisión de frenos", precio_desde: 0, duracion_minutos: 60 },
  ],
  dias_bloqueados: [], clientes: [],
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
  const user = { email: "taller@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
