// Graba en vídeo una demo de iando usada en un móvil (390x844 a 2x), con un «dedo» que marca cada toque.
// Uso: node grabar.js <config.json> <carpeta-demo> <carpeta-salida> [--probar]
//   La demo se sirve en local (montar.py arranca el servidor). Las fuentes de Google se sirven desde
//   node_modules/@fontsource (montar.py las instala) y las llamadas a Supabase se contestan con datos
//   de mentira (config.mocks), así no se toca ninguna reserva real.
//   --probar: en vez de vídeo, guarda una captura después de cada acción (salida/probar-NN.png) para revisar.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [cfgPath, demoDir, outDir] = process.argv.slice(2);
const PROBAR = process.argv.includes('--probar');
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const PUERTO = Number(process.env.PUERTO || 8777);
const FS = path.join(process.cwd(), 'node_modules/@fontsource');
const espera = (p, ms) => p.waitForTimeout(ms);
const INICIO = process.env.INICIO || 'index.html';
const pad2 = (n) => String(n).padStart(2, '0');
const isoDia = (d) => d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
// En mocks.tablas se puede escribir "HOY", "MANANA" o "HOY+3" como fecha: se cambia por la fecha real del día de grabación.
const fechas = (v) => JSON.parse(JSON.stringify(v || {}), (k, x) => {
  if (typeof x !== 'string') return x; const m = x.match(/^(HOY|MANANA)([+-]\d+)?$/); if (!m) return x;
  const d = new Date(); d.setDate(d.getDate() + (m[1] === 'MANANA' ? 1 : 0) + Number(m[2] || 0)); return isoDia(d);
});
// Sustituto de supabase-js para el panel privado (citas/index.html): sesión iniciada y tablas de mentira (mocks.tablas).
// Filtra por eq/neq/gte/lte cuando la fila tiene esa columna; las escrituras cambian solo la copia en memoria.
const SUPABASE_FALSO = `
const T = window.__TABLAS || {};
function consulta(tabla) {
  const filtros = []; let accion = 'select', cambios = null, uno = false, orden = [];
  const filas = () => (T[tabla] || []).filter(r => filtros.every(([op, c, v]) => !(c in r) || (op === 'eq' ? r[c] == v : op === 'neq' ? r[c] != v : op === 'gte' ? r[c] >= v : op === 'lte' ? r[c] <= v : op === 'gt' ? r[c] > v : op === 'lt' ? r[c] < v : true)));
  const q = {
    select() { return q; }, order(c, o) { orden.push([c, !(o && o.ascending === false)]); return q; }, limit() { return q; }, range() { return q; },
    eq(c, v) { filtros.push(['eq', c, v]); return q; }, neq(c, v) { filtros.push(['neq', c, v]); return q; },
    gte(c, v) { filtros.push(['gte', c, v]); return q; }, lte(c, v) { filtros.push(['lte', c, v]); return q; },
    gt(c, v) { filtros.push(['gt', c, v]); return q; }, lt(c, v) { filtros.push(['lt', c, v]); return q; }, in() { return q; }, is() { return q; }, ilike() { return q; }, or() { return q; },
    update(c) { accion = 'update'; cambios = c; return q; }, delete() { accion = 'delete'; return q; },
    insert(c) { accion = 'insert'; cambios = c; return q; }, upsert(c) { accion = 'insert'; cambios = c; return q; },
    single() { uno = true; return q; }, maybeSingle() { uno = true; return q; },
    then(ok, mal) {
      let data;
      if (accion === 'update') { filas().forEach(r => Object.assign(r, cambios)); data = filas(); }
      else if (accion === 'insert') { const n = Object.assign({ id: 'n' + Math.random().toString(36).slice(2) }, cambios); (T[tabla] = T[tabla] || []).push(n); data = [n]; }
      else if (accion === 'delete') { const fuera = new Set(filas()); T[tabla] = (T[tabla] || []).filter(r => !fuera.has(r)); data = []; }
      else { data = filas().slice(); for (const [c, asc] of orden.reverse()) data.sort((a, b) => (a[c] > b[c] ? 1 : a[c] < b[c] ? -1 : 0) * (asc ? 1 : -1)); }
      return Promise.resolve({ data: uno ? (data[0] || null) : data, error: null, count: data.length }).then(ok, mal);
    }
  };
  return q;
}
const usuario = { id: 'u-demo', email: 'demo@ejemplo.com' };
export function createClient() {
  return {
    from: consulta, rpc: () => Promise.resolve({ data: null, error: null }),
    auth: { getSession: async () => ({ data: { session: { user: usuario } } }), signInWithPassword: async () => ({ data: { user: usuario }, error: null }),
      signOut: async () => ({}), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }), getUser: async () => ({ data: { user: usuario } }) },
    channel: () => ({ on() { return this; }, subscribe() { return this; } }), removeChannel() {}
  };
}`;
const slugFuente = (f) => f.toLowerCase().replace(/\+/g, '-').replace(/\s+/g, '-');

function cssFuentes(url) {
  // https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;600&family=DM+Serif+Display
  const u = new URL(url); let css = '';
  for (const fam of u.searchParams.getAll('family')) {
    const [nombre, ejes] = fam.split(':');
    const dir = path.join(FS, slugFuente(nombre), 'files');
    if (!fs.existsSync(dir)) { console.error('Falta la fuente', nombre, '(npm i @fontsource/' + slugFuente(nombre) + ')'); continue; }
    let pesos = ['400'];
    if (ejes) { const m = ejes.match(/wght@(.*)$/); if (m) pesos = m[1].split(';').map(x => x.split(',').pop().split('..')[0]); }
    for (const w of new Set(pesos)) for (const est of ['normal', 'italic']) {
      const f = `${slugFuente(nombre)}-latin-${w}-${est}.woff2`;
      if (fs.existsSync(path.join(dir, f))) css += `@font-face{font-family:'${nombre.replace(/\+/g, ' ')}';font-style:${est};font-weight:${w};font-display:block;src:url(/__f/${slugFuente(nombre)}/files/${f}) format('woff2');}\n`;
    }
  }
  return css;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch({ args: ['--force-device-scale-factor=2'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const M = cfg.mocks || {};
  await ctx.addInitScript((t) => { window.__TABLAS = t; }, fechas(M.tablas));
  await p.route('**/*', async (r) => {
    const u = r.request().url();
    if (u.includes('cdn.jsdelivr.net/npm/@supabase/supabase-js')) return r.fulfill({ contentType: 'application/javascript', body: SUPABASE_FALSO });
    if (u.includes('fonts.googleapis.com')) return r.fulfill({ contentType: 'text/css', body: cssFuentes(u) });
    if (u.includes('/__f/')) return r.fulfill({ contentType: 'font/woff2', body: fs.readFileSync(path.join(FS, u.split('/__f/')[1])) });
    if (u.includes('/rest/v1/servicios')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(M.servicios || [{ id: 'a', nombre: 'Servicio', duracion_minutos: 30 }]) });
    if (u.includes('/rest/v1/negocios')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(M.negocio ? [M.negocio] : []) });
    if (u.includes('huecos_libres')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(M.huecos || ['10:00', '10:30', '11:00', '17:00', '17:30']) });
    if (u.includes('reservar_hueco') || u.includes('/rest/v1/')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ ok: true }) });
    if (u.startsWith(`http://127.0.0.1:${PUERTO}`)) return r.continue();
    return r.abort();
  });
  const ESTILO_DEDO = `.dedo{position:fixed;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;background:rgba(255,255,255,.55);border:2px solid rgba(0,0,0,.25);pointer-events:none;z-index:99999;transform:scale(.6);opacity:0;transition:transform .18s ease-out,opacity .18s}.dedo.on{transform:scale(1);opacity:1}`;
  // Un píxel que cambia en cada fotograma para que Chrome mande cuadros seguidos aunque la página esté quieta
  const parpadeo = () => p.evaluate(() => { const d = document.createElement('div'); d.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:.01;z-index:-1'; document.body.appendChild(d); let i = 0; (function f() { d.style.background = (i++ % 2) ? '#000' : '#fff'; requestAnimationFrame(f); })(); });
  let grabandoYa = false;
  const abre = async (ruta) => { await p.goto(`http://127.0.0.1:${PUERTO}/${ruta.replace(/^\//, '')}`, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready); await p.addStyleTag({ content: ESTILO_DEDO }); if (grabandoYa) await parpadeo(); await espera(p, 250); };
  await abre(INICIO);

  const desliza = (y, ms) => p.evaluate(([y, ms]) => new Promise((ok) => { const y0 = scrollY, t0 = performance.now(); const e = (t) => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    (function f(now) { const t = Math.min(1, (now - t0) / ms); scrollTo(0, y0 + (y - y0) * e(t)); t < 1 ? requestAnimationFrame(f) : ok(); })(t0); }), [y, ms]);
  const yDe = (sel) => p.evaluate((s) => { const el = document.querySelector(s); return el ? el.getBoundingClientRect().top + scrollY - 70 : null; }, sel);
  const marcaDedo = (x, y) => p.evaluate(([x, y]) => { const d = document.createElement('div'); d.className = 'dedo'; d.style.left = x + 'px'; d.style.top = y + 'px'; document.body.appendChild(d); requestAnimationFrame(() => d.classList.add('on')); setTimeout(() => { d.classList.remove('on'); setTimeout(() => d.remove(), 250); }, 380); }, [x, y]);
  // Abre el enlace de WhatsApp del elemento como una conversación de ejemplo dentro del móvil (sin salir de la página)
  const chat = async (sel, nombre) => {
    const el = p.locator(sel).first();
    if (!(await el.count())) { console.error('No existe', sel); return; }
    await el.scrollIntoViewIfNeeded(); const bb = await el.boundingBox(); if (!bb) return;
    await marcaDedo(bb.x + bb.width / 2, bb.y + bb.height / 2); await espera(p, 450);
    const href = await el.getAttribute('href') || ''; let texto = ''; try { texto = new URL(href).searchParams.get('text') || ''; } catch (e) {}
    await p.evaluate(([texto, nombre]) => {
      const c = document.createElement('div');
      c.style.cssText = 'position:fixed;inset:0;z-index:99990;background:#efeae2;font-family:system-ui,sans-serif;transform:translateY(100%);transition:transform .35s ease-out;display:flex;flex-direction:column';
      const ini = (nombre || 'C').trim()[0].toUpperCase();
      c.innerHTML = '<div style="background:#075e54;color:#fff;padding:52px 16px 14px;display:flex;align-items:center;gap:12px"><span style="font-size:22px">‹</span><span style="width:38px;height:38px;border-radius:50%;background:#cfd8dc;color:#37474f;display:grid;place-items:center;font-weight:700">' + ini + '</span><div><b style="font-size:17px">' + nombre + '</b><div style="font-size:12px;opacity:.8">en línea</div></div></div>'
        + '<div style="flex:1;padding:18px 12px;display:flex;flex-direction:column;justify-content:flex-end;gap:8px" id="__chat"></div>'
        + '<div style="background:#f0f0f0;padding:10px 10px 28px;display:flex;gap:8px;align-items:center"><div id="__caja" style="flex:1;background:#fff;border-radius:22px;padding:11px 14px;font-size:15px;color:#111;min-height:20px;max-height:120px;overflow:hidden"></div><span id="__env" style="width:44px;height:44px;border-radius:50%;background:#00a884;display:grid;place-items:center;color:#fff;font-size:20px;transition:transform .15s">➤</span></div>';
      document.body.appendChild(c); requestAnimationFrame(() => { c.style.transform = 'translateY(0)'; });
      window.__chatTexto = texto;
    }, [texto, nombre || 'Cliente']);
    await espera(p, 700);
    await p.evaluate(() => { document.getElementById('__caja').textContent = window.__chatTexto; });
    await espera(p, 1100);
    const env = await p.locator('#__env').boundingBox(); if (env) await marcaDedo(env.x + env.width / 2, env.y + env.height / 2);
    await espera(p, 250);
    await p.evaluate(() => {
      const h = new Date(); const hora = String(h.getHours()).padStart(2, '0') + ':' + String(h.getMinutes()).padStart(2, '0');
      document.getElementById('__caja').textContent = '';
      const b = document.createElement('div');
      b.style.cssText = 'align-self:flex-end;max-width:82%;background:#d9fdd3;border-radius:10px 10px 2px 10px;padding:9px 11px 6px;font-size:15px;line-height:1.35;color:#111;box-shadow:0 1px 1px rgba(0,0,0,.12);opacity:0;transform:translateY(8px);transition:all .25s';
      b.innerHTML = window.__chatTexto.replace(/[<>&]/g, '') + '<div style="text-align:right;font-size:11px;color:#667781;margin-top:3px">' + hora + ' <span style="color:#53bdeb">✓✓</span></div>';
      document.getElementById('__chat').appendChild(b); requestAnimationFrame(() => { b.style.opacity = 1; b.style.transform = 'none'; });
    });
    await espera(p, 600);
  };
  const toca = async (sel) => {
    const el = p.locator(sel).first();
    if (!(await el.count())) { console.error('No existe', sel); return; }
    await el.scrollIntoViewIfNeeded(); const bb = await el.boundingBox(); if (!bb) return;
    const x = bb.x + bb.width / 2, y = bb.y + bb.height / 2;
    await marcaDedo(x, y);
    await espera(p, 230); await el.click(); await espera(p, 320);
  };

  // Grabación con el screencast de Chrome (a 2x de verdad)
  const cdp = await ctx.newCDPSession(p); const cuadros = []; let grabando = false;
  const dirC = path.join(outDir, 'cuadros'); fs.rmSync(dirC, { recursive: true, force: true }); fs.mkdirSync(dirC);
  cdp.on('Page.screencastFrame', async (f) => { if (grabando) { fs.writeFileSync(path.join(dirC, String(cuadros.length).padStart(5, '0') + '.jpg'), Buffer.from(f.data, 'base64')); cuadros.push(f.metadata.timestamp); } try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {} });
  if (!PROBAR) {
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 780, maxHeight: 1688, everyNthFrame: 1 });
    await espera(p, 300); grabando = true;
    await parpadeo(); grabandoYa = true;
  }
  // Acciones: {"esperar":ms} | {"deslizar":"#sel","ms":1100} | {"deslizar_px":800,"ms":900} | {"tocar":"#sel"} |
  //           {"escribir":"#sel","texto":"Lucía"} | {"marcar":"#sel"} | {"elegir":"#select","valor":"..."}
  //           {"paso":2} (marca dónde empieza cada paso del reel «sistema completo») | {"ir":"citas/index.html?n=demo"}
  //           {"whatsapp":"#hojaCont a.wa","nombre":"Lucía"} (enseña el mensaje de WhatsApp como conversación de ejemplo)
  //           En selectores y textos, {HOY} y {MANANA} se cambian por la fecha del día (AAAA-MM-DD).
  let n = 0; const pasos = [];
  const hoyIso = isoDia(new Date()), mananaIso = isoDia(new Date(Date.now() + 864e5));
  cfg.acciones = JSON.parse(JSON.stringify(cfg.acciones || []).replace(/\{HOY\}/g, hoyIso).replace(/\{MANANA\}/g, mananaIso));
  const ahora = () => (cuadros.length ? cuadros[cuadros.length - 1] - cuadros[0] : 0);
  for (const a of cfg.acciones || []) {
    if (a.paso != null) pasos.push({ paso: a.paso, t: +ahora().toFixed(3) });
    else if (a.ir) await abre(a.ir);
    else if (a.whatsapp) await chat(a.whatsapp, a.nombre);
    else if (a.esperar) await espera(p, a.esperar);
    else if (a.deslizar) { const y = await yDe(a.deslizar); if (y == null) console.error('No existe', a.deslizar); else await desliza(y, a.ms || 1100); }
    else if (a.deslizar_px != null) await desliza(a.deslizar_px, a.ms || 1000);
    else if (a.tocar) await toca(a.tocar);
    else if (a.escribir) { const el = p.locator(a.escribir).first(); if (await el.count()) { await el.fill(''); await el.pressSequentially(a.texto, { delay: 45 }); } else console.error('No existe', a.escribir); }
    else if (a.marcar) { const el = p.locator(a.marcar).first(); if (await el.count()) await el.check(); }
    else if (a.elegir) { const el = p.locator(a.elegir).first(); if (await el.count()) await el.selectOption(a.valor ? { value: a.valor } : { index: 1 }); }
    if (PROBAR) await p.screenshot({ path: path.join(outDir, `probar-${String(++n).padStart(2, '0')}.png`) });
  }
  if (!PROBAR) {
    grabando = false; await cdp.send('Page.stopScreencast');
    let lista = ''; for (let i = 0; i < cuadros.length; i++) { const d = i + 1 < cuadros.length ? cuadros[i + 1] - cuadros[i] : 0.04; lista += `file 'cuadros/${String(i).padStart(5, '0')}.jpg'\nduration ${d.toFixed(4)}\n`; }
    lista += `file 'cuadros/${String(cuadros.length - 1).padStart(5, '0')}.jpg'\n`;
    fs.writeFileSync(path.join(outDir, 'cuadros.txt'), lista);
    fs.writeFileSync(path.join(outDir, 'pasos.json'), JSON.stringify(pasos));
    console.log(JSON.stringify({ cuadros: cuadros.length, segundos: cuadros.length ? +(cuadros[cuadros.length - 1] - cuadros[0]).toFixed(1) : 0 }));
  }
  await ctx.close(); await b.close();
})();
