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
  await p.route('**/*', async (r) => {
    const u = r.request().url();
    if (u.includes('fonts.googleapis.com')) return r.fulfill({ contentType: 'text/css', body: cssFuentes(u) });
    if (u.includes('/__f/')) return r.fulfill({ contentType: 'font/woff2', body: fs.readFileSync(path.join(FS, u.split('/__f/')[1])) });
    if (u.includes('/rest/v1/servicios')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(M.servicios || [{ id: 'a', nombre: 'Servicio', duracion_minutos: 30 }]) });
    if (u.includes('/rest/v1/negocios')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(M.negocio ? [M.negocio] : []) });
    if (u.includes('huecos_libres')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify(M.huecos || ['10:00', '10:30', '11:00', '17:00', '17:30']) });
    if (u.includes('reservar_hueco') || u.includes('/rest/v1/')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ ok: true }) });
    if (u.startsWith(`http://127.0.0.1:${PUERTO}`)) return r.continue();
    return r.abort();
  });
  await p.goto(`http://127.0.0.1:${PUERTO}/index.html`, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.addStyleTag({ content: `.dedo{position:fixed;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;background:rgba(255,255,255,.55);border:2px solid rgba(0,0,0,.25);pointer-events:none;z-index:99999;transform:scale(.6);opacity:0;transition:transform .18s ease-out,opacity .18s}.dedo.on{transform:scale(1);opacity:1}` });

  const desliza = (y, ms) => p.evaluate(([y, ms]) => new Promise((ok) => { const y0 = scrollY, t0 = performance.now(); const e = (t) => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    (function f(now) { const t = Math.min(1, (now - t0) / ms); scrollTo(0, y0 + (y - y0) * e(t)); t < 1 ? requestAnimationFrame(f) : ok(); })(t0); }), [y, ms]);
  const yDe = (sel) => p.evaluate((s) => { const el = document.querySelector(s); return el ? el.getBoundingClientRect().top + scrollY - 70 : null; }, sel);
  const toca = async (sel) => {
    const el = p.locator(sel).first();
    if (!(await el.count())) { console.error('No existe', sel); return; }
    await el.scrollIntoViewIfNeeded(); const bb = await el.boundingBox(); if (!bb) return;
    const x = bb.x + bb.width / 2, y = bb.y + bb.height / 2;
    await p.evaluate(([x, y]) => { const d = document.createElement('div'); d.className = 'dedo'; d.style.left = x + 'px'; d.style.top = y + 'px'; document.body.appendChild(d); requestAnimationFrame(() => d.classList.add('on')); setTimeout(() => { d.classList.remove('on'); setTimeout(() => d.remove(), 250); }, 380); }, [x, y]);
    await espera(p, 230); await el.click(); await espera(p, 320);
  };

  // Grabación con el screencast de Chrome (a 2x de verdad)
  const cdp = await ctx.newCDPSession(p); const cuadros = []; let grabando = false;
  const dirC = path.join(outDir, 'cuadros'); fs.rmSync(dirC, { recursive: true, force: true }); fs.mkdirSync(dirC);
  cdp.on('Page.screencastFrame', async (f) => { if (grabando) { fs.writeFileSync(path.join(dirC, String(cuadros.length).padStart(5, '0') + '.jpg'), Buffer.from(f.data, 'base64')); cuadros.push(f.metadata.timestamp); } try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {} });
  if (!PROBAR) {
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 780, maxHeight: 1688, everyNthFrame: 1 });
    await espera(p, 300); grabando = true;
    await p.evaluate(() => { const d = document.createElement('div'); d.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;opacity:.01;z-index:-1'; document.body.appendChild(d); let i = 0; (function f() { d.style.background = (i++ % 2) ? '#000' : '#fff'; requestAnimationFrame(f); })(); });
  }
  // Acciones: {"esperar":ms} | {"deslizar":"#sel","ms":1100} | {"deslizar_px":800,"ms":900} | {"tocar":"#sel"} |
  //           {"escribir":"#sel","texto":"Lucía"} | {"marcar":"#sel"} | {"elegir":"#select","valor":"..."}
  let n = 0;
  for (const a of cfg.acciones || []) {
    if (a.esperar) await espera(p, a.esperar);
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
    console.log(JSON.stringify({ cuadros: cuadros.length, segundos: cuadros.length ? +(cuadros[cuadros.length - 1] - cuadros[0]).toFixed(1) : 0 }));
  }
  await ctx.close(); await b.close();
})();
