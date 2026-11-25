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
  foto      {"imagen": "img/escena.jpg", "foco": "50% 30%", "globo": {...}}  foto o imagen generada (Cloudflare) en grande, con zoom lento y bocadillo
  captura   {"imagen": "capturas/reserva-movil.png", "desplazar": true}  captura real (ruta relativa a la config)
            dentro de un móvil; con desplazar, baja poco a poco como si se hiciera scroll
  cierre    {}  «Comenta PALABRA y te paso la guía». Opcional: "arriba", "palabra", "abajo" para otro cierre y "caja": true
            para enseñar debajo la caja de comentarios escribiendo la palabra (reels de servicios: «YO»)
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

# Tema «color» (17-11-2026, Jesús: «muy apagado con el fondo blanco»): fondo de marca en degradado violeta con
# luces que se mueven, subtítulos en blanco con la palabra clave en amarillo, escenas más grandes y tarjetas que resaltan.
CSS_COLOR = """
body{color:#fff;background:#3f37c9;--vaon:#fff;--vaoff:rgba(255,255,255,.38);--vbon:var(--amarillo)}
#fondo{position:absolute;inset:0;overflow:hidden;background:linear-gradient(160deg,#2e2a8f 0%,#4f46e5 45%,#7c3aed 100%)}
#fondo i{position:absolute;border-radius:50%;filter:blur(70px);opacity:.55}
#fondo i:nth-child(1){width:620px;height:620px;background:#22d3ee;left:-200px;top:180px}
#fondo i:nth-child(2){width:560px;height:560px;background:#f472b6;right:-180px;top:900px}
#fondo i:nth-child(3){width:480px;height:480px;background:#ffd43b;left:300px;top:1500px;opacity:.35}
#fondo b{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.16) 2px,transparent 2px);background-size:54px 54px}
#cap{top:250px;font-size:92px}
#cap .w{color:rgba(255,255,255,.38)}
#cap .w.on{color:#fff;text-shadow:0 6px 30px rgba(20,10,80,.35)}
#cap .w.key.on{color:var(--tinta)}
#cap .w.key.on:after{bottom:-4px;top:4px;height:auto;left:-14px;right:-14px;border-radius:14px}
.esc{transform:scale(1.15);top:580px}
.card{color:var(--tinta);box-shadow:0 40px 90px -20px rgba(10,5,60,.55)}
.gigante{color:#fff;text-shadow:0 10px 40px rgba(20,10,80,.35)}
.gigante.cnum,.gigante.vf{color:var(--amarillo)!important}
.esc > div[style*="#4a4c60"]{color:rgba(255,255,255,.9)!important}
.badge{background:var(--amarillo);color:var(--tinta)}
.marca{color:rgba(255,255,255,.8)}
.tarj .ic,.num{background:#efeffb}
"""
JS_COLOR = r"""
(function(){ const f=document.getElementById("fondo"); if(!f) return; const L=[...f.querySelectorAll("i")];
  const mover=window.__moverFondo=(t)=>{ L.forEach((x,k)=>{ const a=t/1000*(0.35+0.12*k)+k*2; x.style.transform=`translate(${Math.sin(a)*120}px,${Math.cos(a*0.8)*90}px)`; }); };
  mover(0); const r0=window.render; window.render=function(t){ r0(t); mover(t*1000); }; })();
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
  case "dibujo": h = `<div class="dib" style="position:absolute;left:-10px;right:-10px;top:0;transform-origin:50% 55%">${window.DIBUJOS[e.dibujo]||""}</div>`+
     (e.globo?`<div class="card globo" style="left:${e.globo.x||130}px;top:${e.globo.y||170}px;width:470px;padding:22px 28px;font-size:34px;line-height:1.3"><b style="display:block;font-size:24px;letter-spacing:.5px;color:${e.globo.color||"#6b6d80"}">${esc((e.globo.titulo||"").toUpperCase())}</b>${esc(e.globo.texto)}</div>`:""); break;
  case "anim": { // escena animada: imagen (IA) + capas que se mueven, según plantilla (persiana, sofa, terraza, huerto, helada)
     const P=e.plantilla, q=e.params||{}; let svg="";
     const NS='<defs><pattern id="lamas'+i+'" width="10" height="26" patternUnits="userSpaceOnUse"><rect width="10" height="26" fill="#8d97a6"/><rect y="20" width="10" height="6" fill="#5f6876"/><rect y="2" width="10" height="3" fill="#b3bcc8"/></pattern><radialGradient id="halo'+i+'"><stop offset="0" stop-color="#ffd870" stop-opacity=".85"/><stop offset="1" stop-color="#ffd870" stop-opacity="0"/></radialGradient><linearGradient id="alba'+i+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb36b" stop-opacity=".95"/><stop offset=".55" stop-color="#ffd9a0" stop-opacity=".55"/><stop offset="1" stop-color="#fff2d6" stop-opacity="0"/></linearGradient></defs>';
     const estrellas = (zona)=>{ let r=""; for(let k=0;k<(zona[4]||20);k++){ const x=zona[0]+((k*137)%100)/100*zona[2], y=zona[1]+((k*71)%100)/100*zona[3]; r+=`<circle class="est" data-f="${(k*1.7)%6}" data-v="${1+(k%3)*0.6}" cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="${1.6+(k%3)}" fill="#fff"/>`;} return r; };
     if(P==="persiana"){ const [hx,hy,hw,hh]=q.hueco, [cx,cy]=q.cartel;
       svg = `<rect class="noche" width="1024" height="1024" fill="#0b0a2e" opacity="0"/>`+
         (q.cielo?`<g class="cielo">${estrellas(q.cielo)}</g>`:"")+
         (q.modo==="sube"?`<rect class="alba" x="0" y="0" width="1024" height="${q.cielo?q.cielo[1]+q.cielo[3]+80:260}" fill="url(#alba${i})" opacity="0"/><circle class="sol" cx="${q.sol?q.sol[0]:880}" cy="${q.sol?q.sol[1]:120}" r="46" fill="#ffd34d" opacity="0"/>`:"")+
         (q.faroles||[]).map((f,k)=>`<circle class="halo" cx="${f[0]}" cy="${f[1]}" r="70" fill="url(#halo${i})"/><rect class="apaga" x="${f[0]-19}" y="${f[1]-38}" width="38" height="70" rx="8" fill="#2a2440" opacity="0"/>`).join("")+
         `<clipPath id="hueco${i}"><rect x="${hx}" y="${hy}" width="${hw}" height="${hh}"/></clipPath><g clip-path="url(#hueco${i})"><g class="persiana"><rect x="${hx}" y="0" width="${hw}" height="${hh}" fill="url(#lamas${i})"/><rect x="${hx}" y="${hh-10}" width="${hw}" height="14" fill="#3e4552"/><rect x="${hx+hw/2-20}" y="${hh-18}" width="40" height="10" rx="4" fill="#2b313b"/></g></g>`+
         `<g class="cartel"><line x1="${cx}" y1="${cy}" x2="${cx-35}" y2="${cy+50}" stroke="#2b313b" stroke-width="4"/><line x1="${cx}" y1="${cy}" x2="${cx+35}" y2="${cy+50}" stroke="#2b313b" stroke-width="4"/><circle cx="${cx}" cy="${cy}" r="7" fill="#2b313b"/><rect class="tabla" x="${cx-100}" y="${cy+48}" width="200" height="78" rx="12" fill="#fff" stroke="#e0413a" stroke-width="6"/><text class="letrero" x="${cx}" y="${cy+100}" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="34" fill="#e0413a">CERRADO</text></g>`;
     } else if(P==="sofa"){ const [tx,ty]=q.telefono, [rx,ry]=q.reloj;
       svg = (q.cielo?`<g class="cielo">${estrellas(q.cielo)}</g>`:"")+
         `<circle class="brillo" cx="${tx}" cy="${ty}" r="60" fill="#9fd0ff" opacity="0" style="mix-blend-mode:screen"/>`+
         `<g class="ondas" fill="none" stroke="#25d366" stroke-width="5" stroke-linecap="round"><path d="M${tx-62} ${ty-30} q-18 30 0 60"/><path d="M${tx+62} ${ty-30} q18 30 0 60"/><path d="M${tx-84} ${ty-46} q-26 46 0 92"/><path d="M${tx+84} ${ty-46} q26 46 0 92"/></g>`+
         `<g class="reloj"><circle cx="${rx}" cy="${ry}" r="62" fill="#fff" stroke="#2b2a3f" stroke-width="9"/>${[0,1,2,3,4,5,6,7,8,9,10,11].map(k=>`<line x1="${rx}" y1="${ry-50}" x2="${rx}" y2="${ry-42}" stroke="#2b2a3f" stroke-width="4" transform="rotate(${k*30} ${rx} ${ry})"/>`).join("")}<line class="horas" x1="${rx}" y1="${ry}" x2="${rx}" y2="${ry-30}" stroke="#2b2a3f" stroke-width="8" stroke-linecap="round"/><line class="minutos" x1="${rx}" y1="${ry}" x2="${rx}" y2="${ry-46}" stroke="#e0413a" stroke-width="5" stroke-linecap="round"/><circle cx="${rx}" cy="${ry}" r="6" fill="#2b2a3f"/><rect x="${rx-58}" y="${ry+72}" width="116" height="40" rx="10" fill="#2b2a3f"/><text class="digital" x="${rx}" y="${ry+101}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="26" fill="#fff">23:30</text></g>`;
     } else if(P==="huerto"){ // jardinera: siembra, brotes, riego, calendario, cosecha (q.tierra=[x0,x1,y])
       const [x0,x1,yt]=q.tierra, M=q.modo, n=q.plantas||7, xs=[...Array(n)].map((_,k)=>x0+30+(x1-x0-60)*k/(n-1));
       const roseta=(x,k,cls,esc)=>`<g class="${cls}" data-k="${k}" transform="translate(${x} ${yt})"><g class="r" style="transform:scale(${esc});transform-origin:0 0">${[0,1,2,3,4,5,6,7].map(j=>`<g transform="rotate(${j*45-180+ (j%2?12:-12)})"><ellipse cx="0" cy="-26" rx="11" ry="27" fill="${j%2?"#3f8f3a":"#4fa846"}" stroke="#24521f" stroke-width="3"/><line x1="0" y1="-6" x2="0" y2="-44" stroke="#a6d98c" stroke-width="2.5"/></g>`).join("")}</g></g>`;
       if(M==="siembra"){ svg = `<g class="mano"><path d="M0 0 q40 -30 80 0 l10 40 q-50 30 -100 0z" fill="#f2c39b" stroke="#7a4a2a" stroke-width="5"/><path d="M10 34 q40 18 74 0" stroke="#7a4a2a" stroke-width="4" fill="none"/></g>`+
           [...Array(18)].map((_,k)=>`<circle class="semilla" data-k="${k}" cx="0" cy="0" r="5" fill="#6b4a2b"/>`).join("")+
           [...Array(26)].map((_,k)=>`<circle class="tierrita" data-k="${k}" cx="${x0+((k*97)%100)/100*(x1-x0)}" cy="${yt-4}" r="${3+k%3}" fill="#4a3020" opacity="0"/>`).join(""); }
       else if(M==="brotes"){ svg = xs.map((x,k)=>roseta(x,k,"brote",0)).join("")+`<g class="dias"><rect x="${x0+40}" y="${yt-330}" width="230" height="90" rx="18" fill="#fff" stroke="#24521f" stroke-width="6"/><text class="ndia" x="${x0+155}" y="${yt-270}" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="44" fill="#24521f">Día 1</text></g>`; }
       else if(M==="riego"){ svg = xs.map((x,k)=>roseta(x,k,"planta",0.85)).join("")+`<ellipse class="charco" cx="${(x0+x1)/2}" cy="${yt+4}" rx="10" ry="6" fill="#6fb6e8" opacity="0"/>`+
           `<g class="regadera"><path d="M0 0 h120 v90 q0 20 -20 20 h-80 q-20 0 -20 -20z" fill="#3aa0d8" stroke="#1d5f86" stroke-width="6"/><path d="M120 20 l90 -40 l10 16 l-90 46" fill="#3aa0d8" stroke="#1d5f86" stroke-width="6"/><path d="M0 20 q-50 10 -40 60" stroke="#1d5f86" stroke-width="10" fill="none"/></g>`+
           [...Array(16)].map((_,k)=>`<ellipse class="gota" data-k="${k}" cx="0" cy="0" rx="5" ry="9" fill="#6fb6e8" opacity="0"/>`).join(""); }
       else if(M==="calendario"){ svg = xs.map((x,k)=>roseta(x,k,"tanda",0)).join("")+`<g class="cal"><rect x="${x0+20}" y="${yt-380}" width="240" height="200" rx="16" fill="#fff" stroke="#2b2a3f" stroke-width="6"/><rect x="${x0+20}" y="${yt-380}" width="240" height="56" rx="16" fill="#e0413a"/><text x="${x0+140}" y="${yt-340}" text-anchor="middle" font-family="Arial" font-weight="900" font-size="28" fill="#fff">SIEMBRA</text><text class="semana" x="${x0+140}" y="${yt-230}" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="42" fill="#2b2a3f">Semana 1</text></g>`; }
       else if(M==="cosecha"){ svg = xs.map((x,k)=>roseta(x,k,"planta",1.25)).join("")+`<g class="bol"><path d="M${x1-30} ${yt-300} h200 q0 110 -100 110 q-100 0 -100 -110z" fill="#fff" stroke="#2b2a3f" stroke-width="6"/></g>`+
           [...Array(5)].map((_,k)=>`<g class="hoja" data-k="${k}"><ellipse cx="0" cy="0" rx="13" ry="30" fill="#4fa846" stroke="#24521f" stroke-width="3"/></g>`).join("")+
           `<g class="tijeras"><circle cx="-18" cy="40" r="16" fill="none" stroke="#e0413a" stroke-width="8"/><circle cx="18" cy="40" r="16" fill="none" stroke="#e0413a" stroke-width="8"/><g class="hojaA"><path d="M-6 26 L6 -60 L14 -58 L4 28z" fill="#c9ced6" stroke="#5b6270" stroke-width="3"/></g><g class="hojaB"><path d="M6 26 L-6 -60 L-14 -58 L-4 28z" fill="#c9ced6" stroke="#5b6270" stroke-width="3"/></g></g>`; }
  } else if(P==="helada"){ // MiHuerto, heladas (25-11-2026): termometro, pared, agrupar, tapar, raiz (q.tierra=[x0,x1,y])
       const [x0,x1,yt]=q.tierra, M=q.modo, n=q.plantas||5, xs=[...Array(n)].map((_,k)=>x0+40+(x1-x0-80)*k/(n-1));
       const mata=(x,y,k,cls,esc)=>`<g class="${cls}" data-k="${k}" transform="translate(${x} ${y})"><g class="r" style="transform:scale(${esc});transform-origin:0 0">${[0,1,2,3,4,5,6,7].map(j=>`<g transform="rotate(${j*45-180+(j%2?12:-12)})"><ellipse cx="0" cy="-26" rx="11" ry="27" fill="${j%2?"#3f8f3a":"#4fa846"}" stroke="#24521f" stroke-width="3"/></g>`).join("")}</g></g>`;
       const maceta=(k,x,y)=>`<g class="maceta" data-k="${k}" transform="translate(${x} ${y})"><path d="M-62 0 h124 l-14 118 h-96z" fill="#c8693c" stroke="#6e3216" stroke-width="6"/><rect x="-70" y="-12" width="140" height="24" rx="6" fill="#d97b4a" stroke="#6e3216" stroke-width="6"/>${mata(0,-10,0,"m",1.05)}</g>`;
       const noche=`<rect class="noche" x="0" y="0" width="1024" height="1024" fill="#0b1a3a" opacity="0"/><g class="luna" opacity="0"><circle cx="860" cy="150" r="54" fill="#f4f1dc"/><circle cx="884" cy="134" r="50" fill="#0b1a3a" opacity=".0"/></g>`;
       if(M==="termometro"){ svg = noche + xs.map((x,k)=>mata(x,yt,k,"planta",1)).join("") +
           [...Array(26)].map((_,k)=>`<g class="cristal" data-k="${k}" opacity="0" transform="translate(${xs[k%n]+((k*53)%60-30)} ${yt-30-((k*37)%50)})"><path d="M0 -9 V9 M-8 -5 L8 5 M-8 5 L8 -5" stroke="#eaf6ff" stroke-width="3.5" stroke-linecap="round"/></g>`).join("") +
           `<g transform="translate(120 170)"><rect x="-34" y="-20" width="68" height="430" rx="34" fill="#fff" stroke="#2b2a3f" stroke-width="7"/><circle cx="0" cy="430" r="58" fill="#e0413a" stroke="#2b2a3f" stroke-width="7"/><rect class="merc" x="-14" y="40" width="28" height="380" rx="14" fill="#e0413a"/>${[0,1,2,3,4].map(j=>`<line x1="20" y1="${60+j*80}" x2="34" y2="${60+j*80}" stroke="#2b2a3f" stroke-width="5"/>`).join("")}<rect x="60" y="150" width="210" height="110" rx="22" fill="#fff" stroke="#2b2a3f" stroke-width="7"/><text class="grados" x="165" y="228" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="64" fill="#2b2a3f">12 °C</text></g>`; }
       else if(M==="pared"||M==="agrupar"){ const muro=`<rect x="0" y="120" width="190" height="904" fill="#b5654a"/>${[...Array(16)].map((_,k)=>`<rect x="${(k%2)*-45+((k*0)%1)}" y="${140+k*54}" width="${k%2?235:190}" height="6" fill="#7d3c28" opacity=".7"/>`).join("")}`+
           [0,1,2].map(k=>`<path class="calor" data-k="${k}" d="M205 ${420+k*120} q30 -25 60 0 t60 0" stroke="#ff9a3c" stroke-width="10" fill="none" stroke-linecap="round" opacity="0"/>`).join("");
         svg = noche + muro + [0,1,2].map(k=>maceta(k, 560+k*170, 760)).join(""); }
       else if(M==="tapar"){ svg = noche + xs.map((x,k)=>mata(x,yt,k,"planta",1)).join("") +
           `<g class="velo"><path d="M${x0-40} ${yt+20} Q${(x0+x1)/2} ${yt-330} ${x1+40} ${yt+20}z" fill="#ffffff" fill-opacity=".72" stroke="#dfe6ee" stroke-width="6"/><path d="M${x0+30} ${yt-40} Q${(x0+x1)/2} ${yt-250} ${x1-30} ${yt-40}" fill="none" stroke="#e8eef5" stroke-width="5" stroke-dasharray="14 12"/></g>`+
           `<g class="sol" opacity="0"><circle cx="860" cy="160" r="70" fill="#ffd43b"/>${[...Array(10)].map((_,j)=>`<line x1="860" y1="60" x2="860" y2="30" stroke="#ffd43b" stroke-width="10" stroke-linecap="round" transform="rotate(${j*36} 860 160)"/>`).join("")}</g>`; }
       else if(M==="raiz"){ const cx=512, top=330;
         svg = `<rect x="0" y="0" width="1024" height="1024" fill="#eef3f6" opacity=".88"/><g transform="translate(${cx} ${top})"><path d="M-230 0 h460 l-60 470 h-340z" fill="#c8693c" stroke="#6e3216" stroke-width="8"/><path d="M-212 30 h424 l-52 410 h-320z" fill="#6b4a2b"/>`+
           [...Array(9)].map((_,k)=>`<path class="raiz" d="M${-120+k*30} 40 q${(k%2?30:-30)} 120 ${(k%3-1)*40} 220 t${(k%2?-20:20)} 140" stroke="#e8d3a8" stroke-width="${6-k%3}" fill="none" stroke-linecap="round"/>`).join("")+
           `${mata(0,10,0,"m",1.1)}<g class="burbujas" style="transform-origin:0 235px">${[...Array(48)].map((_,k)=>`<circle cx="${-250+(k%8)*72+((Math.floor(k/8))%2)*36}" cy="${30+Math.floor(k/8)*78}" r="26" fill="#dff1ff" fill-opacity=".55" stroke="#9cc9e8" stroke-width="3"/>`).join("")}</g></g>`+
           [0,1,2,3].map(k=>`<g class="frio" data-k="${k}"><path d="M0 0 h90 m-30 -26 l30 26 l-30 26" stroke="#4aa3e0" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>`).join("")+
           `<text class="frase-raiz" x="${cx}" y="${top-150}" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="54" fill="#4aa3e0">LA RAÍZ PASA FRÍO</text>`; }
  } else if(P==="terraza"){ const [cx,cy]=q.cartel;
       svg = (q.vapor||[]).map(v=>[0,1,2].map(k=>`<circle class="vapor" data-k="${k}" cx="${v[0]}" cy="${v[1]}" r="12" fill="#fff" opacity="0"/>`).join("")).join("")+
         `<g class="neon"><rect x="${cx-120}" y="${cy-42}" width="240" height="84" rx="16" fill="#1b1530" stroke="#2bd46b" stroke-width="5"/><text x="${cx}" y="${cy+16}" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="44" fill="#57ff95" style="filter:drop-shadow(0 0 8px #2bd46b)">ABIERTO</text></g>`;
     }
     h = `<div class="dib card" style="position:absolute;left:40px;right:40px;top:0;height:920px;overflow:hidden;padding:0"><div class="capa" style="position:absolute;inset:0;transform-origin:50% 55%"><img class="fondo" src="${e.src}" style="width:100%;height:100%;object-fit:cover;display:block">${e.figsrc?`<img class="fig" src="${e.figsrc}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 90%">`:""}<svg viewBox="0 0 1024 1024" preserveAspectRatio="xMidYMid slice" style="position:absolute;inset:0;width:100%;height:100%">${NS}${svg}</svg></div></div>`+
       (e.globo?`<div class="card globo" style="left:${e.globo.x||130}px;top:${e.globo.y||170}px;width:470px;padding:22px 28px;font-size:34px;line-height:1.3"><b style="display:block;font-size:24px;letter-spacing:.5px;color:${e.globo.color||"#6b6d80"}">${esc((e.globo.titulo||"").toUpperCase())}</b><span class="gtxt">${esc(e.globo.texto)}</span>${e.globo.escribiendo?`<span class="gpuntos" style="font-size:44px;letter-spacing:4px;color:#9aa0b0">•••</span>`:""}</div>`:"");
     break; }
  case "foto": h = `<div class="dib card" style="position:absolute;left:40px;right:40px;top:0;height:920px;overflow:hidden;padding:0;transform-origin:50% 50%"><img class="fondo" src="${e.src}" style="width:100%;height:100%;object-fit:cover;display:block;object-position:${e.foco||"50% 50%"};transform-origin:50% 50%">${e.figsrc?`<img class="fig" src="${e.figsrc}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:${e.foco||"50% 50%"};transform-origin:50% 90%">`:""}</div>`+
     (e.globo?`<div class="card globo" style="left:${e.globo.x||130}px;top:${e.globo.y||170}px;width:470px;padding:22px 28px;font-size:34px;line-height:1.3"><b style="display:block;font-size:24px;letter-spacing:.5px;color:${e.globo.color||"#6b6d80"}">${esc((e.globo.titulo||"").toUpperCase())}</b>${esc(e.globo.texto)}</div>`:""); break;
  case "captura": h = `<div class="movil card" style="top:0"><div class="pant" style="background:#fff"><img src="${e.src}" style="width:100%;display:block;position:absolute;top:0;left:0"></div></div>`; break;
  case "video": h = ""; break;
  case "pizarra": h = `<div class="pz" style="position:absolute;left:90px;right:90px;top:0;height:900px"><svg viewBox="0 0 900 900" width="900" height="900" style="overflow:visible">${e.trazos}</svg>`+
      `<svg class="boli" viewBox="0 0 60 160" width="54" height="144" style="position:absolute;left:0;top:0;transform-origin:4px 156px;opacity:0"><g transform="rotate(28 30 80)"><rect x="16" y="0" width="28" height="112" rx="8" fill="#2d2f3a"/><rect x="16" y="20" width="28" height="18" fill="#ffd43b"/><path d="M18 112 h24 l-8 30 h-8z" fill="#e9e3d6"/><path d="M26 142 h8 l-4 14z" fill="#1d1d1f"/></g></svg></div>`; break;
  case "cierre": h = `<div class="card centro" style="left:120px;right:120px;top:140px;padding:70px 50px;text-align:center"><div style="font-size:54px;font-weight:600">${esc(e.arriba||"Comenta")}</div><div class="pill" style="font-size:${(e.palabra||PALABRA).length>8?84:116}px">${esc(e.palabra||PALABRA)}</div><div style="font-size:42px;line-height:1.3;color:#4a4c60">${e.abajo?negrita(e.abajo):"y te paso la guía<br>por mensaje privado 📩"}</div></div>${e.caja?`<div class="card ccaja" style="left:90px;right:90px;top:720px;padding:26px 30px;display:flex;align-items:center;gap:22px;opacity:0"><div class="av" style="background:#c3c5d0;flex:none">Tú</div><div class="ctx" style="flex:1;font-size:40px;font-weight:600;color:#9a9cab">Añade un comentario…</div><div class="cpub" style="font-size:34px;font-weight:800;color:#b9c8ff">Publicar</div></div>`:""}<div class="marca">${esc(window.MARCA||"iando.xyz")}</div>`; break;
  }
  if(e.sello) h += `<div class="sello ${e.tono==="verde"?"verde":""}">${esc(e.sello)}</div>`;
  d.innerHTML = h; raiz.appendChild(d); return d;
}
const NODOS = ESC.map(construir);
const Q = (d,s) => Array.from(d.querySelectorAll(s));

function animar(e,d,lt,dur){
  switch(e.tipo){
  case "video": break;
  case "pizarra": { const f = lt/dur, R=d, svg=R.querySelector("svg"), boli=R.querySelector(".boli"); let punta=null;
      const fr=(el)=>{ const t0=+el.dataset.t||0, dd=+el.dataset.d||0.2; return Math.max(0,Math.min(1,(f-t0)/dd)); };
      R.querySelectorAll(".tz").forEach(el=>{ const pr=fr(el); el.style.strokeDasharray="1 1"; el.style.strokeDashoffset=String(1-pr);
        if(pr>0 && pr<1 && el.getTotalLength){ const L=el.getTotalLength(), pt=el.getPointAtLength(L*pr), m=el.getCTM(); if(m) punta={x:pt.x*m.a+pt.y*m.c+m.e, y:pt.x*m.b+pt.y*m.d+m.f}; } });
      R.querySelectorAll(".ap").forEach(el=>{ const pr=ease(fr(el)); el.style.opacity=pr; const bx=el.getBBox?el.getBBox():null; if(bx){ el.style.transformOrigin=`${bx.x+bx.width/2}px ${bx.y+bx.height/2}px`; el.style.transform=`scale(${0.6+0.4*pr})`; } });
      R.querySelectorAll(".sale").forEach(el=>{ el.style.opacity=1-ease(fr(el)); });
      R.querySelectorAll(".vuela").forEach((el,k)=>{ const x=+el.dataset.x, y=+el.dataset.y, px=el.dataset.px, py=el.dataset.py;
        let ox=Math.sin(lt*(2.1+k*0.37)+k)*38, oy=Math.cos(lt*(2.7+k*0.29)+k*1.7)*26, X=x, Y=y;
        if(px!==undefined){ const pg=ease(fr(el)); X=x+(+px-x)*pg; Y=y+(+py-y)*pg; ox*=1-pg; oy*=1-pg; }
        el.setAttribute("transform",`translate(${X+ox} ${Y+oy})`); el.style.opacity = el.dataset.fuera ? 1-ease(Math.max(0,Math.min(1,(f-(+el.dataset.fuera))/0.25))) : 1; });
      R.querySelectorAll(".ondula").forEach((el,k)=>{ el.setAttribute("transform", `${el.dataset.base||""} rotate(${Math.sin(lt*6+k)*12})`); });
      if(punta){ boli.style.opacity=1; boli.style.left=(punta.x-4)+"px"; boli.style.top=(punta.y-156)+"px"; } else { boli.style.opacity=0; }
      break; }
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
  case "versus": { const a=pop(lt,dur*0.5,.3); d.querySelector(".va").style.color = a>.5?"var(--vaoff,var(--gris))":"var(--vaon,var(--tinta))";
    d.querySelector(".vb").style.color = a>.5?"var(--vbon,var(--indigo))":"var(--gris)"; d.querySelector(".vb").style.transform=`scale(${1+0.12*a})`; d.querySelector(".vf").style.opacity=a; break; }
  case "prompt": { const t=e.texto, n=Math.round(t.length*Math.min(1,lt/(dur*0.85))); let s=t.slice(0,n);
    const abiertos=(s.match(/\[/g)||[]).length-(s.match(/\]/g)||[]).length; if(abiertos>0) s+="]";
    d.querySelector(".ptxt").innerHTML = huecos(s)+(n<t.length?"▍":""); break; }
  case "tarjetas": case "pasos": { const sel = e.tipo==="tarjetas"?".tarj":".paso", n = (e.items||e.pasos).length;
    Q(d,sel).forEach(c=>{ const k=+c.dataset.k, a=pop(lt,k*dur*0.75/n,.3); c.style.opacity=a; c.style.transform=`translateX(${(1-a)*120}px)`;
      if(e.tipo==="pasos"){ const on = lt >= k*dur*0.75/n; c.querySelector(".num").style.background = on?"var(--indigo)":"#efeffb"; c.querySelector(".num").style.color = on?"#fff":"var(--indigo)"; } }); break; }
  case "anim": { const P=e.plantilla, q=e.params||{}, p=ease(Math.min(1,lt/Math.max(dur,0.1))), $$=(c)=>d.querySelectorAll(c), $1=(c)=>d.querySelector(c);
    const cl=x=>Math.max(0,Math.min(1,x));
    $1(".capa").style.transform=`scale(${1.02+0.05*p}) translateX(${(e.paneo||0)*p}%)`;
    const fg=$1(".fig"); if(fg) fg.style.transform=`scale(${1.03+0.06*p}) translateY(${Math.sin(lt*2.4)*4}px)`;
    $$(".est").forEach(c=>c.setAttribute("opacity", 0.3+0.7*Math.abs(Math.sin(lt*(+c.dataset.v)+(+c.dataset.f)))));
    $1(".dib").style.opacity=pop(lt,0,.25);
    if(P==="persiana"){ const [hx,hy,hw,hh]=q.hueco, [cx,cy]=q.cartel, sube=q.modo==="sube";
      const T0=sube?0.35:0.35, TD=Math.min(2.4, dur*0.5);
      let k=cl((lt-T0)/TD); const reb=k<.82?ease(k/.82):1-Math.sin((k-.82)/.18*Math.PI)*0.025;
      const bajada = sube ? 1-ease(k) : reb;   // 1 = cerrada
      const vib=(k>0&&k<1)?Math.sin(lt*60)*1.2:0;
      $1(".persiana").setAttribute("transform",`translate(${vib} ${hy+hh*bajada-hh})`);
      const tOff = sube ? -1 : T0+TD+0.15;
      const off = sube ? 1 : cl((lt-tOff)/0.5), parpa=(!sube && lt>tOff && lt<tOff+0.5)?(Math.sin(lt*90)>0?1:0.3):1;
      $$(".halo").forEach(x=>x.style.opacity=(1-off)*parpa); $$(".apaga").forEach(x=>x.setAttribute("opacity",off*0.75));
      const noche=$1(".noche"); noche.setAttribute("opacity", sube ? 0.28*(1-cl(lt/(TD+0.6))) : 0.28*off);
      if(sube){ const a=cl(lt/(TD+0.8)); $1(".alba").setAttribute("opacity",a*0.9); const sol=$1(".sol"); sol.setAttribute("opacity",a); sol.setAttribute("transform",`translate(0 ${60*(1-a)})`); $$(".est").forEach(c=>c.setAttribute("opacity",(1-a)*0.8)); }
      const ca=$1(".cartel"); ca.style.transformOrigin=`${cx}px ${cy}px`; ca.style.transformBox="view-box";
      if(!sube){ const tc=T0+TD*0.9, a=cl((lt-tc)/0.35); const ang=a<1?-60*(1-a):Math.sin((lt-tc-0.35)*6)*14*Math.exp(-(lt-tc-0.35)*0.9); ca.style.opacity=a; ca.style.transform=`rotate(${ang}deg)`; }
      else { // el cartel sube con la persiana y da la vuelta: ABIERTO
        const tg=T0+TD+0.1, g=cl((lt-tg)/0.5); ca.style.opacity=1; ca.style.transform=`translate(0px, ${-(1-bajada)*0}px) scaleX(${Math.abs(Math.cos(g*Math.PI))||0.02})`;
        const L=$1(".letrero"), Tb=$1(".tabla"); if(g>0.5){ L.textContent="ABIERTO"; L.setAttribute("fill","#1f9d55"); Tb.setAttribute("stroke","#1f9d55"); } }
    } else if(P==="sofa"){ const [rx,ry]=q.reloj;
      const ini=(q.desde||[23,30]), fin=(q.hasta||[23,37]); const mins=ini[1]+(fin[1]-ini[1])*cl(lt/(dur*0.9));
      $1(".minutos").setAttribute("transform",`rotate(${mins*6} ${rx} ${ry})`); $1(".horas").setAttribute("transform",`rotate(${(ini[0]%12)*30+mins*0.5} ${rx} ${ry})`);
      $1(".digital").textContent=`${ini[0]}:${String(Math.floor(mins)).padStart(2,"0")}`;
      $1(".brillo").setAttribute("opacity", 0.25+0.35*Math.abs(Math.sin(lt*3)));
      const env=cl((lt-0.9)/0.3)*(1-cl((lt-2.2)/0.3)); $1(".ondas").style.opacity=env*(0.4+0.6*Math.abs(Math.sin(lt*7)));
      const gp=$1(".gpuntos"), gt=$1(".gtxt"); if(gp){ const esc_=lt<1.5; gp.style.display=esc_?"inline":"none"; gt.style.display=esc_?"none":"inline"; gp.style.opacity=0.5+0.5*Math.abs(Math.sin(lt*6)); }
    } else if(P==="huerto"){ const [x0,x1,yt]=q.tierra, M=q.modo, n=q.plantas||7;
      const roset=(cls,f)=>$$(cls).forEach(g=>{const k=+g.dataset.k; g.querySelector(".r").style.transform=`scale(${f(k)})`;});
      if(M==="siembra"){ const mx=x0+(x1-x0)*cl(lt/(dur*0.75)); $1(".mano").setAttribute("transform",`translate(${mx-40} ${yt-260+Math.sin(lt*8)*6})`);
        $$(".semilla").forEach(c=>{const k=+c.dataset.k, t0=k*(dur*0.7)/18, u=cl((lt-t0)/0.6); const sx=x0+(x1-x0)*cl(t0/(dur*0.75)); c.setAttribute("cx",sx+((k*37)%20-10)); c.setAttribute("cy",yt-215+(225)*u*u); c.setAttribute("opacity",lt<t0?0:1);});
        $$(".tierrita").forEach(c=>{const k=+c.dataset.k; c.setAttribute("opacity",cl((lt-dur*0.6-k*0.02)/0.3));}); }
      else if(M==="brotes"){ roset(".brote",k=>0.15+0.75*ease(cl((lt-0.3-k*0.12)/(dur*0.55)))); $1(".ndia").textContent="Día "+(1+Math.floor(9*cl(lt/(dur*0.8)))); }
      else if(M==="riego"){ // regadera a la derecha, volteada: el pitorro apunta a la jardinera y baja al regar (corregido 25-11-2026, Jesús: «riega del revés»)
        const rx=x1+60, ry=yt-330, th=35*ease(cl(lt/0.6)), rad=th*Math.PI/180;
        $1(".regadera").setAttribute("transform",`translate(${rx} ${ry}) scale(-1 1) rotate(${th} 110 60)`);
        const px=105, py=-92, bx=rx-(110+px*Math.cos(rad)-py*Math.sin(rad)), by=ry+(60+px*Math.sin(rad)+py*Math.cos(rad));
        $$(".gota").forEach(g=>{const k=+g.dataset.k, c=((lt*1.6+k/16)%1); g.setAttribute("cx",bx-c*40+((k*13)%30)-15); g.setAttribute("cy",by+c*(yt-by)); g.setAttribute("opacity",lt<0.5?0:0.9);});
        const w=cl((lt-0.6)/(dur*0.7)); const ch=$1(".charco"); ch.setAttribute("rx",10+240*w); ch.setAttribute("ry",6+10*w); ch.setAttribute("opacity",0.85*cl(w*3));
        roset(".planta",k=>0.85-0.25*w); $$(".planta .r").forEach(r=>r.style.filter=`saturate(${1-0.6*w}) brightness(${1-0.15*w})`); }
      else if(M==="calendario"){ const sem=[1,3,5,7], st=Math.min(3,Math.floor(cl(lt/(dur*0.85))*4)); $1(".semana").textContent="Semana "+sem[st];
        $1(".cal").style.transform=`rotate(${Math.sin(lt*3)*2}deg)`; $1(".cal").style.transformOrigin=`${x0+140}px ${yt-380}px`;
        roset(".tanda",k=>{ const grupo=Math.floor(k*4/n), edad=st-grupo+cl((lt%(dur*0.85/4))/(dur*0.85/4)); return grupo>st?0:Math.min(1.1,0.25+0.28*edad); }); }
      else if(M==="cosecha"){ const xs=[...Array(n)].map((_,k)=>x0+30+(x1-x0-60)*k/(n-1)); const per=dur*0.8/5;
        const i0=Math.min(4,Math.floor(lt/per)), ph=(lt%per)/per, tx=xs[1+i0], tyy=yt-40;
        $1(".tijeras").setAttribute("transform",`translate(${tx} ${tyy-80+20*Math.sin(ph*Math.PI)}) rotate(-20)`);
        const ab=ph<0.5?Math.sin(ph*2*Math.PI)*18:0; $1(".hojaA").setAttribute("transform",`rotate(${ab} 0 26)`); $1(".hojaB").setAttribute("transform",`rotate(${-ab} 0 26)`);
        $$(".planta").forEach(g=>{const k=+g.dataset.k; g.style.opacity=(k>=1&&k<=5&&k-1<i0)||(k-1===i0&&ph>0.55)?0:1;});
        $$(".hoja").forEach(h=>{const k=+h.dataset.k; let u=k<i0?1:k===i0?cl((ph-0.55)/0.4):-1; if(u<0){h.style.opacity=0;return;} const sx=xs[1+k], ex=x1+70+(k%3-1)*30, ey=yt-215;
          h.style.opacity=1; h.setAttribute("transform",`translate(${sx+(ex-sx)*u} ${yt-40+(ey-yt+40)*u-Math.sin(u*Math.PI)*120}) rotate(${u*200+k*20})`);}); }
    } else if(P==="helada"){ const M=q.modo, [x0,x1,yt]=q.tierra;
      const nocheA=(a)=>{ const f=$1(".fondo"); if(f) f.style.filter=`brightness(${1-0.5*a}) saturate(${1-0.35*a}) hue-rotate(${-12*a}deg)`; const lu=$1(".luna"); if(lu) lu.setAttribute("opacity",a); };
      if(M==="termometro"){ const a=cl(lt/(dur*0.8)), temp=Math.round(12-14*ease(a)); $1(".merc").setAttribute("y",40+330*ease(a)); $1(".merc").setAttribute("height",380-330*ease(a));
        $1(".grados").textContent=temp+" °C"; $1(".grados").setAttribute("fill", temp<=0?"#1d6fb8":"#2b2a3f"); nocheA(ease(a));
        $$(".cristal").forEach(c=>{const k=+c.dataset.k; c.setAttribute("opacity", cl((a-0.55-k*0.012)/0.2));});
        $$(".planta .r").forEach(r=>r.style.filter=`saturate(${1-0.5*cl((a-0.5)/0.5)}) brightness(${1+0.25*cl((a-0.6)/0.4)})`); }
      else if(M==="pared"||M==="agrupar"){ nocheA(0.85); const a=ease(cl(lt/(dur*0.6)));
        $$(".maceta").forEach(g=>{const k=+g.dataset.k; const ini=560+k*170, fin=M==="pared"? 290+k*170 : 290+k*112;
          const x0_=M==="agrupar"? 290+k*170 : ini; const x=x0_+(fin-x0_)*a; g.setAttribute("transform",`translate(${x} ${760-Math.abs(Math.sin(a*Math.PI*3))*10*(1-a)})`);});
        $$(".calor").forEach(c=>{const k=+c.dataset.k; c.setAttribute("opacity", (M==="pared"? cl((lt-dur*0.4)/0.4):1)*(0.45+0.45*Math.sin(lt*5+k)));
          c.setAttribute("transform",`translate(${Math.sin(lt*3+k)*6} 0)`);}); }
      else if(M==="tapar"){ const baja=ease(cl(lt/(dur*0.35))), sube=ease(cl((lt-dur*0.62)/(dur*0.3)));
        $1(".velo").setAttribute("transform",`translate(0 ${-720*(1-baja)-720*sube})`); nocheA(1-sube); $1(".sol").setAttribute("opacity",sube);
        $1(".sol").setAttribute("transform",`translate(0 ${60*(1-sube)})`); }
      else if(M==="raiz"){ const env=ease(cl((lt-dur*0.45)/(dur*0.35)));
        $$(".frio").forEach(f=>{const k=+f.dataset.k, lado=k<2?-1:1, y=430+(k%2)*170, base=lado<0? 120 : 904, c=((lt*0.9+k*0.25)%1);
          const dx= lado<0? 140*c : -140*c - 90; f.setAttribute("transform",`translate(${base+dx} ${y}) ${lado<0?"":"scale(-1 1) translate(-90 0)"}`); f.setAttribute("opacity",(1-env)*(1-c)*0.95);});
        $1(".burbujas").style.transform=`scaleY(${env})`; $1(".burbujas").style.opacity=env;
        $$(".raiz").forEach(r=>r.setAttribute("stroke", env>0.5?"#e8d3a8":(Math.sin(lt*6)>0?"#9fc8ea":"#e8d3a8")));
        const fr=$1(".frase-raiz"); fr.textContent= env>0.6 ? "RAÍZ ABRIGADA" : "LA RAÍZ PASA FRÍO"; fr.setAttribute("fill", env>0.6?"#1f9d55":"#4aa3e0"); }
    } else if(P==="terraza"){
      const n=$1(".neon"); n.style.opacity = lt<0.6 ? (Math.sin(lt*70)>0?1:0.15) : (0.85+0.15*Math.sin(lt*9));
      $$(".vapor").forEach(v=>{ const k=+v.dataset.k, c=((lt*0.7+k/3)%1); v.setAttribute("transform",`translate(${Math.sin(c*6+k)*8} ${-c*90})`); v.setAttribute("opacity",(1-c)*0.55); v.setAttribute("r",10+c*18); });
    }
    const g=$1(".globo"); if(g){ const a=pop(lt,e.globo.retraso??0.35,.35); g.style.opacity=a; g.style.transform=`translateY(${(1-a)*30}px) scale(${0.9+0.1*a})`; }
    break; }
  case "foto": { // 2,5D: el fondo se acerca despacio y el personaje (recortado) un poco más y respira -> profundidad
    const p=ease(Math.min(1,lt/Math.max(dur,0.1))), f=d.querySelector(".fondo"), fg=d.querySelector(".fig"), c=d.querySelector(".dib");
    const dx=(e.paneo||0)*p; if(f) f.style.transform=`scale(${1.02+0.06*p}) translateX(${dx}%)`;
    if(fg) fg.style.transform=`scale(${1.04+0.11*p}) translateX(${dx*1.6}%) translateY(${Math.sin(lt*2.4)*5}px) rotate(${Math.sin(lt*1.7)*0.6}deg)`;
    const a0=pop(lt,0,.3); if(c){ c.style.opacity=a0; }
    const g=d.querySelector(".globo"); if(g){ const a=pop(lt,0.3,.35); g.style.opacity=a; g.style.transform=`translateY(${(1-a)*30}px) scale(${0.9+0.1*a})`; }
    break; }
  case "dibujo": { const tel=d.querySelector("#telefono"), on=d.querySelector("#ondas"), br=d.querySelector("#brazo");
    const dib=d.querySelector(".dib"); if(dib){ const z=1+0.05*ease(Math.min(1,lt/Math.max(dur,0.1))); dib.style.transform=`scale(${z})`; }
    d.querySelectorAll(".sudor").forEach((g,k)=>{ const c=((lt*1.3+k*0.4)%1); g.style.transform=`translateY(${c*40}px)`; g.style.opacity=1-c; });
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
  case "cierre": { const a=pop(lt,0,.4), c=d.querySelector(".card"); c.style.opacity=a; c.style.transform=`scale(${0.85+0.15*a})`;
    const cj=d.querySelector(".ccaja"); if(cj){ const b=pop(lt,0.5,.35); cj.style.opacity=b; cj.style.transform=`translateY(${(1-b)*40}px)`;
      const pal=e.palabra||PALABRA, n=Math.max(0,Math.min(pal.length,Math.floor((lt-0.9)/0.22)+1)), tx=cj.querySelector(".ctx"), pb=cj.querySelector(".cpub");
      if(lt<0.9){ tx.textContent="Añade un comentario…"; tx.style.color="#9a9cab"; } else { tx.textContent=pal.slice(0,n)+(n<pal.length||Math.floor(lt*3)%2?"|":""); tx.style.color="#17162b"; }
      pb.style.color = n>=pal.length && lt>0.9 ? "#0095f6" : "#b9c8ff"; } break; }
  // "caja": true en el cierre → caja de comentarios de Instagram escribiendo la palabra (regla de iando para los reels de servicios, 25-11-2026)
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
        if e.get("tipo") in ("captura", "foto", "anim"):
            src = e["imagen"]
            e["src"] = src if src.startswith("http") else f"file://{(base / src).resolve()}"
            if e.get("figura"):
                fg = e["figura"]
                e["figsrc"] = fg if fg.startswith("http") else f"file://{(base / fg).resolve()}"
    for i, e in enumerate(cfg["escenas"]):
        if e.get("tipo") == "tarjetas":
            for k, t in enumerate(e["items"]):
                iconos[f"{i}-{k}"] = icono(t.get("icono", "sparkles"), 64, "#5b5bd6")
    color = cfg.get("tema") in ("color", "verde")
    extra = CSS_COLOR if color else ""
    if cfg.get("fondo_video"):   # prueba MiHuerto 25-11-2026: vídeo libre (Pexels) detrás, la página es transparente
        extra += ("body{background:transparent!important}#fondo{display:none!important}"
                  "#cap{background:rgba(10,20,10,.42);padding:26px 30px;border-radius:34px;left:50px;right:50px}"
                  "#cap .w{color:rgba(255,255,255,.55)!important}#cap .w.on{color:#fff!important;text-shadow:0 4px 18px rgba(0,0,0,.6)}"
                  "#cap .w.key.on{color:#17162b!important;text-shadow:none}.marca{color:#fff!important;text-shadow:0 3px 12px rgba(0,0,0,.7)}")
    if cfg.get("tema") == "pizarra":   # estilo pizarra dibujada a mano (prueba MiHuerto 25-11-2026)
        extra += ("body{background:#fbfaf5}#escenas:before{content:'';position:absolute;inset:0;background-image:linear-gradient(#ecebe4 2px,transparent 2px),"
                  "linear-gradient(90deg,#ecebe4 2px,transparent 2px);background-size:60px 60px;opacity:.7}.pz text{font-family:inherit;font-weight:800}")
    if cfg.get("tema") == "verde":   # MiHuertoUrbano: mismo estilo con verdes de huerto
        extra = extra.replace("#2e2a8f 0%,#4f46e5 45%,#7c3aed 100%", "#14532d 0%,#1f7a3d 45%,#3f9b4a 100%").replace("background:#3f37c9", "background:#1f7a3d").replace("#22d3ee", "#a3e635").replace("#f472b6", "#fbbf24")
    css = CSS.replace("url(F/", f"url(file://{AQUI / 'fuentes'}/") + extra
    fondo = "<div id='fondo'><i></i><i></i><i></i><b></b></div>" if color else ""
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{css}</style></head><body>{fondo}"
            f"<div id='cap'></div><div id='escenas'></div><script>window.DATOS={json.dumps(datos, ensure_ascii=False)};"
            f"window.ESCENAS={json.dumps(cfg['escenas'], ensure_ascii=False)};window.PALABRA={json.dumps(cfg.get('palabra', ''))};"
            f"window.MARCA={json.dumps(cfg.get('marca','iando.xyz'))};window.ICONOS={json.dumps(iconos)};window.DIBUJOS={json.dumps(dibujos)};{JS}{JS_COLOR if color else ''}</script></body></html>")


# Voz: el cupo gratuito de Gemini es de pocos audios al día, así que se pide UN SOLO audio con el guion entero
# (con pausas entre frases, estilo G.ESTILO) y aquí se trocea por frases. Si el troceo no cuadra, se piden las
# frases sueltas como respaldo. Los reels hechos antes con un audio por frase (G.ESTILO_LIBRE) siguen valiendo.
def voces_reel(frases):
    """Lista de (pcm, sr) por frase, o None en las frases que aún no tienen audio."""
    sueltas = [G.descargar(f, estilo=G.ESTILO_LIBRE) for f in frases]
    if all(sueltas):
        return sueltas
    entero = G.descargar(" ".join(frases), estilo=G.ESTILO)
    if entero:
        try:
            import alinear_voz
            trozos = alinear_voz.alinear(entero[0], entero[1], frases)
        except Exception as e:   # sin Kokoro o librosa: troceo por silencios, menos fino
            print(f"AVISO: alineado con Kokoro no disponible ({e}); troceo por silencios", file=sys.stderr)
            trozos = G.partir_alineado(entero[0], entero[1], frases)
        if trozos:
            return [(t, entero[1]) for t in trozos]
    return sueltas


def pedido_voz(frases):
    voces = voces_reel(frases)
    if all(voces):
        return "Ya están todos los audios."
    if G.descargar(" ".join(frases), estilo=G.ESTILO) is None:
        tandas = G.pedido([" ".join(frases)], estilo=G.ESTILO)          # un solo audio para todo el reel
    else:   # el audio entero existe pero no se trocea bien: frases sueltas de respaldo
        tandas = G.pedido([f for f, v in zip(frases, voces) if not v], estilo=G.ESTILO_LIBRE)
    return "\n".join(G.sql_pedido(tandas)) if tandas else "Ya están todos los audios."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--pedido-voz", action="store_true")
    ap.add_argument("--sin-voz", action="store_true")
    ap.add_argument("--kokoro", action="store_true", help="voz de respaldo (Kokoro em_alex) para pruebas, sin gastar cupo de Gemini")
    ap.add_argument("--salida", default=str(RAIZ / "reels"))
    a = ap.parse_args()
    cfg = json.load(open(a.config)); cfg["_ruta"] = a.config
    frases = [e["voz"].strip() for e in cfg["escenas"]]
    if a.pedido_voz:
        print(pedido_voz(frases))
        return
    if a.kokoro:
        from voz_kokoro import Kokoro24
        kok = Kokoro24(velocidad=1.08)
        voces = []
        for f in frases:
            pcm, _ = kok.decir(f)
            voces.append((pcm, kok.sr))
    else:
        voces = None if a.sin_voz else voces_reel(frases)
    datos, pcms, sr, t = [], [], 24000, INICIO
    for k, (e, f) in enumerate(zip(cfg["escenas"], frases)):
        r = voces[k] if voces else None
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
    for v in list((tmp / "fr").glob("*.jpg")) + list((tmp / "fr").glob("*.png")):
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
        pg.on("pageerror", lambda e: print("ERROR JS:", e, file=sys.stderr)); pg.goto(f"file://{tmp / 'reel.html'}"); pg.wait_for_timeout(500)
        n = int(total * FPS + 0.999)
        for k in range(n):
            pg.evaluate("t => window.render(t)", k / FPS)
            if cfg.get("fondo_video"):
                pg.screenshot(path=str(tmp / "fr" / f"{k:05d}.png"), omit_background=True)
            else:
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
    if cfg.get("fondo_video"):   # fondo: un clip por escena (campo "video", ruta relativa a la config), recortado a lo que dura
        base = pathlib.Path(a.config).parent; partes = []
        for k, (e, d) in enumerate(zip(cfg["escenas"], datos)):
            fin = datos[k + 1]["ini"] if k + 1 < len(datos) else total
            ini = 0 if k == 0 else d["ini"]
            seg = tmp / f"bg{k:02d}.mp4"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(base / e["video"]), "-t", f"{fin - ini:.3f}", "-an",
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,eq=brightness=-0.04:saturation=1.08",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(seg)], check=True)
            partes.append(seg)
        (tmp / "bg.txt").write_text("".join(f"file '{x}'\n" for x in partes))
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "bg.txt"), "-c", "copy", str(tmp / "bg.mp4")], check=True)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(tmp / "bg.mp4"), "-framerate", str(FPS), "-i", str(tmp / "fr/%05d.png"), "-i", str(audio),
                        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[v]", "-map", "[v]", "-map", "2:a",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                        "-shortest", "-movflags", "+faststart", str(mp4)], check=True)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{datos[0]['dur'] * 0.9:.2f}", "-i", str(mp4), "-frames:v", "1", str(salida / f"{cfg['slug']}-portada.jpg")], check=True)
        print(json.dumps({"reel": str(mp4), "portada": str(salida / f"{cfg['slug']}-portada.jpg"), "segundos": round(total, 1), "voz": "gemini", "fondo": "video"}, ensure_ascii=False))
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "fr/%05d.jpg"), "-i", str(audio),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(mp4)], check=True)
    print(json.dumps({"reel": str(mp4), "portada": str(salida / f"{cfg['slug']}-portada.jpg"), "segundos": round(total, 1),
                      "voz": "kokoro" if a.kokoro else ("ninguna" if a.sin_voz else "gemini")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
