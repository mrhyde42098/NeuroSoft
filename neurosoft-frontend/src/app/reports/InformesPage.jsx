/* ═══════════════════════════════════════════════════════════════════════
 * src/app/reports/InformesPage.jsx — Generación de informes PDF/DOCX/XLSX
 * ───────────────────────────────────────────────────────────────────────
 * Stepper visual de 4 pasos: Paciente → Evaluación → Previsualizar → Descargar.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { api } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Btn, Card, I, Input, Label, Sel, TopBar, Txta } from "../../ui/primitives.jsx";
import GlossaryTerm from "../../ui/GlossaryTerm.jsx"; // §N2
import { TEAL } from "../../ui/tokens.js";
import { SkeletonCard } from "../../ui/Skeleton.jsx";

const STEPS = [
  { label: "Paciente",       icon: "person" },
  { label: "Evaluación",     icon: "clinical_notes" },
  { label: "Previsualizar",  icon: "preview" },
  { label: "Descargar",      icon: "download" },
];

const PDF_TEMPLATES = [
  { value: "pro", label: "★ Profesional (estándar)" },
  { value: "pediatrico", label: "Pediátrica" },
  { value: "medicolegal", label: "Medicolegal" },
  { value: "junta_medica", label: "Junta Médica" },
  { value: "inconcluso", label: "Inconclusa" },
  { value: "paciente", label: "Paciente (lenguaje claro)" },
  { value: "therapy_closure", label: "Cierre terapéutico" },
  { value: "estandar", label: "Clásico (legado)" },
];

export default function InformesPage({ _setPage }) {
  const toast = useToast();
  const [patients, setPatients] = useState([]);
  const [patId, setPatId] = useState("");
  const [evals, setEvals] = useState([]);
  const [ld, setLd] = useState(false);
  const [preview, setPreview] = useState(null);
  const [gen, setGen] = useState(null);
  const [pdfTemplate, setPdfTemplate] = useState("pro");
  /* Overlay in-page para PDF (pywebview no soporta descarga vía a.download) */
  const [pdfOverlay, setPdfOverlay] = useState(null); // { url: blobUrl, filename, blob, evalId }
  const pdfIframeRef = useRef(null);

  /* §QW-1: Modal de envío por correo */
  const [emailModal, setEmailModal] = useState(null); // { evalId, paciente, fecha }
  const [emailSending, setEmailSending] = useState(false);
  const [emailForm, setEmailForm] = useState({
    to: "", cc: "", subject: "", body: "",
    tipo: "informe", include_pdf: true,
  });
  /* §QW-1: Estado SMTP (para deshabilitar botón si no configurado) */
  const [smtpReady, setSmtpReady] = useState(null);
  useEffect(() => {
    api.get("/api/v1/emails/status")
      .then(d => setSmtpReady(!!d.configured))
      .catch(() => setSmtpReady(false));
  }, []);

  useEffect(() => {
    api.get("/api/v1/patients/panel")
      .then(d => setPatients(d.pacientes || d || []))
      .catch(() => toast.error("Error al cargar datos"));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadE = async (pid) => {
    if (!pid) return;
    setLd(true);
    setPreview(null);
    try {
      const d = await api.get(`/api/v1/evaluations/${pid}`);
      setEvals(d.evaluaciones || d.evaluations || []);
    } catch { setEvals([]); }
    setLd(false);
  };
  const loadP = async (id) => {
    try { setPreview(await api.get(`/api/v1/reports/preview/${id}`)); }
    catch { setPreview({ error: true }); }
  };
  const downloadBlob = async (urlPath, filename, key, evalId = null) => {
    setGen(key);
    try {
      const b = await api.blob(urlPath);
      const u = URL.createObjectURL(b);

      if (filename.endsWith(".pdf")) {
        /* PDF → mostrar en overlay in-page. En pywebview, a.download no abre
           diálogo nativo. El usuario imprime/guarda desde el visor de PDF.
           §QW-1: guardamos también el blob para "Guardar como…" y print. */
        setPdfOverlay({ url: u, filename, blob: b, evalId });
      } else {
        /* DOCX / XLSX → descarga directa (sí funciona en pywebview) */
        const a = document.createElement("a");
        a.href = u;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(u), 3000);
      }
    } catch (e) {
      toast.error("Error generando documento: " + (e.detail || e.message || JSON.stringify(e)));
    }
    setGen(null);
  };
  const closePdfOverlay = () => {
    if (pdfOverlay) { URL.revokeObjectURL(pdfOverlay.url); setPdfOverlay(null); }
  };
  const genPDF  = (id) => downloadBlob(
    `/api/v1/reports/pdf/${id}?template=${encodeURIComponent(pdfTemplate)}`,
    `InformeNPS_${pdfTemplate}_${id.slice(0, 8)}.pdf`,
    id,
    id,
  );
  const genDOCX = (id) => downloadBlob(`/api/v1/reports/docx/${id}`, `InformeNPS_${id.slice(0, 8)}.docx`, `docx:${id}`);
  const genXLSX = (id) => downloadBlob(`/api/v1/reports/xlsx/${id}`, `Puntajes_${id.slice(0, 8)}.xlsx`,   `xlsx:${id}`);

  /* §QW-1: Imprimir directamente desde iframe del overlay PDF.
     Funciona en pywebview (Edge WebView2 soporta print del iframe).
     En navegador estándar también funciona. */
  const printPdfFromOverlay = () => {
    try {
      const iframe = pdfIframeRef.current;
      if (!iframe || !iframe.contentWindow) {
        toast.error("Visor PDF no listo");
        return;
      }
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    } catch {
      toast.error("No se pudo abrir diálogo de impresión");
    }
  };

  /* §QW-1: Guardar como… usando File System Access API (Chrome/Edge ≥86).
     Fallback: descarga normal con a.download.
     En pywebview cae al fallback porque el API no está disponible. */
  const savePdfAs = async () => {
    if (!pdfOverlay) return;
    const { blob, filename } = pdfOverlay;
    if (window.showSaveFilePicker) {
      try {
        const handle = await window.showSaveFilePicker({
          suggestedName: filename,
          types: [{ description: "PDF", accept: { "application/pdf": [".pdf"] } }],
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        toast.success("Informe guardado");
        return;
      } catch (e) {
        if (e.name === "AbortError") return; // usuario canceló
        // si falla por permiso, cae al fallback
      }
    }
    // Fallback: descarga normal
    const a = document.createElement("a");
    a.href = pdfOverlay.url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast.success("Descarga iniciada");
  };

  /* §QW-1: Abrir modal de envío por correo */
  const openEmailModal = (evalId) => {
    if (!smtpReady) {
      toast.error("SMTP no configurado. Configúralo en Ajustes → Comunicaciones.");
      return;
    }
    setEmailForm({
      to: "", cc: "", subject: "", body: "",
      tipo: "informe", include_pdf: true,
    });
    setEmailModal({
      evalId,
      paciente: preview?.nombre_completo || "",
      fecha: preview?.fecha || "",
    });
  };
  const closeEmailModal = () => { setEmailModal(null); setEmailSending(false); };

  const sendEmail = async () => {
    if (!emailModal) return;
    const to = emailForm.to.split(/[,;]/).map(s => s.trim()).filter(Boolean);
    if (to.length === 0) {
      toast.error("Indica al menos un destinatario");
      return;
    }
    setEmailSending(true);
    try {
      const payload = {
        to,
        cc: emailForm.cc.split(/[,;]/).map(s => s.trim()).filter(Boolean),
        tipo: emailForm.tipo,
        subject: emailForm.subject || undefined,
        body: emailForm.body || undefined,
        include_pdf: emailForm.include_pdf,
      };
      const res = await api.post(
        `/api/v1/reports/${emailModal.evalId}/send-email`,
        payload,
      );
      if (res.ok || res.status === "sent") {
        toast.success(`Correo enviado a ${res.recipient_to || to.join(", ")}`);
        closeEmailModal();
      } else {
        toast.error("Envío falló: " + (res.error || "desconocido"));
      }
    } catch (e) {
      const detail = e.detail || e.message || "";
      const msg = typeof detail === "object" ? detail.error || JSON.stringify(detail) : detail;
      toast.error("Error: " + msg);
    }
    setEmailSending(false);
  };

  const chk = (v, l) => (
    <div className="flex items-center gap-2">
      <I name={v ? "check_circle" : "cancel"}
         className={`text-lg ${v ? "text-teal-600" : "text-gray-300"}`} fill />
      <span className={`text-xs font-semibold ${v ? "text-gray-700" : "text-gray-400"}`}>{l}</span>
    </div>
  );

  /* §M-5: ítem de sección con detalle + crítico */
  const sectionItem = (sec) => {
    const color = sec.ok ? "#10b981" : (sec.critico ? "#dc2626" : "#f59e0b");
    return (
      <div key={sec.id} className="flex items-center gap-2">
        <I name={sec.ok ? "check_circle" : (sec.critico ? "cancel" : "warning")}
           fill className="text-lg" style={{ color }} />
        <span className="text-xs font-semibold flex-1" style={{ color: sec.ok ? "var(--ns-text)" : "var(--ns-muted)" }}>
          {sec.label}
          {sec.detalle && <span className="ml-1 opacity-60">— {sec.detalle}</span>}
        </span>
        {sec.critico && !sec.ok && (
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded"
            style={{ background: "rgba(220,38,38,0.10)", color: "#dc2626" }}>CRÍTICO</span>
        )}
      </div>
    );
  };

  /* Stepper: muestra progreso del flujo de generación */
  const step = !patId ? 0 : !preview || preview.error ? 1 : gen ? 3 : 2;

  return (
    <>
      <TopBar title="Generación de Informes" />
      <main className="p-8 space-y-6">
        <Card className="p-5">
          <div className="flex items-center justify-between gap-2">
            {STEPS.map((s, i) => {
              const active = i === step;
              const done = i < step;
              return (
                <React.Fragment key={s.label}>
                  <div className="flex items-center gap-3 flex-shrink-0"
                    style={{ opacity: active || done ? 1 : 0.5 }}>
                    <div className="w-9 h-9 rounded-full flex items-center justify-center font-extrabold text-sm transition-all"
                      style={
                        active
                          ? { background: TEAL, color: "#fff", boxShadow: "0 8px 20px -4px rgba(13,148,136,0.5)", transform: "scale(1.1)" }
                          : done
                          ? { background: "#10b981", color: "#fff" }
                          : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }
                      }>
                      {done ? <I name="check" fill className="text-base" /> : <I name={s.icon} className="text-base" />}
                    </div>
                    <div className="text-left">
                      <p className="text-[9px] font-extrabold uppercase tracking-widest"
                        style={{ color: active ? TEAL : "var(--ns-muted)" }}>Paso {i + 1}</p>
                      <p className="text-xs font-bold"
                        style={{ color: active ? "var(--ns-text)" : "var(--ns-muted)" }}>{s.label}</p>
                    </div>
                  </div>
                  {i < STEPS.length - 1 && (
                    <div className="flex-1 h-0.5 rounded-full mx-1"
                      style={{ background: i < step ? "#10b981" : "var(--ns-subtle)" }} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex-1">
            <Label>Seleccionar Paciente</Label>
            <Sel value={patId} onChange={(e) => { setPatId(e.target.value); loadE(e.target.value); setPreview(null); }}>
              <option value="">— Seleccione —</option>
              {patients.map(p => (
                <option key={p.id} value={p.id}>
                  {p.nombre_completo || `${p.primer_nombre} ${p.primer_apellido}`} — {p.numero_documento}
                </option>
              ))}
            </Sel>
          </div>
        </Card>

        {!patId ? (
          <div className="flex flex-col items-center py-20 text-gray-400">
            <I name="picture_as_pdf" className="text-6xl mb-4 opacity-30" />
            <p className="font-bold text-lg">Selecciona un paciente</p>
          </div>
        ) : ld ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : (
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-12 lg:col-span-5 space-y-3">
              <h3 className="text-lg font-bold px-1">Evaluaciones ({evals.length})</h3>
              {evals.length === 0 ? (
                <Card className="p-8 text-center text-gray-400">
                  <I name="assignment" className="text-4xl mb-3" />
                  <p className="font-bold">Sin evaluaciones</p>
                </Card>
              ) : (
                evals.map((ev, i) => {
                  const eid = ev.evaluation_id || ev.id;
                  return (
                    <button key={eid || i} onClick={() => loadP(eid)}
                      className={`w-full text-left ${preview && !preview.error && preview.eval_id === eid ? "ring-2 ring-teal-600/30" : ""}`}>
                      <Card className={`p-5 hover:shadow-lg transition-all ${preview && !preview.error && preview.eval_id === eid ? "bg-teal-50/50" : ""}`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-teal-600">{ev.protocolo || "Evaluación"}</span>
                          <span className="text-[10px] text-gray-400 font-bold">{ev.fecha || ""}</span>
                        </div>
                        <p className="text-xs text-gray-500">{ev.pruebas_realizadas || 0} pruebas</p>
                      </Card>
                    </button>
                  );
                })
              )}
            </div>

            <div className="col-span-12 lg:col-span-7">
              {!preview ? (
                <Card className="p-12 text-center text-gray-400 min-h-[400px] flex flex-col items-center justify-center">
                  <I name="preview" className="text-5xl mb-4 opacity-30" />
                  <p className="font-bold text-lg">Selecciona una evaluación</p>
                </Card>
              ) : preview.error ? (
                <Card className="p-12 text-center text-red-400">
                  <I name="error" className="text-5xl mb-4" />
                  <p className="font-bold">Error cargando vista previa</p>
                </Card>
              ) : (
                <div className="space-y-4 sticky top-24">
                  <Card className="p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-lg font-bold">{preview.nombre_completo || "Paciente"}</h3>
                        <p className="text-sm text-gray-400">{preview.protocolo} — {preview.fecha}</p>
                      </div>
                      <span className="bg-teal-100 text-teal-700 text-xs font-bold px-3 py-1 rounded-full capitalize">
                        {(preview.poblacion || "").replace("_", " ")}
                      </span>
                    </div>
                    {/* §M-5: completitud detallada con bloqueos visibles */}
                    <div className="rounded-2xl p-5 space-y-2 mb-6" style={{ background: "var(--ns-subtle)" }}>{/* §dark-mode-fix */}
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Completitud del informe</h4>
                        {typeof preview.completitud_pct === "number" && (
                          <span className="text-xs font-extrabold ns-mono px-2 py-0.5 rounded"
                            style={{
                              background: preview.completitud_pct >= 80 ? "rgba(16,185,129,0.12)" : preview.completitud_pct >= 50 ? "rgba(245,158,11,0.12)" : "rgba(220,38,38,0.12)",
                              color: preview.completitud_pct >= 80 ? "#047857" : preview.completitud_pct >= 50 ? "#92400e" : "#dc2626",
                            }}>
                            {preview.completitud_pct}%
                          </span>
                        )}
                      </div>
                      {Array.isArray(preview.secciones)
                        ? preview.secciones.map(sectionItem)
                        : (<>
                            {chk(preview.resultados_count > 0, `${preview.resultados_count} resultados`)}
                            {chk(preview.tiene_historia_clinica, "Historia clínica")}
                            {chk(preview.tiene_observaciones, "Observaciones clínicas")}
                            {chk(preview.pruebas_realizadas > 0, `${preview.pruebas_realizadas} pruebas`)}
                          </>)
                      }
                    </div>

                    {/* §M-5: panel de bloqueos críticos */}
                    {Array.isArray(preview.bloqueos) && preview.bloqueos.length > 0 && (
                      <div className="rounded-2xl p-4 mb-6 border border-red-200" style={{ background: "rgba(220,38,38,0.04)" }}>
                        <h4 className="text-xs font-bold uppercase tracking-wider mb-2 flex items-center gap-1.5"
                          style={{ color: "#dc2626" }}>
                          <I name="block" className="text-base" />
                          Descarga bloqueada — falta:
                        </h4>
                        <ul className="space-y-1">
                          {preview.bloqueos.map((b, i) => (
                            <li key={i} className="text-xs flex items-center gap-2" style={{ color: "#7f1d1d" }}>
                              <I name="error" className="text-sm" />{b}
                            </li>
                          ))}
                        </ul>
                        <p className="text-[10px] mt-3 italic" style={{ color: "#9f1239" }}>
                          Alternativa: usa plantilla <code className="ns-mono">inconcluso</code> en EvalResultsPage si la batería no se completó por motivo justificado.
                        </p>
                      </div>
                    )}

                    {/* §M-5: advertencias no críticas */}
                    {Array.isArray(preview.advertencias_completitud) && preview.advertencias_completitud.length > 0 && (
                      <div className="rounded-2xl p-3 mb-6 border border-yellow-200" style={{ background: "rgba(245,158,11,0.05)" }}>
                        <h4 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5"
                          style={{ color: "#92400e" }}>
                          <I name="warning" className="text-base" />
                          Recomendaciones de completitud
                        </h4>
                        <ul className="space-y-0.5">
                          {preview.advertencias_completitud.slice(0, 5).map((w, i) => (
                            <li key={i} className="text-xs" style={{ color: "#78350f" }}>• {w}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {preview.advertencias && preview.advertencias.length > 0 && (
                      <div className="rounded-2xl p-4 mb-6 border border-orange-200" style={{ background: "#fff8f0" }}>
                        <h4 className="text-xs font-bold text-orange-600 uppercase mb-2">Advertencias</h4>
                        {preview.advertencias.slice(0, 5).map((w, i) => (
                          <p key={i} className="text-xs text-gray-600 mb-1">• {w}</p>
                        ))}
                      </div>
                    )}
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="rounded-xl p-4" style={{ background: "#ffdad620" }}>
                        <h4 className="text-xs font-bold text-red-600 uppercase mb-2">Puntos Débiles</h4>
                        {(preview.puntos_debiles || []).length > 0
                          ? (preview.puntos_debiles || []).map((p, i) => (
                            <p key={i} className="text-xs text-gray-600">• {typeof p === "string" ? p : p.test_nombre || ""}</p>
                          ))
                          : <p className="text-xs text-gray-400">Ninguno</p>}
                      </div>
                      <div className="rounded-xl p-4" style={{ background: "#0D948815" }}>
                        <h4 className="text-xs font-bold text-teal-600 uppercase mb-2">Puntos Fuertes</h4>
                        {(preview.puntos_fuertes || []).length > 0
                          ? (preview.puntos_fuertes || []).map((p, i) => (
                            <p key={i} className="text-xs text-gray-600">• {typeof p === "string" ? p : p.test_nombre || ""}</p>
                          ))
                          : <p className="text-xs text-gray-400">Ninguno</p>}
                      </div>
                    </div>

                    {/* §N2: Leyenda de índices clínicos con tooltips embebidos */}
                    {preview.poblacion === "infantil" && (
                      <div className="rounded-xl p-3 mb-6 text-xs flex items-center gap-1 flex-wrap"
                        style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                        <I name="info" className="text-base" style={{ color: "#0D9488" }} />
                        <span className="font-bold mr-2">Índices clínicos clave:</span>
                        <GlossaryTerm term="ICV">ICV</GlossaryTerm>
                        <span>·</span>
                        <GlossaryTerm term="IRP">IRP</GlossaryTerm>
                        <span>·</span>
                        <GlossaryTerm term="IMT">IMT</GlossaryTerm>
                        <span>·</span>
                        <GlossaryTerm term="IVP">IVP</GlossaryTerm>
                        <span>·</span>
                        <GlossaryTerm term="CIT">CIT</GlossaryTerm>
                        <span>·</span>
                        <GlossaryTerm term="ICG">ICG</GlossaryTerm>
                        <span className="ml-2 opacity-70">(hover/click para ver definición)</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 mb-3">
                      <Label className="text-xs shrink-0">Plantilla PDF</Label>
                      <Sel
                        value={pdfTemplate}
                        onChange={e => setPdfTemplate(e.target.value)}
                        className="text-xs flex-1"
                        title="Variante del informe (default: Profesional)"
                      >
                        {PDF_TEMPLATES.map(t => (
                          <option key={t.value} value={t.value}>{t.label}</option>
                        ))}
                      </Sel>
                    </div>
                    {/* §M-5: bloqueado si faltan secciones críticas */}
                    <button onClick={() => genPDF(preview.eval_id)}
                      disabled={gen === preview.eval_id || preview.puede_descargar === false}
                      title={preview.puede_descargar === false ? "Resuelve los bloqueos arriba o usa plantilla 'inconcluso'" : ""}
                      className="w-full flex items-center justify-center gap-3 py-5 rounded-2xl text-white font-bold text-lg shadow-2xl active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{
                        background: preview.puede_descargar === false
                          ? "linear-gradient(135deg,#9ca3af,#6b7280)"
                          : "linear-gradient(135deg,#004ac6,#2563eb)",
                        boxShadow: preview.puede_descargar === false ? "none" : "0 20px 40px rgba(0,74,198,0.3)",
                      }}>
                      {gen === preview.eval_id ? (
                        <>
                          <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full" />
                          Generando...
                        </>
                      ) : preview.puede_descargar === false ? (
                        <><I name="block" className="text-2xl" />Bloqueado — resuelve {preview.bloqueos.length} ítem{preview.bloqueos.length === 1 ? "" : "s"}</>
                      ) : (
                        <><I name="picture_as_pdf" className="text-2xl" />Descargar Informe PDF</>
                      )}
                    </button>
                    <div className="grid grid-cols-2 gap-3 mt-3">
                      <button onClick={() => genDOCX(preview.eval_id)} disabled={gen === `docx:${preview.eval_id}`}
                        className="flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm border-2 active:scale-95 transition-all disabled:opacity-60"
                        style={{ borderColor: "#2563eb", color: "#2563eb", background: "#eff6ff" }}>
                        {gen === `docx:${preview.eval_id}` ? (
                          <>
                            <div className="animate-spin w-4 h-4 border-2 border-blue-200 border-t-blue-600 rounded-full" />
                            Generando...
                          </>
                        ) : (
                          <><I name="description" className="text-base" />Word (.docx)</>
                        )}
                      </button>
                      <button onClick={() => genXLSX(preview.eval_id)} disabled={gen === `xlsx:${preview.eval_id}`}
                        className="flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm border-2 active:scale-95 transition-all disabled:opacity-60"
                        style={{ borderColor: "#0d9488", color: "#0d9488", background: "#f0fdfa" }}>
                        {gen === `xlsx:${preview.eval_id}` ? (
                          <>
                            <div className="animate-spin w-4 h-4 border-2 border-teal-200 border-t-teal-600 rounded-full" />
                            Generando...
                          </>
                        ) : (
                          <><I name="grid_on" className="text-base" />Puntajes (.xlsx)</>
                        )}
                      </button>
                    </div>

                    {/* §QW-1: Botón enviar por correo */}
                    <button
                      onClick={() => openEmailModal(preview.eval_id)}
                      disabled={smtpReady === false}
                      title={smtpReady === false ? "Configura SMTP primero (Ajustes → Comunicaciones)" : "Enviar informe por correo"}
                      className="w-full mt-3 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm border-2 active:scale-95 transition-all disabled:opacity-50"
                      style={{ borderColor: "#7c3aed", color: "#7c3aed", background: "#f5f3ff" }}>
                      <I name="mail" className="text-base" />
                      Enviar por correo
                      {smtpReady === false && <span className="text-xs opacity-60 ml-1">(SMTP no configurado)</span>}
                    </button>
                  </Card>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* ── Overlay visor de PDF (fallback pywebview — sustituye descarga nativa) ── */}
      {pdfOverlay && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 9999,
          background: "rgba(0,0,0,0.85)",
          display: "flex", flexDirection: "column",
        }}>
          {/* Barra de herramientas — §QW-1: con Imprimir, Guardar como, Email */}
          <div style={{
            background: "#1e293b", padding: "12px 20px",
            display: "flex", gap: 8, alignItems: "center",
            flexShrink: 0, flexWrap: "wrap",
          }}>
            <I name="picture_as_pdf" style={{ color: "#f87171", fontSize: 22 }} />
            <span style={{ color: "#fff", fontWeight: "bold", flex: 1, minWidth: 200, fontSize: 14 }}>
              {pdfOverlay.filename}
            </span>
            {/* Imprimir */}
            <button
              onClick={printPdfFromOverlay}
              title="Imprimir o guardar como PDF (Ctrl+P)"
              style={{
                padding: "8px 14px", background: "#0d9488", color: "#fff",
                border: "none", borderRadius: 8, fontWeight: "bold",
                cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
              }}>
              <I name="print" style={{ fontSize: 18 }} /> Imprimir
            </button>
            {/* Guardar como (selector de carpeta cuando esté disponible) */}
            <button
              onClick={savePdfAs}
              title="Guardar PDF en una carpeta de tu elección"
              style={{
                padding: "8px 14px", background: "#2563eb", color: "#fff",
                border: "none", borderRadius: 8, fontWeight: "bold",
                cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
              }}>
              <I name="save" style={{ fontSize: 18 }} /> Guardar como…
            </button>
            {/* Enviar por correo */}
            {pdfOverlay.evalId && (
              <button
                onClick={() => openEmailModal(pdfOverlay.evalId)}
                disabled={smtpReady === false}
                title={smtpReady === false ? "Configura SMTP primero" : "Enviar por correo"}
                style={{
                  padding: "8px 14px",
                  background: smtpReady === false ? "#4b5563" : "#7c3aed",
                  color: "#fff",
                  border: "none", borderRadius: 8, fontWeight: "bold",
                  cursor: smtpReady === false ? "not-allowed" : "pointer",
                  display: "flex", alignItems: "center", gap: 6,
                  opacity: smtpReady === false ? 0.6 : 1,
                }}>
                <I name="mail" style={{ fontSize: 18 }} /> Enviar
              </button>
            )}
            <button
              onClick={closePdfOverlay}
              style={{
                padding: "8px 14px", background: "#475569", color: "#fff",
                border: "none", borderRadius: 8, fontWeight: "bold",
                cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
              }}>
              <I name="close" style={{ fontSize: 18 }} /> Cerrar
            </button>
          </div>
          {/* Visor PDF integrado */}
          <iframe
            ref={pdfIframeRef}
            src={pdfOverlay.url}
            title={pdfOverlay.filename}
            style={{ flex: 1, border: "none", background: "#525659" }}
          />
        </div>
      )}

      {/* §QW-1: Modal de envío por correo */}
      {emailModal && (
        <div
          onClick={(e) => { if (e.target === e.currentTarget && !emailSending) closeEmailModal(); }}
          style={{
            position: "fixed", inset: 0, zIndex: 10000,
            background: "rgba(15,23,42,0.6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            padding: 20,
          }}>
          <div style={{
            background: "var(--ns-card)", borderRadius: 16,
            maxWidth: 560, width: "100%", maxHeight: "90vh", overflow: "auto",
            boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
          }}>
            {/* Header */}
            <div style={{
              padding: "20px 24px", borderBottom: "1px solid var(--ns-border)",
              display: "flex", alignItems: "center", gap: 10,
            }}>
              <I name="mail" style={{ color: "#7c3aed", fontSize: 26 }} />
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: 0, fontWeight: 800, fontSize: 18, color: "var(--ns-text)" }}>
                  Enviar informe por correo
                </h3>
                {emailModal.paciente && (
                  <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--ns-muted)" }}>
                    {emailModal.paciente} — {emailModal.fecha}
                  </p>
                )}
              </div>
              <button onClick={closeEmailModal} disabled={emailSending}
                style={{
                  border: "none", background: "transparent",
                  cursor: emailSending ? "not-allowed" : "pointer", padding: 4, opacity: emailSending ? 0.4 : 1,
                }}>
                <I name="close" style={{ fontSize: 22, color: "var(--ns-muted)" }} />
              </button>
            </div>

            {/* Body */}
            <div style={{ padding: 24, display: "flex", flexDirection: "column", gap: 16 }}>
              <div>
                <Label>Destinatario(s) *</Label>
                <Input type="email" multiple
                  value={emailForm.to}
                  onChange={(e) => setEmailForm(f => ({ ...f, to: e.target.value }))}
                  placeholder="paciente@email.com, eps@institucion.co"
                  disabled={emailSending} />
                <p style={{ fontSize: 11, color: "var(--ns-muted)", marginTop: 4 }}>
                  Separa múltiples destinatarios con coma o punto y coma.
                </p>
              </div>
              <div>
                <Label>Copia (CC) — opcional</Label>
                <Input type="text"
                  value={emailForm.cc}
                  onChange={(e) => setEmailForm(f => ({ ...f, cc: e.target.value }))}
                  placeholder="medico.tratante@example.com"
                  disabled={emailSending} />
              </div>
              <div>
                <Label>Tipo de envío</Label>
                <Sel value={emailForm.tipo}
                  onChange={(e) => setEmailForm(f => ({ ...f, tipo: e.target.value }))}
                  disabled={emailSending}>
                  <option value="informe">Informe (al paciente / familia)</option>
                  <option value="remision">Remisión (a colega / médico)</option>
                  <option value="evolucion">Evolución terapéutica</option>
                  <option value="rips">RIPS (EPS / aseguradora)</option>
                  <option value="otro">Otro documento clínico</option>
                </Sel>
              </div>
              <div>
                <Label>Asunto — opcional (deja vacío para usar plantilla)</Label>
                <Input type="text"
                  value={emailForm.subject}
                  onChange={(e) => setEmailForm(f => ({ ...f, subject: e.target.value }))}
                  placeholder="Si vacío: 'Informe de Evaluación Neuropsicológica — …'"
                  disabled={emailSending} />
              </div>
              <div>
                <Label>Mensaje — opcional</Label>
                <Txta rows={5}
                  value={emailForm.body}
                  onChange={(e) => setEmailForm(f => ({ ...f, body: e.target.value }))}
                  placeholder="Si vacío, se usa el cuerpo estándar de la plantilla."
                  disabled={emailSending} />
              </div>
              <label style={{
                display: "flex", alignItems: "center", gap: 8,
                cursor: emailSending ? "not-allowed" : "pointer",
                padding: "10px 12px", background: "var(--ns-subtle)",
                borderRadius: 8,
              }}>
                <input type="checkbox"
                  checked={emailForm.include_pdf}
                  onChange={(e) => setEmailForm(f => ({ ...f, include_pdf: e.target.checked }))}
                  disabled={emailSending} />
                <span style={{ fontSize: 13, color: "var(--ns-text)", fontWeight: 600 }}>
                  Adjuntar PDF del informe
                </span>
              </label>
            </div>

            {/* Footer */}
            <div style={{
              padding: "16px 24px", borderTop: "1px solid var(--ns-border)",
              display: "flex", gap: 10, justifyContent: "flex-end",
            }}>
              <Btn variant="ghost" onClick={closeEmailModal} disabled={emailSending}>
                Cancelar
              </Btn>
              <Btn onClick={sendEmail} disabled={emailSending}
                style={{ background: "#7c3aed", color: "#fff", borderColor: "#7c3aed" }}>
                {emailSending
                  ? <><div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full inline-block mr-2" />Enviando…</>
                  : <><I name="send" className="mr-1.5" />Enviar</>}
              </Btn>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
