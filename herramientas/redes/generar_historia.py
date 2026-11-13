"""
Reel «historia» de iando (decidido por Jesús el 13-11-2026, inspirado en los reels explicativos que funcionan).

Cómo es: voz natural (Gemini «Achird») que cuenta una pequeña historia frase a frase; arriba, subtítulos de 2-3
palabras que se encienden palabra a palabra (la palabra clave, subrayada en amarillo); debajo, UNA ESCENA POR
FRASE que enseña lo que dice la voz (chat, lista, ventanas, tabla que se rellena, cifra que sube, aviso en el
móvil, comparación, prompt, tarjetas, pasos) y, si hace falta, un sello que cae («TÚ HACES LOS PASOS»).

Uso:
  python3 herramientas/redes/generar_historia.py configs/<slug>-historia.json --pedido-voz   # SQL para pedir las voces
  python3 herramientas/redes/generar_historia.py configs/<slug>-historia.json                # genera el reel
  python3 herramientas/redes/generar_historia.py configs/<slug>-historia.json --sin-voz      # vista previa muda
Salida: reels/<slug>.mp4 y reels/<slug>-portada.jpg. Formato de la configuración: ejemplo-historia.json.

Tipos de escena (todas llevan "voz" = la frase que se lee y, opcional, "clave" = palabra a subrayar,
"sello" = texto de un sello que cae al final de la frase y "tono": "rojo" | "verde"):
  frase     {"texto": "4.000 €", "sub": "..."}                 texto gigante (ganchos, cifras redondas)
  chat      {"nombre": "Chatbot", "inicial": "IA", "color": "#25d366", "mensajes": [{"de": "yo"|"ia", "texto": "..."}], "desde": 0}
            los mensajes a partir de "desde" van apareciendo (el primero «yo» se escribe letra a letra)
  lista     {"items": ["..."], "marcar": false}                lista con casillas (marcar=true las va tachando)
  ventanas  {"titulos": ["Competidor A", ...], "etiqueta": "Agente de IA"}  ventanas que un cursor recorre ✓
  tabla     {"columnas": [...], "filas": [[...], ...], "completa": false}
            celdas vacías ("") se rellenan con barras; con texto, aparece el texto. completa=true: ya llena
  cifra     {"valor": "200", "unidad": "palabras", "texto": "..."}   número que sube hasta el valor
  aviso     {"app": "Tu agente", "texto": "..."}               notificación que baja en un móvil
  versus    {"a": "preguntar", "b": "delegar"}                 la primera se apaga y se enciende la segunda
  prompt    {"app": "ChatGPT", "texto": "Voy a negociar [qué y con quién]…"}  se escribe solo; [huecos] en color
  tarjetas  {"items": [{"icono": "calendar", "titulo": "..."}]}  tarjetas con icono que entran una a una
  pasos     {"pasos": ["...", "..."]}                          pasos numerados que se encienden en orden
  dibujo    {"dibujo": "peluqueria", "vibrar": true, "reserva": false, "globo": {"titulo": "WhatsApp", "texto": "...", "color": "#25d366"}}
            ilustración de dibujos/<nombre>.svg (propias) con móvil que vibra, reserva confirmada y bocadillo
  captura   {"imagen": "capturas/reserva-movil.png", "desplazar": true}  captura real (ruta relativa a la config)
            dentro de un móvil; con desplazar, baja poco a poco como si se hiciera scroll
  cierre    {}  «Comenta PALABRA y te paso la guía». Opcional: "arriba", "palabra", "abajo" para otro cierre
Opcional en la raíz de la config: "musica": "suave" | "animada" (bucles propios de musica.py, sin derechos de nadie):
suena muy baja y baja sola cuando habla la voz.
Nada inventado: todo lo que sale en pantalla y en la voz tiene que estar en el artículo.
"""
import argparse, json, pathlib, subprocess, sys, wave

AQUI = pathlib.Path(__file__).parent
sys.path.insert(0, str(AQUI))
import voz_gemini as G  # noqa: E402
from componentes import icono  # noqa: E402

RAIZ = AQUI.parent.parent
FPS, HUECO, INICIO, FIN = 30, 0.18, 0.35, 1.4

CSS = """
@font-face{font-family:I;font-weight:400;src:url(F/inter-latin-400-normal.woff2)}
@font-face{font-family:I;font-weight:600;src:url(F/inter-latin-600-normal.woff2)}
@font-face{font-family:I;font-weight:800;src:url(F/inter-latin-800-normal.woff2)}
:root{--tinta:#17162b;--gris:#c3c5d0;--indigo:#5b5bd6;--amarillo:#ffd43b;--verde:#1f9d55;--rojo:#e0413a}
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1920px;overflow:hidden;font-family:I,sans-serif;color:var(--tinta);
 background:radial-gradient(120% 70% at 50% 45%,#fbfbfd 0%,#e9eaf0 60%,#d9dbe3 100%)}
#cap{position:absolute;top:300px;left:60px;right:60px;text-align:center;font-size:88px;line-height:1.1;font-weight:400;letter-spacing:-2px}
#cap .w{display:inline-block;margin:0 .12em;color:var(--gris)}
#cap .w.on{color:var(--tinta);font-weight:800}
#cap .w.key{position:relative;z-index:0}
#cap .w.key.on:after{content:"";position:absolute;left:-6px;right:-6px;bottom:6px;height:30px;background:var(--amarillo);z-index:-1;border-radius:4px}
.esc{position:absolute;left:0;right:0;top:600px;height:1080px;display:none;transform:scale(1.15);transform-origin:50% 0}
.card{position:absolute;background:#fff;border-radius:34px;box-shadow:0 30px 70px -24px rgba(23,22,43,.35)}
.centro{left:110px;right:110px;top:40px;padding:34px 36px}
.cab{display:flex;align-items:center;gap:18px;font-weight:800;font-size:32px;margin-bottom:24px}
.av{width:60px;height:60px;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:800;font-size:24px;background:var(--indigo)}
.bur{font-size:36px;line-height:1.3;padding:22px 28px;border-radius:30px;max-width:88%;margin-top:18px;width:fit-content}
.bur.yo{background:var(--indigo);color:#fff;margin-left:auto;border-bottom-right-radius:8px}
.bur.ia{background:#f0f0f5;border-bottom-left-radius:8px}
.sello{position:absolute;left:0;right:0;margin:auto;width:fit-content;top:640px;border:9px solid var(--rojo);color:var(--rojo);font-weight:800;font-size:60px;padding:10px 34px;border-radius:14px;background:rgba(255,255,255,.88);z-index:5;opacity:0}
.sello.verde{border-color:var(--verde);color:var(--verde)}
.li{display:flex;gap:22px;align-items:center;font-size:36px;padding:14px 0;font-weight:600}
.caja{width:44px;height:44px;border:4px solid var(--gris);border-radius:10px;display:grid;place-items:center;font-weight:800;color:#fff;font-size:28px;flex:none}
.caja.si{background:var(--verde);border-color:var(--verde)}
.web{width:330px;height:220px;overflow:hidden}
.web .barra{height:42px;background:#eceef3;display:flex;align-items:center;gap:9px;padding:0 16px;border-radius:34px 34px 0 0}
.web .barra i{width:13px;height:13px;border-radius:50%;background:#d0d3dc}
.web .tit{font-weight:800;font-size:25px;line-height:1.15;padding:18px 90px 8px 22px}
.web .lin{height:16px;border-radius:8px;background:#eceef3;margin:12px 24px}
.tick{position:absolute;right:18px;top:58px;width:60px;height:60px;border-radius:50%;background:var(--verde);color:#fff;display:grid;place-items:center;font-size:34px;font-weight:800}
.cursor{position:absolute;width:60px;height:60px;z-index:9}
.badge{position:absolute;top:-30px;left:0;right:0;margin:auto;width:fit-content;font-weight:800;font-size:28px;padding:10px 22px;border-radius:30px;background:var(--tinta);color:#fff}
.fila{display:grid;align-items:center;gap:20px;font-size:32px;padding:18px 0;border-bottom:2px solid #f0f0f5}
.fila.h{font-weight:800;color:#6b6d80;font-size:26px}
.celda{height:28px;border-radius:14px;background:linear-gradient(90deg,var(--indigo),#8f8ff0)}
.celda.b{background:linear-gradient(90deg,#f3a21b,var(--amarillo))}
.movil{left:270px;width:540px;top:0;height:1040px;background:#17162b;border-radius:70px;padding:20px}
.pant{background:linear-gradient(#3b3a6b,#5b5bd6);height:100%;border-radius:54px;position:relative;overflow:hidden}
.noti{position:absolute;left:22px;right:22px;top:-260px;background:rgba(255,255,255,.96);border-radius:30px;padding:28px 30px;font-size:38px;line-height:1.3}
.noti b{display:block;font-size:26px;color:#6b6d80;margin-bottom:6px;letter-spacing:.5px}
.gigante{position:absolute;width:100%;text-align:center;font-weight:800;letter-spacing:-4px}
.hueco{color:var(--indigo);font-weight:800}
.tarj{position:absolute;left:150px;right:150px;height:190px;display:flex;align-items:center;gap:30px;padding:0 36px;font-size:38px;font-weight:800}
.tarj .ic{width:110px;height:110px;border-radius:28px;background:#efeffb;display:grid;place-items:center;flex:none}
.paso{position:absolute;left:150px;right:150px;height:170px;display:flex;align-items:center;gap:30px;padding:0 36px;font-size:36px;font-weight:600}
.num{width:84px;height:84px;border-radius:50%;background:#efeffb;color:var(--indigo);display:grid;place-items:center;font-weight:800;font-size:40px;flex:none}
.pill{display:inline-block;background:var(--amarillo);font-weight:800;font-size:116px;padding:10px 46px;border-radius:24px;letter-spacing:2px;margin:24px 0}
.marca{position:absolute;bottom:120px;width:100%;text-align:center;font-weight:800;font-size:40px;color:#6b6d80}
"""

JS = r"""
const D = window.DATOS, ESC = window.ESCENAS, PALABRA = window.PALABRA;
const ease = x => x<0?0:x>1?1:1-Math.pow(1-x,3);
const pop = (t,a,d=.35) => ease((t-a)/d);
const esc = s => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;");
const negrita = s => esc(s).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>");
const huecos = s => esc(s).replace(/\[(.+?)\]/g,'<span class="hueco">[$1]</span>');
const raiz = document.getElementById("escenas");
const CUR = '<svg class="cursor" viewBox="0 0 24 24"><path d="M4 2l15 10-7 1 4 8-3 1-4-8-5 5z" fill="#17162b" stroke="#fff" stroke-width="1.5"/></svg>';
const POS = [[110,160],[640,160],[375,430],[110,700],[640,700],[375,950]];

function construir(e,i){
  const d = document.createElement("div"); d.className = "esc"; d.id = "e"+i; let h = "";
  switch(e.tipo){
  case "frase": h = `<div class="gigante" style="top:220px;padding:0 90px;font-size:${e.texto.length>12?118:e.texto.length>8?150:220}px">${esc(e.texto)}</div>`+
     (e.sub?`<div style="position:absolute;top:560px;width:100%;text-align:center;font-size:44px;color:#4a4c60;padding:0 140px">${negrita(e.sub)}</div>`:""); break;
  case "chat": h = `<div class="card centro"><div class="cab"><div class="av"${e.color?` style="background:${e.color}"`:""}>${esc(e.inicial||"IA")}</div>${esc(e.nombre||"Chat de IA")}</div>`+
     e.mensajes.map((m,k)=>`<div class="bur ${m.de==="yo"?"yo":"ia"}" data-k="${k}">${esc(m.texto)}</div>`).join("")+`</div>`; break;
  case "lista": h = `<div class="card centro" style="left:170px;right:170px;top:60px">`+
     e.items.map((t,k)=>`<div class="li" data-k="${k}"><span class="caja">${e.marcar?"✓":""}</span>${esc(t)}</div>`).join("")+`</div>`; break;
  case "ventanas": h = (e.etiqueta?`<div class="badge" style="top:0">${esc(e.etiqueta)}</div>`:"")+
     e.titulos.map((t,k)=>`<div class="card web" data-k="${k}" style="left:${POS[k][0]}px;top:${POS[k][1]}px"><div class="barra"><i></i><i></i><i></i></div><div class="tit">${esc(t)}</div><div class="lin" style="width:70%"></div><div class="lin" style="width:50%"></div><div class="tick" style="opacity:0">✓</div></div>`).join("")+CUR; break;
  case "tabla": { const cols = `grid-template-columns:1.3fr ${"1fr ".repeat(e.columnas.length-1)}`;
     h = `<div class="card centro" style="left:120px;right:120px;top:60px"><div class="fila h" style="${cols}">${e.columnas.map(c=>`<span>${esc(c)}</span>`).join("")}</div>`+
     e.filas.map((f,k)=>`<div class="fila" style="${cols}">${f.map((c,j)=> j===0?`<span>${esc(c)}</span>`: c===""?`<span><div class="celda${j%2===0?" b":""}" data-r="${k}" data-c="${j}"></div></span>`:`<span class="txt" data-r="${k}" data-c="${j}" style="font-weight:800">${esc(c)}</span>`).join("")}</div>`).join("")+`</div>`; break; }
  case "cifra": h = `<div class="gigante cnum" style="top:120px;font-size:300px;color:var(--indigo)">0</div><div style="position:absolute;top:470px;width:100%;text-align:center;font-size:64px;font-weight:800">${esc(e.unidad||"")}</div>`+
     (e.texto?`<div style="position:absolute;top:600px;width:100%;text-align:center;font-size:42px;color:#4a4c60;padding:0 150px;line-height:1.3">${negrita(e.texto)}</div>`:""); break;
  case "aviso": h = `<div class="movil card"><div class="pant"><div style="color:#fff;text-align:center;font-size:120px;font-weight:600;margin-top:150px">9:41</div><div class="noti"><b>${esc((e.app||"Notificación").toUpperCase())} · ahora</b>${esc(e.texto)}</div></div></div>`; break;
  case "versus": h = `<div class="gigante va" style="top:150px;font-size:150px">${esc(e.a)}</div><div class="gigante vf" style="top:400px;font-size:110px;color:var(--indigo);opacity:0">↓</div><div class="gigante vb" style="top:560px;font-size:150px;color:var(--gris)">${esc(e.b)}</div>`; break;
  case "prompt": h = `<div class="card centro" style="top:60px"><div class="cab"><div class="av">IA</div>${esc(e.app||"Tu asistente de IA")}</div><div class="ptxt" style="font-size:38px;line-height:1.4;min-height:300px;background:#f6f6fa;border-radius:22px;padding:26px 30px"></div></div>`; break;
  case "tarjetas": h = e.items.map((t,k)=>`<div class="card tarj" data-k="${k}" style="top:${40+k*220}px"><div class="ic">${window.ICONOS[i+"-"+k]||""}</div>${esc(t.titulo)}</div>`).join(""); break;
  case "pasos": h = e.pasos.map((t,k)=>`<div class="card paso" data-k="${k}" style="top:${40+k*200}px"><div class="num">${k+1}</div>${esc(t)}</div>`).join(""); break;
  case "dibujo": h = `<div class="dib" style="position:absolute;left:90px;right:90px;top:30px">${window.DIBUJOS[e.dibujo]||""}</div>`+
     (e.globo?`<div class="card globo" style="left:${e.globo.x||130}px;top:${e.globo.y||170}px;width:470px;padding:22px 28px;font-size:34px;line-height:1.3"><b style="display:block;font-size:24px;letter-spacing:.5px;color:${e.globo.color||"#6b6d80"}">${esc((e.globo.titulo||"").toUpperCase())}</b>${esc(e.globo.texto)}</div>`:""); break;
  case "captura": h = `<div class="movil card" style="top:0"><div class="pant" style="background:#fff"><img src="${e.src}" style="width:100%;display:block;position:absolute;top:0;left:0"></div></div>`; break;
  case "cierre": h = `<div class="card centro" style="left:120px;right:120px;top:140px;padding:70px 50px;text-align:center"><div style="font-size:54px;font-weight:600">${esc(e.arriba||"Comenta")}</div><div class="pill" style="font-size:${(e.palabra||PALABRA).length>8?84:116}px">${esc(e.palabra||PALABRA)}</div><div style="font-size:42px;line-height:1.3;color:#4a4c60">${e.abajo?negrita(e.abajo):"y te paso la guía<br>por mensaje privado 📩"}</div></div><div class="marca">iando.xyz</div>`; break;
  }
  if(e.sello) h += `<div class="sello ${e.tono==="verde"?"verde":""}">${esc(e.sello)}</div>`;
  d.innerHTML = h; raiz.appendChild(d); return d;
}
const NODOS = ESC.map(construir);
const Q = (d,s) => Array.from(d.querySelectorAll(s));

function animar(e,d,lt,dur){
  switch(e.tipo){
  case "frase": { const a = pop(lt,0,.3); d.querySelector(".gigante").style.transform=`scale(${0.7+0.3*a})`; d.style.opacity=a; break; }
  case "chat": { const desde = e.desde||0, nuevos = e.mensajes.length-desde;
    Q(d,".bur").forEach(b=>{ const k=+b.dataset.k; if(k<desde){ b.style.opacity=1; return; }
      const a0 = (k-desde)*dur*0.85/Math.max(1,nuevos);
      if(k===0 && e.mensajes[0].de==="yo"){ const txt=e.mensajes[0].texto, n=Math.round(txt.length*Math.min(1,lt/(dur*0.8))); b.textContent=txt.slice(0,n)+(n<txt.length?"▍":""); b.style.opacity=1; return; }
      const a = pop(lt,a0+0.1); b.style.opacity=a; b.style.transform=`translateY(${(1-a)*40}px)`; }); break; }
  case "lista": Q(d,".li").forEach(l=>{ const k=+l.dataset.k, n=e.items.length; const a=pop(lt,k*Math.min(.25,dur*.5/n)); l.style.opacity=a;
      if(e.marcar) l.querySelector(".caja").classList.toggle("si", lt > dur*0.25 + k*dur*0.6/n); }); break;
  case "ventanas": { const n=e.titulos.length, per=dur/n;
    Q(d,".web").forEach(w=>{ const k=+w.dataset.k, a=pop(lt,k*0.1,.3); w.style.opacity=a; w.style.marginTop=((1-a)*80)+"px";
      w.querySelector(".tick").style.opacity=pop(lt,0.45+k*per*0.85,.15); });
    const seg=Math.min(n-1,Math.max(0,(lt-0.3)/(per*0.85))), k0=Math.floor(seg), fr=ease(seg-k0), k1=Math.min(n-1,k0+1);
    const c=d.querySelector(".cursor"); c.style.left=(POS[k0][0]+(POS[k1][0]-POS[k0][0])*fr+250)+"px"; c.style.top=(POS[k0][1]+(POS[k1][1]-POS[k0][1])*fr+150)+"px"; break; }
  case "tabla": { const n=e.filas.length;
    Q(d,"[data-r]").forEach(c=>{ const r=+c.dataset.r, j=+c.dataset.c; const a = e.completa?1:ease((lt - r*dur*0.8/n - (j-1)*0.15)/(dur*0.8/n));
      if(c.classList.contains("celda")) c.style.width=(a*(j%2?100:70))+"%"; else c.style.opacity=a; }); break; }
  case "cifra": { const v=parseFloat(String(e.valor).replace(/\./g,"").replace(",",".")), a=ease(lt/(dur*0.6));
    const txt = isNaN(v) ? e.valor : (a>=1? e.valor : Math.round(v*a).toLocaleString("es-ES")); d.querySelector(".cnum").textContent=txt; break; }
  case "aviso": d.querySelector(".noti").style.top = (-260 + pop(lt,0.3,.45)*390)+"px"; break;
  case "versus": { const a=pop(lt,dur*0.5,.3); d.querySelector(".va").style.color = a>.5?"var(--gris)":"var(--tinta)";
    d.querySelector(".vb").style.color = a>.5?"var(--indigo)":"var(--gris)"; d.querySelector(".vb").style.transform=`scale(${1+0.12*a})`; d.querySelector(".vf").style.opacity=a; break; }
  case "prompt": { const t=e.texto, n=Math.round(t.length*Math.min(1,lt/(dur*0.85))); let s=t.slice(0,n);
    const abiertos=(s.match(/\[/g)||[]).length-(s.match(/\]/g)||[]).length; if(abiertos>0) s+="]";
    d.querySelector(".ptxt").innerHTML = huecos(s)+(n<t.length?"▍":""); break; }
  case "tarjetas": case "pasos": { const sel = e.tipo==="tarjetas"?".tarj":".paso", n = (e.items||e.pasos).length;
    Q(d,sel).forEach(c=>{ const k=+c.dataset.k, a=pop(lt,k*dur*0.75/n,.3); c.style.opacity=a; c.style.transform=`translateX(${(1-a)*120}px)`;
      if(e.tipo==="pasos"){ const on = lt >= k*dur*0.75/n; c.querySelector(".num").style.background = on?"var(--indigo)":"#efeffb"; c.querySelector(".num").style.color = on?"#fff":"var(--indigo)"; } }); break; }
  case "dibujo": { const tel=d.querySelector("#telefono"), on=d.querySelector("#ondas"), br=d.querySelector("#brazo");
    if(tel){ tel.style.transform = e.vibrar ? `translateX(${Math.sin(lt*70)*4}px)` : "none"; }
    if(on){ on.style.opacity = e.vibrar ? (0.4+0.6*Math.abs(Math.sin(lt*6))) : 0; }
    if(br){ br.style.transformOrigin="736px 350px"; br.style.transformBox="view-box"; br.style.transform=`rotate(${Math.sin(lt*5)*4}deg)`; }
    if(e.reserva){ const pa=d.querySelector("#pantalla"), ck=d.querySelector("#check"), a=pop(lt,0.3,.3); if(pa) pa.setAttribute("fill", a>.5?"#1f9d55":"#7b7bf0"); if(ck) ck.style.opacity=a; }
    const g=d.querySelector(".globo"); if(g){ const a=pop(lt,0.25,.35); g.style.opacity=a; g.style.transform=`translateY(${(1-a)*30}px) scale(${0.9+0.1*a})`; }
    break; }
  case "captura": { const img=d.querySelector("img"), m=d.querySelector(".movil"), a=pop(lt,0,.35);
    m.style.opacity=a; m.style.transform=`translateY(${(1-a)*60}px)`;
    if(e.desplazar && img.naturalHeight){ const alto=img.clientHeight, vent=img.parentElement.clientHeight; const p=ease(Math.max(0,(lt-0.5)/(dur*0.8)));
      img.style.top = (-(Math.max(0,alto-vent))*p)+"px"; } break; }
  case "cierre": { const a=pop(lt,0,.4), c=d.querySelector(".card"); c.style.opacity=a; c.style.transform=`scale(${0.85+0.15*a})`; break; }
  }
  if(e.sello){ const s=d.querySelector(".sello"), a=pop(lt,dur*0.45,.22); s.style.opacity=a; s.style.transform=`rotate(-7deg) scale(${2.2-1.2*a})`; }
}

function caption(f,t){
  const palabras=f.texto.split(" "), tot=f.texto.length; let acc=0;
  const tiempos=palabras.map(p=>{ const ini=f.ini+f.dur*0.92*acc/tot; acc+=p.length+1; return ini; });
  const trozos=[]; for(let i=0;i<palabras.length;i+=3) trozos.push([i,Math.min(palabras.length,i+3)]);
  if(trozos.length>1 && trozos[trozos.length-1][1]-trozos[trozos.length-1][0]===1){ const u=trozos.pop(); trozos[trozos.length-1][1]=u[1]; }
  let c=trozos[0]; for(const z of trozos) if(t>=tiempos[z[0]]) c=z;
  const limpia = s => s.normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[.,;:¿?¡!«»"]/g,"").toLowerCase();
  document.getElementById("cap").innerHTML = palabras.slice(c[0],c[1]).map((p,j)=>{ const k=c[0]+j;
    const key = f.clave && limpia(p)===limpia(f.clave); return `<span class="w${t>=tiempos[k]?" on":""}${key?" key":""}">${esc(p)}</span>`; }).join(" ");
}
window.render = function(t){
  let i = 0; for(let k=0;k<D.length;k++) if(t>=D[k].ini) i=k;
  const f=D[i]; caption(f,t);
  NODOS.forEach((n,k)=> n.style.display = k===i ? "block" : "none");
  animar(ESC[i], NODOS[i], t-f.ini, f.dur);
};
"""


def pagina(cfg, datos):
    iconos, dibujos = {}, {}
    for e in cfg["escenas"]:
        if e.get("tipo") == "dibujo" and e["dibujo"] not in dibujos:
            dibujos[e["dibujo"]] = (AQUI / "dibujos" / f"{e['dibujo']}.svg").read_text()
    base = pathlib.Path(cfg.get("_ruta", ".")).parent
    for e in cfg["escenas"]:
        if e.get("tipo") == "captura":
            src = e["imagen"]
            e["src"] = src if src.startswith("http") else f"file://{(base / src).resolve()}"
    for i, e in enumerate(cfg["escenas"]):
        if e.get("tipo") == "tarjetas":
            for k, t in enumerate(e["items"]):
                iconos[f"{i}-{k}"] = icono(t.get("icono", "sparkles"), 64, "#5b5bd6")
    css = CSS.replace("url(F/", f"url(file://{AQUI / 'fuentes'}/")
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{css}</style></head><body>"
            f"<div id='cap'></div><div id='escenas'></div><script>window.DATOS={json.dumps(datos, ensure_ascii=False)};"
            f"window.ESCENAS={json.dumps(cfg['escenas'], ensure_ascii=False)};window.PALABRA={json.dumps(cfg.get('palabra', ''))};"
            f"window.ICONOS={json.dumps(iconos)};window.DIBUJOS={json.dumps(dibujos)};{JS}</script></body></html>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--pedido-voz", action="store_true")
    ap.add_argument("--sin-voz", action="store_true")
    ap.add_argument("--salida", default=str(RAIZ / "reels"))
    a = ap.parse_args()
    cfg = json.load(open(a.config)); cfg["_ruta"] = a.config
    frases = [e["voz"].strip() for e in cfg["escenas"]]
    if a.pedido_voz:
        tandas = G.pedido(frases, estilo=G.ESTILO_LIBRE)
        print("\n".join(G.sql_pedido(tandas)) if tandas else "Ya están todos los audios.")
        return
    datos, pcms, sr, t = [], [], 24000, INICIO
    for e, f in zip(cfg["escenas"], frases):
        r = None if a.sin_voz else G.descargar(f, estilo=G.ESTILO_LIBRE)
        if r:
            pcm, sr = r
            pcm = G.recortar(pcm, sr)
            dur = len(pcm) / 2 / sr
        elif a.sin_voz:
            pcm, dur = b"", max(1.4, len(f) / 15)
        else:
            sys.exit(f"Falta la voz de «{f}». Pídela con --pedido-voz (o usa --sin-voz para una vista previa).")
        pcms.append(pcm)
        datos.append({"texto": f, "ini": round(t, 3), "dur": round(dur, 3), "clave": e.get("clave")})
        t += dur + HUECO
    total = t - HUECO + FIN
    if total > 62:
        print(f"AVISO: el reel dura {total:.0f} s; acorta frases o quita escenas (máximo 60 s).")
    salida = pathlib.Path(a.salida); salida.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path("/tmp") / f"historia-{cfg['slug']}"; (tmp / "fr").mkdir(parents=True, exist_ok=True)
    for v in (tmp / "fr").glob("*.jpg"):
        v.unlink()
    muestras = bytearray(int(total * sr) * 2)
    for d, pcm in zip(datos, pcms):
        i = int(d["ini"] * sr) * 2
        muestras[i:i + len(pcm)] = pcm
    with wave.open(str(tmp / "voz.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(muestras))
    (tmp / "reel.html").write_text(pagina(cfg, datos))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(f"file://{tmp / 'reel.html'}"); pg.wait_for_timeout(500)
        n = int(total * FPS + 0.999)
        for k in range(n):
            pg.evaluate("t => window.render(t)", k / FPS)
            pg.screenshot(path=str(tmp / "fr" / f"{k:05d}.jpg"), type="jpeg", quality=88)
        d0 = datos[0]
        pg.evaluate("t => window.render(t)", d0["ini"] + d0["dur"] * 0.95)
        pg.screenshot(path=str(salida / f"{cfg['slug']}-portada.jpg"), type="jpeg", quality=92)
        b.close()
    mp4 = salida / f"{cfg['slug']}.mp4"
    audio = tmp / "voz.wav"
    musica = cfg.get("musica")
    if musica:   # música propia (musica.py) muy baja y que se aparta cuando habla la voz
        pista = AQUI / "musica" / f"{musica}.wav"
        if not pista.exists():
            subprocess.run([sys.executable, str(AQUI / "musica.py")], check=True)
        audio = tmp / "mezcla.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "voz.wav"), "-stream_loop", "-1", "-i", str(pista), "-filter_complex",
                        f"[0:a]aresample=44100,asplit=2[v][sc];[1:a]volume=0.22,atrim=0:{total:.2f},afade=t=in:d=0.6,afade=t=out:st={max(0, total - 1.2):.2f}:d=1.2[m];"
                        "[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[v][md]amix=inputs=2:duration=first:normalize=0[out]",
                        "-map", "[out]", "-ac", "1", str(audio)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "fr/%05d.jpg"), "-i", str(audio),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(mp4)], check=True)
    print(json.dumps({"reel": str(mp4), "portada": str(salida / f"{cfg['slug']}-portada.jpg"), "segundos": round(total, 1),
                      "voz": "ninguna" if a.sin_voz else "gemini"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
