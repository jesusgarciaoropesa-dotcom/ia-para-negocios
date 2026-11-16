// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(1); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0 || d2.getDay() === 6) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { pv: { nombre: "Primera visita y valoración" }, ep: { nombre: "Entrenamiento personal" }, fu: { nombre: "Clase de funcional" } };
const now = new Date().toISOString();
const H = [["07:00","22:00"]];
const DATA = {
  negocios: [{ nombre: "Gimnasio de ejemplo", config: { horario: { "1": H, "2": H, "3": H, "4": H, "5": H, "6": [["09:00","14:00"]], "7": [] }, intervalo_min: 30, tema: {"nombre": "Tu gimnasio", "colores": {"borde": "#d3d8dc", "fondo": "#eceeef", "oscuro": "#1d2125", "tarjeta": "#ffffff", "primario": "#c81e1e"}, "fuentes": {"titulos": "Teko:wght@600", "texto": "Libre Franklin:wght@400;700"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 196 44\" role=\"img\" aria-label=\"Tu gimnasio\"><path d=\"M13 15a9 9 0 0 1 18 0\" fill=\"none\" stroke=\"#ff4d42\" stroke-width=\"4.5\"/><path d=\"M10.5 17h23a11 11 0 0 1 3 7.6 12 12 0 0 1-4.6 9.4H12.1a12 12 0 0 1-4.6-9.4 11 11 0 0 1 3-7.6Z\" fill=\"#ff4d42\"/><rect x=\"15\" y=\"23\" width=\"14\" height=\"6\" rx=\"1\" fill=\"#1d2125\"/><text x=\"46\" y=\"33\" fill=\"#ffffff\" font-family=\"Teko, Impact, sans-serif\" font-weight=\"600\" font-size=\"32\" letter-spacing=\".5\">Tu gimnasio</text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "07:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Marcos P.", telefono: "600111222" }, servicios: S.ep },
    { id: "r2", created_at: now, fecha: F1, hora: "09:30:00", estado: "confirmada", notas: "Vuelvo después de dos años sin entrenar", clientes: { nombre: "Elena M.", telefono: "600123456" }, servicios: S.pv },
    { id: "r3", created_at: now, fecha: F1, hora: "13:00:00", estado: "pendiente", notas: null, clientes: { nombre: "Raúl G.", telefono: "600333444" }, servicios: S.fu },
    { id: "r4", created_at: now, fecha: F1, hora: "18:30:00", estado: "pendiente", notas: "Me molesta un poco la rodilla", clientes: { nombre: "Carmen L.", telefono: "600555666" }, servicios: S.fu },
    { id: "r5", created_at: now, fecha: F1, hora: "20:00:00", estado: "pendiente", notas: null, clientes: { nombre: "Dani T.", telefono: "600777888" }, servicios: S.ep },
    { id: "r6", created_at: now, fecha: F2, hora: "08:00:00", estado: "pendiente", notas: null, clientes: { nombre: "Alba R.", telefono: "600999000" }, servicios: S.ep },
  ],
  servicios: [
    { id: "a", nombre: "Clase de funcional", precio_desde: 0, duracion_minutos: 45 },
    { id: "b", nombre: "Entrenamiento personal", precio_desde: 0, duracion_minutos: 60 },
    { id: "c", nombre: "Primera visita y valoración", precio_desde: 0, duracion_minutos: 30 },
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
  const user = { email: "gimnasio@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
