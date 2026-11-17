// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(1); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 0 || d2.getDay() === 6) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { co: { nombre: "Clase práctica de coche" }, mo: { nombre: "Clase práctica de moto" }, in: { nombre: "Información y matrícula" } };
const now = new Date().toISOString();
const H = [["08:00","14:00"],["16:00","21:00"]];
const DATA = {
  negocios: [{ nombre: "Autoescuela de ejemplo", config: { horario: { "1": H, "2": H, "3": H, "4": H, "5": H, "6": [], "7": [] }, intervalo_min: 45, tema: {"nombre": "Tu autoescuela", "colores": {"fondo": "#f5f7f5", "tarjeta": "#ffffff", "borde": "#dbe3dd", "primario": "#12753a", "oscuro": "#0c3a20"}, "fuentes": {"titulos": "Nunito:wght@800;900", "texto": "Nunito Sans:wght@400;700"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 250 48\" role=\"img\" aria-label=\"Tu autoescuela\"><rect x=\"3\" y=\"3\" width=\"42\" height=\"42\" rx=\"8\" fill=\"#12753a\" stroke=\"#ffffff\" stroke-width=\"2.5\"/><path d=\"M15 10h7.5v20H34v8H15Z\" fill=\"#ffffff\"/><text x=\"56\" y=\"33\" fill=\"#ffffff\" font-family=\"Nunito, system-ui, sans-serif\" font-weight=\"900\" font-size=\"26\" textLength=\"186\" lengthAdjust=\"spacingAndGlyphs\">Tu autoescuela</text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "08:00:00", estado: "confirmada", notas: null, clientes: { nombre: "Sara P.", telefono: "600111222" }, servicios: S.co },
    { id: "r2", created_at: now, fecha: F1, hora: "08:45:00", estado: "confirmada", notas: "Quiero practicar rotondas", clientes: { nombre: "Hugo M.", telefono: "600123456" }, servicios: S.co },
    { id: "r3", created_at: now, fecha: F1, hora: "11:00:00", estado: "pendiente", notas: null, clientes: { nombre: "Nerea G.", telefono: "600333444" }, servicios: S.mo },
    { id: "r4", created_at: now, fecha: F1, hora: "16:45:00", estado: "pendiente", notas: "Primera vez, vengo con mi madre", clientes: { nombre: "Iván L.", telefono: "600555666" }, servicios: S.in },
    { id: "r5", created_at: now, fecha: F1, hora: "19:00:00", estado: "pendiente", notas: null, clientes: { nombre: "Laura T.", telefono: "600777888" }, servicios: S.co },
    { id: "r6", created_at: now, fecha: F2, hora: "17:30:00", estado: "pendiente", notas: null, clientes: { nombre: "Óscar R.", telefono: "600999000" }, servicios: S.mo },
  ],
  servicios: [
    { id: "a", nombre: "Clase práctica de coche", precio_desde: 0, duracion_minutos: 45 },
    { id: "b", nombre: "Clase práctica de moto", precio_desde: 0, duracion_minutos: 45 },
    { id: "c", nombre: "Información y matrícula", precio_desde: 0, duracion_minutos: 20 },
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
  const user = { email: "autoescuela@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
