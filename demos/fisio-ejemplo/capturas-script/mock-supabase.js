// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(1); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0 || d2.getDay() === 6) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { pv: { nombre: "Primera valoración" }, se: { nombre: "Sesión de fisioterapia" }, pu: { nombre: "Punción seca" }, ma: { nombre: "Masaje descontracturante" } };
const now = new Date().toISOString();
const H = [["09:00","14:00"],["16:00","20:30"]];
const DATA = {
  negocios: [{ nombre: "Fisio de ejemplo", config: { horario: { "1": H, "2": H, "3": H, "4": H, "5": H, "6": [], "7": [] }, intervalo_min: 30, tema: {"nombre": "Tu fisio", "colores": {"borde": "#d3deec", "fondo": "#eef4fb", "oscuro": "#0d2b57", "tarjeta": "#ffffff", "primario": "#1552c0"}, "fuentes": {"texto": "Manrope:wght@400;600;700", "titulos": "Plus Jakarta Sans:wght@800"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 160 44\" role=\"img\" aria-label=\"Tu fisio\"><circle cx=\"31\" cy=\"8\" r=\"5.5\" fill=\"#7fb0ff\"/><path d=\"M6 20c8 2 15 2.6 22 1.8 5-.7 9.5-2.6 14.5-6\" fill=\"none\" stroke=\"#7fb0ff\" stroke-width=\"5\" stroke-linecap=\"round\"/><path d=\"M27 22c-1 7-2.6 12-7.6 17M27 22c3.4 5 7.6 7.6 13.6 9.4l-2.6 10\" fill=\"none\" stroke=\"#ffffff\" stroke-width=\"5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/><text x=\"52\" y=\"31\" fill=\"#ffffff\" font-family=\"Plus Jakarta Sans, system-ui, sans-serif\" font-weight=\"800\" font-size=\"25\" letter-spacing=\"-.6\">Tu<tspan fill=\"#9cc2ff\">fisio</tspan></text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "09:00:00", estado: "confirmada", notas: "Primera vez, molestia en la rodilla al bajar escaleras", clientes: { nombre: "Lucía M.", telefono: "600111222" }, servicios: S.pv },
    { id: "r2", created_at: now, fecha: F1, hora: "10:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Javier R.", telefono: "600123456" }, servicios: S.se },
    { id: "r3", created_at: now, fecha: F1, hora: "12:30:00", estado: "pendiente", notas: "Me la propuso el fisio en la última sesión", clientes: { nombre: "Pilar G.", telefono: "600333444" }, servicios: S.pu },
    { id: "r4", created_at: now, fecha: F1, hora: "17:00:00", estado: "pendiente", notas: "Espalda cargada del trabajo", clientes: { nombre: "Andrés L.", telefono: "600555666" }, servicios: S.ma },
    { id: "r5", created_at: now, fecha: F2, hora: "16:30:00", estado: "pendiente", notas: null, clientes: { nombre: "Rosa T.", telefono: "600777888" }, servicios: S.se },
  ],
  servicios: [
    { id: "a", nombre: "Masaje descontracturante", precio_desde: 0, duracion_minutos: 45 },
    { id: "b", nombre: "Primera valoración", precio_desde: 0, duracion_minutos: 45 },
    { id: "c", nombre: "Punción seca", precio_desde: 0, duracion_minutos: 30 },
    { id: "d", nombre: "Sesión de fisioterapia", precio_desde: 0, duracion_minutos: 50 },
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
  const user = { email: "clinica@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
