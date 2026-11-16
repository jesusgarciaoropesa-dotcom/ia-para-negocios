// Función reservas-correos (Supabase Edge Function).
// Manda a los clientes de las reservas: confirmación al reservar, recordatorio el día y, después, petición de reseña.
// Solo para negocios con negocios.config.correos.activo = true. Sin RESEND_API_KEY no envía nada.
// La llaman: el disparador al entrar una reserva (confirmación al momento) y pg_cron cada 15 min.
// config.correos = { "activo": true, "telefono": "637847114", "whatsapp": "34637847114", "responder_a": "negocio@…",
//                    "direccion": "Calle …", "resena_url": "https://g.page/r/…/review" }
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const KEY = Deno.env.get("RESEND_API_KEY");
const FROM = Deno.env.get("RESEND_FROM") || "reservas@iando.xyz";
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));
const hex = (v: unknown, d: string) => (typeof v === "string" && /^#[0-9a-f]{3,8}$/i.test(v) ? v : d);
const fechaLarga = (f: string) => new Date(f + "T12:00:00").toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long", timeZone: "Europe/Madrid" });

type P = { reserva_id: string; tipo: "confirmacion" | "recordatorio" | "resena"; email: string; nombre: string; servicio: string;
  fecha: string; hora: string; duracion: number; notas: string | null; negocio: string; config: any };

function correo(p: P) {
  const t = p.config?.tema || {}, c = t.colores || {}, k = p.config?.correos || {};
  const nom = t.nombre || p.negocio, oscuro = hex(c.oscuro, "#1d2320"), prim = hex(c.primario, "#1f3a2c"), fondo = hex(c.fondo, "#f6f5f1");
  const hora = String(p.hora).slice(0, 5), dia = fechaLarga(p.fecha), pila = esc(String(p.nombre || "").split(" ")[0]);
  const wa = /^\d{11,13}$/.test(k.whatsapp || "") ? `https://wa.me/${k.whatsapp}` : "";
  const tel = /^\d{9}$/.test(k.telefono || "") ? k.telefono : "";
  const contacto = wa || tel ? `<p style="margin:16px 0 0;font-size:15px;color:#555">¿Necesitas cambiarla o anularla? ${wa ? `<a href="${wa}" style="color:${prim}">Escríbenos por WhatsApp</a>` : ""}${wa && tel ? " o llama al " : tel ? "Llámanos al " : ""}${tel ? `<a href="tel:+34${tel}" style="color:${prim}">${tel.replace(/(\d{3})(\d{3})(\d{3})/, "$1 $2 $3")}</a>` : ""}.</p>` : "";
  const ficha = `<table role="presentation" style="width:100%;border-collapse:collapse;margin:18px 0;background:${fondo};border-radius:10px">
    <tr><td style="padding:14px 16px;font-size:16px;line-height:1.6;color:#222"><b>${esc(p.servicio)}</b><br>${esc(dia)} a las <b>${hora}</b>${p.notas ? `<br><span style="color:#555">${esc(p.notas)}</span>` : ""}${k.direccion ? `<br><span style="color:#555">${esc(k.direccion)}</span>` : ""}</td></tr></table>`;
  let asunto = "", cuerpo = "";
  if (p.tipo === "confirmacion") {
    asunto = `Reserva confirmada: ${dia} a las ${hora}`;
    cuerpo = `<h1 style="margin:0 0 8px;font-size:24px;color:#111">¡Hecho, ${pila}!</h1><p style="margin:0;font-size:16px;color:#333">Tu reserva en ${esc(nom)} está apuntada.</p>${ficha}${contacto}`;
  } else if (p.tipo === "recordatorio") {
    const hoy = new Date().toLocaleDateString("en-CA", { timeZone: "Europe/Madrid" }) === p.fecha;
    asunto = `${hoy ? "Hoy" : "Mañana"} a las ${hora} en ${nom}`;
    cuerpo = `<h1 style="margin:0 0 8px;font-size:24px;color:#111">${hoy ? "Hoy" : "Mañana"} te esperamos</h1><p style="margin:0;font-size:16px;color:#333">Te recordamos tu reserva en ${esc(nom)}.</p>${ficha}${contacto}`;
  } else {
    asunto = `¿Qué tal en ${nom}?`;
    cuerpo = `<h1 style="margin:0 0 8px;font-size:24px;color:#111">Gracias por venir, ${pila}</h1><p style="margin:0 0 20px;font-size:16px;color:#333">Si te gustó, nos ayuda mucho que lo cuentes en Google. Es un minuto.</p>
      <p style="margin:0"><a href="${esc(k.resena_url)}" style="display:inline-block;background:${prim};color:#fff;text-decoration:none;font-weight:bold;padding:14px 22px;border-radius:10px;font-size:16px">Dejar mi opinión</a></p>`;
  }
  const html = `<!doctype html><html lang="es"><body style="margin:0;background:#eeeeee;font-family:Arial,Helvetica,sans-serif">
  <table role="presentation" style="width:100%;border-collapse:collapse"><tr><td align="center" style="padding:24px 12px">
  <table role="presentation" style="width:100%;max-width:560px;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden">
  <tr><td style="background:${oscuro};padding:18px 24px;color:#fff;font-size:20px;font-weight:bold">${esc(nom)}</td></tr>
  <tr><td style="padding:26px 24px 30px">${cuerpo}</td></tr></table>
  <p style="font-size:12px;color:#888;margin:14px 0 0">Recibes este correo por tu reserva en ${esc(nom)}.</p></td></tr></table></body></html>`;
  return { asunto, html, nom, responder: typeof k.responder_a === "string" && k.responder_a.includes("@") ? k.responder_a : undefined };
}

Deno.serve(async () => {
  const { data, error } = await db.rpc("correos_pendientes");
  if (error) return Response.json({ ok: false, error: error.message }, { status: 500 });
  const lista = (data || []) as P[];
  if (!KEY) return Response.json({ ok: true, sin_clave: true, pendientes: lista.length });
  const res: Record<string, number> = { enviados: 0, fallos: 0 };
  for (const p of lista) {
    const tag = "email_" + p.tipo;
    const { data: mio } = await db.rpc("reclamar_aviso", { p_reserva: p.reserva_id, p_tag: tag });
    if (!mio) continue;
    const m = correo(p);
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST", headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: `${m.nom} <${FROM}>`, to: [p.email], subject: m.asunto, html: m.html, reply_to: m.responder }),
    });
    if (r.ok) res.enviados++;
    else { res.fallos++; console.error("resend", r.status, await r.text()); await db.rpc("soltar_aviso", { p_reserva: p.reserva_id, p_tag: tag }); }
  }
  return Response.json({ ok: true, ...res });
});
