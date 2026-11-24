// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 1) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(1); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0 || d2.getDay() === 1) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { ma: { nombre: "Manicura semipermanente" }, ge: { nombre: "Uñas de gel (nuevo set)" }, re: { nombre: "Relleno de gel" }, li: { nombre: "Lifting de pestañas" }, ce: { nombre: "Diseño de cejas" }, de: { nombre: "Depilación con cera, piernas" } };
const now = new Date().toISOString();
const H = [["10:00","14:00"],["16:00","20:00"]];
const DATA = {
  negocios: [{ nombre: "Estudio de uñas y estética de ejemplo", config: { horario: { "1": [], "2": H, "3": H, "4": H, "5": H, "6": H, "7": [] }, intervalo_min: 15, tema: {"nombre": "Tu estudio", "colores": {"fondo": "#fbf4f3", "tarjeta": "#ffffff", "borde": "#efd9d6", "primario": "#b02e5c", "oscuro": "#2b1622"}, "fuentes": {"titulos": "Urbanist:wght@700;800", "texto": "Mulish:wght@400;700"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 230 64\" role=\"img\" aria-label=\"Tu estudio · Uñas y estética\"><rect x=\"14\" y=\"2\" width=\"12\" height=\"22\" rx=\"3\" fill=\"#ffffff\"/><rect x=\"11\" y=\"22\" width=\"18\" height=\"5\" rx=\"1.5\" fill=\"#ffffff\"/><path d=\"M8 30c0-2 1.5-3 3-3h18c1.5 0 3 1 3 3v24c0 4-3 7-7 7H15c-4 0-7-3-7-7z\" fill=\"#e8799f\"/><path d=\"M12 35h3v18h-3z\" fill=\"#ffffff\" opacity=\".55\"/><text x=\"44\" y=\"38\" font-family=\"Urbanist,Arial,sans-serif\" font-weight=\"800\" font-size=\"31\" fill=\"#ffffff\" letter-spacing=\"-0.5\">Tu estudio</text><text x=\"45\" y=\"56\" font-family=\"Mulish,Arial,sans-serif\" font-weight=\"700\" font-size=\"10.5\" fill=\"#f3c6d4\" letter-spacing=\"2.6\">UÑAS Y ESTÉTICA</text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "10:00:00", estado: "confirmada", notas: "Rosa nude, como la última vez", clientes: { nombre: "Lucía M.", telefono: "600111222" }, servicios: S.re },
    { id: "r2", created_at: now, fecha: F1, hora: "11:15:00", estado: "confirmada", notas: null, clientes: { nombre: "Paula G.", telefono: "600123456" }, servicios: S.ma },
    { id: "r3", created_at: now, fecha: F1, hora: "12:30:00", estado: "pendiente", notas: "Primera vez", clientes: { nombre: "Rocío S.", telefono: "600333444" }, servicios: S.li },
    { id: "r4", created_at: now, fecha: F1, hora: "16:00:00", estado: "pendiente", notas: "Almendradas, largo medio", clientes: { nombre: "Nerea C.", telefono: "600555666" }, servicios: S.ge },
    { id: "r5", created_at: now, fecha: F1, hora: "18:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Ana B.", telefono: "600999000" }, servicios: S.ce },
    { id: "r6", created_at: now, fecha: F2, hora: "17:00:00", estado: "pendiente", notas: null, clientes: { nombre: "Rosa T.", telefono: "600777888" }, servicios: S.de },
  ],
  servicios: [
    { id: "a", nombre: "Depilación con cera, piernas", precio_desde: 0, duracion_minutos: 40 },
    { id: "b", nombre: "Diseño de cejas", precio_desde: 0, duracion_minutos: 20 },
    { id: "c", nombre: "Lifting de pestañas", precio_desde: 0, duracion_minutos: 60 },
    { id: "d", nombre: "Manicura semipermanente", precio_desde: 0, duracion_minutos: 45 },
    { id: "e", nombre: "Relleno de gel", precio_desde: 0, duracion_minutos: 60 },
    { id: "f", nombre: "Uñas de gel (nuevo set)", precio_desde: 0, duracion_minutos: 90 },
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
  const user = { email: "estudio@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
