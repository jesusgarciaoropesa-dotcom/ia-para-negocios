// Sustituto de supabase-js solo para sacar capturas del panel sin red. Datos ficticios.
const pad = n => String(n).padStart(2, "0");
const iso = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
function laborable(desde) { const d = new Date(); d.setDate(d.getDate() + desde); while (d.getDay() === 1) d.setDate(d.getDate() + 1); return d; }
const d1 = laborable(1); const d2 = new Date(d1); d2.setDate(d2.getDate() + 1); while (d2.getDay() === 1) d2.setDate(d2.getDate() + 1);
const F1 = iso(d1), F2 = iso(d2);
window.__DEMO_MANANA = F1;
const S = { co: { nombre: "Mesa para comer" }, ce: { nombre: "Mesa para cenar" } };
const now = new Date().toISOString();
const H = [["13:30","16:00"],["20:30","23:00"]];
const DATA = {
  negocios: [{ nombre: "Bar de ejemplo", config: { horario: { "1": [], "2": H, "3": H, "4": H, "5": H, "6": H, "7": H }, intervalo_min: 30, tema: {"nombre": "Tu bar", "colores": {"borde": "#e3d6c1", "fondo": "#faf5ec", "oscuro": "#2f3a22", "tarjeta": "#fffdf8", "primario": "#b4502a"}, "fuentes": {"texto": "Work Sans:wght@400;600;700", "titulos": "DM Serif Display"}, "logo_svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 120 44\" role=\"img\" aria-label=\"Tu bar\"><g transform=\"translate(43 0) scale(.3)\" fill=\"#b9c47a\"><path d=\"M4 44C30 40 60 30 104 8\" fill=\"none\" stroke=\"#b9c47a\" stroke-width=\"3\" stroke-linecap=\"round\"/><ellipse cx=\"26\" cy=\"34\" rx=\"10\" ry=\"4.2\" transform=\"rotate(-48 26 34)\"/><ellipse cx=\"48\" cy=\"25\" rx=\"10\" ry=\"4.2\" transform=\"rotate(-52 48 25)\"/><ellipse cx=\"57\" cy=\"36\" rx=\"10\" ry=\"4.2\" transform=\"rotate(8 57 36)\"/><ellipse cx=\"70\" cy=\"16\" rx=\"10\" ry=\"4.2\" transform=\"rotate(-56 70 16)\"/><ellipse cx=\"80\" cy=\"26\" rx=\"10\" ry=\"4.2\" transform=\"rotate(4 80 26)\"/></g><text x=\"60\" y=\"38\" text-anchor=\"middle\" font-family=\"DM Serif Display, Georgia, serif\" font-size=\"25\" fill=\"#ffffff\" letter-spacing=\"1.2\">TU BAR</text></svg>"} } }],
  reservas: [
    { id: "r1", created_at: now, fecha: F1, hora: "13:30:00", estado: "confirmada", notas: "4 personas", clientes: { nombre: "Lucía M.", telefono: "600111222" }, servicios: S.co },
    { id: "r2", created_at: now, fecha: F1, hora: "14:30:00", estado: "confirmada", notas: "2 personas · en la terraza si se puede", clientes: { nombre: "Javier R.", telefono: "600123456" }, servicios: S.co },
    { id: "r3", created_at: now, fecha: F1, hora: "21:00:00", estado: "pendiente", notas: "6 personas · una trona", clientes: { nombre: "Antonio P.", telefono: "600333444" }, servicios: S.ce },
    { id: "r4", created_at: now, fecha: F2, hora: "20:30:00", estado: "pendiente", notas: "8 personas · cumpleaños", clientes: { nombre: "Marta G.", telefono: "600555666" }, servicios: S.ce },
  ],
  servicios: [
    { id: "a", nombre: "Mesa para cenar", precio_desde: 0, duracion_minutos: 90 },
    { id: "b", nombre: "Mesa para comer", precio_desde: 0, duracion_minutos: 90 },
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
  const user = { email: "bar@ejemplo.es" };
  return {
    auth: { getSession: async () => ({ data: { session: { user } } }), signInWithPassword: async () => ({ data: { user }, error: null }), signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) },
    from: t => new Q(t),
    rpc: async () => ({ data: [], error: null }),
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  };
}
