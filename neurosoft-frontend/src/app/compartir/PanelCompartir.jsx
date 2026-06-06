/* ═══════════════════════════════════════════════════════════════════════
 * SharePanel.jsx — Compartir informes (Telemedicina) — Fase H-bis
 * ───────────────────────────────────────────────────────────────────────
 * Provee:
 *   · ShareButton    — botón que abre un modal para generar link público
 *   · SharedViewer   — página pública (sin auth) que muestra el informe
 *                      cuando alguien abre /shared/view/{token}
 *
 * Uso típico en EvalResultsPage:
 *   <ShareButton evaluationId={evalId}/>
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { useConfirm } from "../../contexts.jsx";

const API  = import.meta.env.PROD ? "" : "http://localhost:8000";
const _tok  = () => localStorage.getItem("ns_token") || "";
const _hdrs = (json = false) => {
  const h = { Authorization: `Bearer ${_tok()}` };
  if (json) h["Content-Type"] = "application/json";
  return h;
};
async function shGet(path, auth = true) {
  const r = await fetch(`${API}${path}`, { headers: auth ? _hdrs() : {} });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `HTTP ${r.status}`);
  return r.json();
}
async function shPost(path, body, auth = true) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: auth ? _hdrs(true) : { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `HTTP ${r.status}`);
  return r.json();
}

/* ─── ShareButton ──────────────────────────────────────────────────── */
export function ShareButton({ evaluationId }) {
  const [open, setOpen] = useState(false);
  const [ttl, setTtl]   = useState(72);
  const [scope, setScope] = useState("summary");
  const [password, setPassword] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [link, setLink] = useState(null);
  const [err, setErr]   = useState("");

  const create = async () => {
    setBusy(true); setErr(""); setLink(null);
    try {
      const r = await shPost("/api/v1/shared", {
        evaluation_id: evaluationId,
        ttl_hours: Number(ttl),
        scope,
        password: password.trim() || null,
      });
      const base = window.location.origin;
      setLink(`${base}${r.public_url}`);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };

  const copy = () => {
    if (!link) return;
    const extra = videoUrl.trim()
      ? `\n\nSala de videollamada: ${videoUrl.trim()}`
      : "";
    navigator.clipboard.writeText(link + extra);
  };

  if (!evaluationId) return null;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="px-3 py-2 rounded-xl bg-white border border-teal-300 text-teal-700 text-xs font-bold hover:bg-teal-50 flex items-center gap-1.5"
      >
        <span className="material-symbols-outlined text-sm">share</span>
        Compartir informe
      </button>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={() => setOpen(false)}>
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold">Compartir informe</h3>
                <p className="text-[11px] text-slate-500">Genera un link temporal para paciente o remitente. Se omiten datos identificables.</p>
              </div>
              <button onClick={() => setOpen(false)}>
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {!link && (
              <>
                <div className="rounded-xl p-3 text-[11px] leading-relaxed bg-teal-50 border border-teal-200 text-teal-900">
                  <p className="font-bold mb-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">info</span>
                    ¿Qué hace este enlace?
                  </p>
                  Genera una página web <strong>de solo lectura</strong> con el resultado del informe.
                  El paciente o el médico remitente la abren desde el navegador, <strong>sin instalar nada ni iniciar sesión</strong>.
                  El enlace <strong>vence solo</strong> al cumplirse la vigencia y puedes <strong>revocarlo</strong> en cualquier momento.
                  Si añades una sala de videollamada, tienes telemedicina completa: ven el informe mientras hablan contigo.
                </div>
                <div>
                  <label className="text-xs font-bold uppercase text-slate-500">Alcance</label>
                  <select value={scope} onChange={e => setScope(e.target.value)}
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm">
                    <option value="summary">Resumen (puntos fuertes / débiles / advertencias)</option>
                    <option value="iq_only">Solo CI (WISC-IV / WAIS-III)</option>
                    <option value="full">Informe completo (Z-scores y resultados)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-bold uppercase text-slate-500">Vigencia (h)</label>
                    <input type="number" min="1" max="720"
                      value={ttl} onChange={e => setTtl(e.target.value)}
                      className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm"/>
                    <p className="text-[9px] text-slate-400">máximo 30 días (720 h)</p>
                  </div>
                  <div>
                    <label className="text-xs font-bold uppercase text-slate-500">Contraseña (opcional)</label>
                    <input type="text"
                      value={password} onChange={e => setPassword(e.target.value)}
                      placeholder="dejar vacío = sin contraseña"
                      className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm"/>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-bold uppercase text-slate-500">Videollamada (opcional)</label>
                  <input type="url"
                    value={videoUrl} onChange={e => setVideoUrl(e.target.value)}
                    placeholder="Link Meet, Zoom o Jitsi para acompañar el informe"
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm"/>
                  <p className="text-[9px] text-slate-400 mt-1">Se incluye al copiar el link. No se almacena en el servidor.</p>
                </div>

                {err && <div className="text-xs text-rose-700 bg-rose-50 p-2 rounded-lg">{err}</div>}

                <button onClick={create} disabled={busy}
                  className="w-full py-2.5 rounded-xl bg-teal-600 text-white font-bold hover:bg-teal-700 disabled:opacity-50">
                  {busy ? "Generando…" : "Generar link"}
                </button>
              </>
            )}

            {link && (
              <>
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2">
                  <p className="text-xs font-bold text-emerald-800">Link generado</p>
                  <code className="text-[11px] block break-all bg-white p-2 rounded border">{link}</code>
                  <button onClick={copy} className="w-full py-2 rounded-lg bg-emerald-600 text-white text-xs font-bold">
                    Copiar al portapapeles
                  </button>
                </div>
                <p className="text-[10px] text-slate-500">
                  El link vence automáticamente. Puedes revocarlo desde el panel de telemedicina.
                </p>
                {videoUrl.trim() && (
                  <p className="text-[10px] text-slate-500">
                    Videollamada: <code className="break-all">{videoUrl.trim()}</code>
                  </p>
                )}
                <button onClick={() => { setLink(null); setPassword(""); setVideoUrl(""); }}
                  className="w-full py-2 rounded-xl border border-slate-300 text-xs">Generar otro</button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

/* ─── SecondOpinionButton — segunda opinión entre colegas ──────────── */
export function SecondOpinionButton({ evaluationId, _patientName }) {
  const [open, setOpen]   = useState(false);
  const [anon, setAnon]   = useState(true);
  const [note, setNote]   = useState("");
  const [busy, setBusy]   = useState(false);
  const [link, setLink]   = useState(null);
  const [err,  setErr]    = useState("");

  const create = async () => {
    setBusy(true); setErr(""); setLink(null);
    try {
      const r = await shPost("/api/v1/shared", {
        evaluation_id: evaluationId,
        ttl_hours: 168,           // 7 días para revisión por par
        scope: "full",
        password: null,
        metadata: {
          purpose: "segunda_opinion",
          anonimizado: anon,
          nota_solicitante: note.trim() || null,
        },
      });
      const base = window.location.origin;
      setLink(`${base}${r.public_url}`);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };

  const copy = () => { if (link) navigator.clipboard.writeText(link); };

  if (!evaluationId) return null;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        title="Solicitar segunda opinión de un colega"
        className="px-3 py-2 rounded-xl bg-white border border-violet-300 text-violet-700 text-xs font-bold hover:bg-violet-50 flex items-center gap-1.5"
      >
        <span className="material-symbols-outlined text-sm">supervised_user_circle</span>
        2ª Opinión
      </button>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={() => setOpen(false)}>
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined text-violet-600">supervised_user_circle</span>
                  Solicitar segunda opinión
                </h3>
                <p className="text-[11px] text-slate-500 mt-1">
                  Comparte el caso con un colega para revisión por pares.
                  El link vence en 7 días y puede incluir todos los resultados.
                </p>
              </div>
              <button onClick={() => setOpen(false)}>
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {!link && (
              <>
                {/* Anonimización */}
                <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 cursor-pointer hover:bg-slate-50">
                  <input type="checkbox" checked={anon} onChange={e => setAnon(e.target.checked)}
                    className="mt-0.5 w-4 h-4 text-violet-600"/>
                  <div>
                    <p className="text-sm font-bold">Anonimizar datos identificables</p>
                    <p className="text-[11px] text-slate-500">
                      El nombre y documento del paciente se reemplazarán por "Paciente X".
                      Los resultados clínicos y el informe se comparten completos.
                    </p>
                  </div>
                </label>

                {/* Nota para el revisor */}
                <div>
                  <label className="text-xs font-bold uppercase text-slate-500">
                    Nota para el revisor (opcional)
                  </label>
                  <textarea
                    value={note} onChange={e => setNote(e.target.value)}
                    rows={3} placeholder="Ej: «Dudas sobre diagnóstico diferencial TEA vs TDAH. ¿El perfil ejecutivo es consistente?»"
                    className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm resize-none"/>
                </div>

                {err && <div className="text-xs text-rose-700 bg-rose-50 p-2 rounded-lg">{err}</div>}

                <button onClick={create} disabled={busy}
                  className="w-full py-2.5 rounded-xl font-bold text-white hover:opacity-90 disabled:opacity-50"
                  style={{ background: "#7c3aed" }}>
                  {busy ? "Generando link…" : "Generar link de revisión"}
                </button>

                <p className="text-[10px] text-slate-400 text-center">
                  Solo el colega con el link puede ver el caso.
                  Vigencia 7 días · conforme con habeas data institucional.
                </p>
              </>
            )}

            {link && (
              <>
                <div className="p-3 rounded-xl bg-violet-50 border border-violet-200 space-y-2">
                  <p className="text-xs font-bold text-violet-800 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Link de revisión generado
                  </p>
                  <code className="text-[11px] block break-all bg-white p-2 rounded border">{link}</code>
                  <button onClick={copy}
                    className="w-full py-2 rounded-lg text-white text-xs font-bold"
                    style={{ background: "#7c3aed" }}>
                    Copiar al portapapeles
                  </button>
                </div>
                <div className="p-3 rounded-xl bg-amber-50 border border-amber-200">
                  <p className="text-[11px] text-amber-800">
                    <span className="material-symbols-outlined text-sm align-middle mr-1">info</span>
                    Comparta este link solo con el colega de confianza.
                    {anon ? " Datos del paciente anonimizados." : " Datos identificables incluidos — asegúrese de tener consentimiento."}
                    {" "}Vigencia: 7 días.
                  </p>
                </div>
                <button onClick={() => { setLink(null); setNote(""); }}
                  className="w-full py-2 rounded-xl border border-slate-300 text-xs">
                  Generar otro link
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

/* ─── SharesPage — gestión de links activos ────────────────────────── */
export function SharesPage() {
  const confirm = useConfirm();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");

  const load = async () => {
    setLoading(true);
    try { setItems(await shGet("/api/v1/shared")); }
    catch (e) { setMsg("Error: " + e.message); setItems([]); }
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const revoke = async (token) => {
    if (!(await confirm({
      title: "Revocar link",
      message: "El destinatario perderá acceso inmediatamente.\nEsta acción es irreversible.",
      confirmText: "Revocar",
      dangerous: true,
    }))) return;
    try {
      const r = await fetch(`${API}/api/v1/shared/${token}`, { method: "DELETE", headers: _hdrs() });
      if (!r.ok) throw new Error("HTTP " + r.status);
      setMsg("Link revocado");
      load();
    } catch (e) { setMsg("Error: " + e.message); }
  };

  const copyLink = (token) => {
    const url = `${window.location.origin}/shared/view/${token}`;
    navigator.clipboard.writeText(url);
    setMsg("Link copiado: " + url);
    setTimeout(() => setMsg(""), 2500);
  };

  const fmt = (s) => { if (!s) return "—"; try { return new Date(s).toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" }); } catch { return s; } };
  const isExpired = (s) => s && new Date(s) < new Date();

  return (
    <div className="max-w-7xl mx-auto p-8 space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Telemedicina · Links compartidos</h1>
        <p className="text-sm text-slate-500 mt-1">
          Gestione los informes que ha compartido con pacientes o remitentes. Los links revocados
          dejan de funcionar de inmediato.
        </p>
      </header>
      {msg && <div className="p-3 rounded-xl text-sm bg-emerald-50 text-emerald-700">{msg}</div>}
      <div className="flex items-center justify-between">
        <p className="text-sm font-bold">{items.length} link{items.length === 1 ? "" : "s"} registrado{items.length === 1 ? "" : "s"}</p>
        <button onClick={load} className="text-xs px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200">Refrescar</button>
      </div>
      {loading ? (
        <div className="flex justify-center py-12"><div className="animate-spin w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full"/></div>
      ) : items.length === 0 ? (
        <div className="rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center text-slate-400">
          <span className="material-symbols-outlined text-5xl opacity-40">link_off</span>
          <p className="mt-3 text-sm font-bold">No ha compartido informes todavía</p>
          <p className="text-xs mt-1">Use el botón "Compartir informe" desde los resultados de una evaluación.</p>
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider">Paciente / Evaluación</th>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider">Alcance</th>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider">Creado</th>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider">Vence</th>
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider">Estado</th>
                <th className="px-4 py-3 w-48"></th>
              </tr>
            </thead>
            <tbody>
              {items.map((s) => {
                const expired = isExpired(s.expires_at);
                const status = s.revoked ? { label: "Revocado", cls: "bg-slate-100 text-slate-500" }
                             : expired  ? { label: "Expirado", cls: "bg-amber-50 text-amber-700" }
                             :            { label: "Activo",   cls: "bg-emerald-50 text-emerald-700" };
                const active = !s.revoked && !expired;
                return (
                  <tr key={s.token} className="border-t border-slate-100">
                    <td className="px-4 py-3">
                      <p className="text-xs font-bold">{s.patient_name || s.evaluation_id}</p>
                      <p className="text-[10px] font-mono text-slate-400">{s.evaluation_id?.slice(0, 8)}…</p>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 uppercase">
                        {s.scope}
                      </span>
                      {s.has_password && <span className="ml-1 text-[10px]" title="Protegido con contraseña">🔒</span>}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{fmt(s.created_at)}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">{fmt(s.expires_at)}</td>
                    <td className="px-4 py-3">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${status.cls}`}>{status.label}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1 justify-end">
                        {active && (
                          <button onClick={() => copyLink(s.token)}
                            className="text-[10px] font-bold px-2 py-1 rounded bg-slate-100 hover:bg-slate-200">
                            Copiar
                          </button>
                        )}
                        {active && (
                          <button onClick={() => revoke(s.token)}
                            className="text-[10px] font-bold px-2 py-1 rounded bg-rose-50 text-rose-700 hover:bg-rose-100">
                            Revocar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ─── SharedViewer — página pública ────────────────────────────────── */
export function SharedViewer({ token }) {
  const [data, setData]     = useState(null);
  const [err, setErr]       = useState("");
  const [needPw, setNeedPw] = useState(false);
  const [pw, setPw]         = useState("");
  const [busy, setBusy]     = useState(false);

  const load = async () => {
    setBusy(true); setErr("");
    try {
      const r = await shGet(`/api/v1/shared/view/${token}`, false);
      if (r.requires_password) setNeedPw(true);
      else setData(r);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { if (token) load(); }, [token]);

  const submitPw = async () => {
    setBusy(true); setErr("");
    try {
      const r = await shPost(`/api/v1/shared/view/${token}/verify`, { password: pw }, false);
      setData(r); setNeedPw(false);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };

  if (err && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="p-6 rounded-2xl bg-white shadow-xl max-w-md text-center">
          <span className="material-symbols-outlined text-5xl text-rose-500">link_off</span>
          <h2 className="text-xl font-bold mt-3">Link no disponible</h2>
          <p className="text-sm text-slate-600 mt-2">{err}</p>
        </div>
      </div>
    );
  }

  if (needPw) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="p-6 rounded-2xl bg-white shadow-xl max-w-md w-full">
          <h2 className="text-xl font-bold">Informe protegido</h2>
          <p className="text-xs text-slate-500 mt-1">Ingrese la contraseña proporcionada por el profesional.</p>
          <input type="password" value={pw} onChange={e => setPw(e.target.value)}
            className="mt-4 w-full px-3 py-2 rounded-lg border border-slate-200"/>
          {err && <p className="text-xs text-rose-700 mt-2">{err}</p>}
          <button onClick={submitPw} disabled={busy}
            className="mt-4 w-full py-2.5 rounded-xl bg-teal-600 text-white font-bold">
            {busy ? "Verificando…" : "Ver informe"}
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin w-10 h-10 border-4 border-teal-200 border-t-teal-600 rounded-full"/>
      </div>
    );
  }

  const ev = data.evaluation || {};
  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-xl overflow-hidden">
        <header className="p-6" style={{ background: "linear-gradient(135deg, #0F172A, #0D9488)", color: "white" }}>
          <p className="text-[10px] uppercase tracking-widest opacity-80">Informe Neuropsicológico Compartido</p>
          <h1 className="text-2xl font-bold mt-1">{data.patient_alias}</h1>
          <p className="text-xs opacity-90 mt-0.5">
            {ev.protocolo} · {ev.fecha || "—"} {ev.edad && `· ${ev.edad}`} {ev.poblacion && `· ${ev.poblacion}`}
          </p>
        </header>

        <div className="p-6 space-y-5">
          {Array.isArray(data.puntos_fuertes) && data.puntos_fuertes.length > 0 && (
            <section>
              <h2 className="font-bold text-emerald-700 text-sm">Puntos fuertes</h2>
              <ul className="list-disc ml-5 text-sm mt-2 space-y-1">
                {data.puntos_fuertes.map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            </section>
          )}

          {Array.isArray(data.puntos_debiles) && data.puntos_debiles.length > 0 && (
            <section>
              <h2 className="font-bold text-amber-700 text-sm">Áreas a fortalecer</h2>
              <ul className="list-disc ml-5 text-sm mt-2 space-y-1">
                {data.puntos_debiles.map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            </section>
          )}

          {Array.isArray(data.advertencias) && data.advertencias.length > 0 && (
            <section>
              <h2 className="font-bold text-rose-700 text-sm">Advertencias</h2>
              <ul className="list-disc ml-5 text-sm mt-2 space-y-1">
                {data.advertencias.map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            </section>
          )}

          {Array.isArray(data.iq) && data.iq.length > 0 && (
            <section>
              <h2 className="font-bold text-slate-700 text-sm">Índices CI</h2>
              <table className="w-full text-sm mt-2 border border-slate-200 rounded-xl overflow-hidden">
                <thead className="bg-slate-50 text-xs">
                  <tr><th className="p-2 text-left">Índice</th><th className="p-2 text-right">Valor</th></tr>
                </thead>
                <tbody>
                  {data.iq.map((r, i) => (
                    <tr key={i} className="border-t border-slate-200">
                      <td className="p-2">{r.test_nombre || r.nombre || r.test_id}</td>
                      <td className="p-2 text-right font-bold">{r.valor || r.index || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {Array.isArray(data.resultados) && data.resultados.length > 0 && (
            <section>
              <h2 className="font-bold text-slate-700 text-sm">Resultados detallados</h2>
              <div className="mt-2 space-y-1 text-xs">
                {data.resultados.slice(0, 50).map((r, i) => (
                  <div key={i} className="flex justify-between p-2 border-b border-slate-100">
                    <span>{r.test_nombre || r.nombre || r.test_id}</span>
                    <span className="font-mono">{r.z_score ?? r.pd ?? "—"}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          <footer className="pt-4 border-t border-slate-200 text-[10px] text-slate-400 text-center">
            Informe compartido · Este link vence el {data.expires_at?.slice(0, 10) || "—"}.
            <br/>Contenido sanitizado — sin información identificable del paciente.
          </footer>
        </div>
      </div>
    </div>
  );
}
