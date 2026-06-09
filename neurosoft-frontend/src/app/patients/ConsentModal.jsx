/* ═══════════════════════════════════════════════════════════════════════
 * ConsentModal — Consentimientos informados
 * Firma digital, imprimir PDF, enviar por correo (SMTP en Config).
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Btn, I, Input, Label, Sel } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { CONSENT_LABELS } from "../../data/ui.js";
import SignatureCanvas from "../evaluation/SignatureCanvas.jsx";
import SectionCard from "../../ui/SectionCard.jsx";

export default function ConsentModal({ patientId, patientName, patientEmail = "", onClose, onAllSigned }) {
  const [pendientes, setPendientes] = useState([]);
  const [ld, setLd] = useState(true);
  const [firmados, setFirmados] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [textoActual, setTextoActual] = useState(null);
  const [firma, setFirma] = useState("");
  const [nombreFirmante, setNombreFirmante] = useState("");
  const [relacion, setRelacion] = useState("titular");
  const [docFirmante, setDocFirmante] = useState("");
  const [aceptado, setAceptado] = useState(false);
  const [saving, setSaving] = useState(false);
  const [modoFirma, setModoFirma] = useState("digital");
  const [emailTo, setEmailTo] = useState(patientEmail || "");
  const [sendingMail, setSendingMail] = useState(false);
  const [pdfOverlay, setPdfOverlay] = useState(null);
  const toast = useToast();

  const closePdfOverlay = () => {
    if (pdfOverlay?.url) URL.revokeObjectURL(pdfOverlay.url);
    setPdfOverlay(null);
  };

  const load = async () => {
    setLd(true);
    try {
      const [p, f] = await Promise.all([
        api.get(`/api/v1/consentimientos/pendientes/${patientId}`).catch(() => ({})),
        api.get(`/api/v1/consentimientos/?patient_id=${patientId}`).catch(() => []),
      ]);
      const pend = Array.isArray(p) ? p : (p?.pendientes ?? []);
      setPendientes(pend);
      setFirmados(f || []);
      if (pend.length > 0) {
        const t = await api.get(`/api/v1/consentimientos/textos/${pend[0]}`).catch(() => null);
        setTextoActual(t);
      }
    } catch (e) {
      toast.error(_parseError(e));
    }
    setLd(false);
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, [patientId]);

  const cargarTipo = async (tipo) => {
    const t = await api.get(`/api/v1/consentimientos/textos/${tipo}`).catch(() => null);
    setTextoActual(t);
    setFirma("");
    setNombreFirmante("");
    setDocFirmante("");
    setAceptado(false);
    setRelacion("titular");
  };

  const tipoActual = pendientes[currentIdx];

  const abrirPdf = async (url, filename = "consentimiento.pdf") => {
    try {
      const blob = await api.blob(url, "GET");
      const u = URL.createObjectURL(blob);
      /* En pywebview window.open(blob) falla — visor in-app como InformesPage. */
      setPdfOverlay({ url: u, filename, blob });
    } catch (e) {
      toast.error(_parseError(e));
    }
  };

  const imprimirPlantilla = () => {
    if (!tipoActual) return;
    abrirPdf(`/api/v1/consentimientos/pdf/plantilla/${tipoActual}?patient_id=${patientId}`);
  };

  const imprimirFirmado = (id) => {
    abrirPdf(`/api/v1/consentimientos/${id}/pdf`);
  };

  const enviarEmail = async (consentimientoId = null) => {
    const tipo = consentimientoId ? firmados.find((x) => x.id === consentimientoId)?.tipo : tipoActual;
    if (!tipo) return;
    const to = emailTo.trim();
    if (!to) {
      toast.error("Indique un correo destino");
      return;
    }
    setSendingMail(true);
    try {
      const r = await api.post("/api/v1/consentimientos/enviar-email", {
        patient_id: patientId,
        tipo,
        to: [to],
        consentimiento_id: consentimientoId,
      });
      if (r.ok) toast.success("Consentimiento enviado por correo");
      else toast.error(r.error || "No se pudo enviar el correo");
    } catch (e) {
      toast.error(_parseError(e));
    }
    setSendingMail(false);
  };

  const firmar = async () => {
    if (!firma || !nombreFirmante || !docFirmante || !aceptado) {
      toast.error("Complete nombre, documento, firma y marque la casilla");
      return;
    }
    setSaving(true);
    try {
      if (modoFirma === "fisico") {
        await api.post("/api/v1/consentimientos/fisico", {
          patient_id: patientId,
          tipo: tipoActual,
          nombre_firmante: nombreFirmante,
          relacion_firmante: relacion,
          documento_firmante: docFirmante,
        });
      } else {
        await api.post("/api/v1/consentimientos/", {
          patient_id: patientId,
          tipo: tipoActual,
          version_texto: textoActual.version,
          texto_completo: textoActual.texto,
          aceptado: true,
          firma_base64: firma,
          nombre_firmante: nombreFirmante,
          relacion_firmante: relacion,
          documento_firmante: docFirmante,
          modo_firma: "digital",
        });
      }
      toast.success("Consentimiento firmado");
      const nuevosPend = pendientes.filter((_, i) => i !== currentIdx);
      setPendientes(nuevosPend);
      if (nuevosPend.length === 0) {
        onAllSigned?.();
        onClose();
      } else {
        setCurrentIdx(0);
        await cargarTipo(nuevosPend[0]);
      }
      load();
    } catch (e) {
      toast.error(_parseError(e));
    }
    setSaving(false);
  };

  const revocar = async (id) => {
    const motivo = prompt("Motivo de la revocación:");
    if (!motivo) return;
    try {
      await api.patch(`/api/v1/consentimientos/${id}/revocar`, { motivo });
      toast.success("Consentimiento revocado");
      load();
    } catch (e) {
      toast.error(_parseError(e));
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()} style={{ background: "var(--ns-card)" }}>
        <div className="p-5 border-b flex items-center justify-between" style={{ borderColor: "var(--ns-card-b)" }}>
          <div>
            <h3 className="text-lg font-bold flex items-center gap-2">
              <I name="verified_user" style={{ color: TEAL }} />Consentimientos informados
            </h3>
            <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
              Paciente: <b>{patientName}</b> · Imprimir o enviar por correo (SMTP en Config)
            </p>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100" aria-label="Cerrar">
            <I name="close" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {ld ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full" />
            </div>
          ) : (
            <div className="space-y-6">
              {pendientes.length > 0 && !textoActual && (
                <SectionCard title="Texto no disponible" icon="error" eyebrow="Error de carga">
                  <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
                    No se pudo cargar el texto del consentimiento <b>{tipoActual}</b>.
                    Verifique la conexión con el servidor o contacte al administrador.
                  </p>
                  <div className="flex justify-end gap-2 mt-4">
                    <Btn v="outline" onClick={onClose}>Más tarde</Btn>
                    <Btn onClick={() => cargarTipo(tipoActual)}>Reintentar</Btn>
                  </div>
                </SectionCard>
              )}
              {pendientes.length > 0 && textoActual && (
                <SectionCard
                  title={CONSENT_LABELS[tipoActual]?.titulo || tipoActual}
                  icon="draw"
                  eyebrow={`${pendientes.length} pendiente(s)`}
                  subtitle={CONSENT_LABELS[tipoActual]?.desc}
                  headerRight={
                    pendientes.length > 1 ? (
                      <div className="flex gap-1">
                        {pendientes.map((t, i) => (
                          <button key={t} type="button" onClick={() => { setCurrentIdx(i); cargarTipo(t); }}
                            className="text-[10px] px-2 py-1 rounded"
                            style={i === currentIdx ? { background: TEAL, color: "white" } : { background: "var(--ns-subtle)" }}>
                            {i + 1}
                          </button>
                        ))}
                      </div>
                    ) : null
                  }
                >
                  <div className="p-4 rounded-lg max-h-52 overflow-auto text-xs leading-relaxed whitespace-pre-wrap mb-4"
                    style={{ background: "var(--ns-subtle)", border: "1px solid var(--ns-card-b)" }}>
                    {textoActual.texto}
                  </div>
                  <p className="text-[10px] mb-3" style={{ color: "var(--ns-muted)" }}>Versión {textoActual.version}</p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    <Btn v="outline" onClick={imprimirPlantilla}>
                      <I name="print" className="text-sm" />Imprimir para firmar
                    </Btn>
                    <div className="flex items-center gap-2 flex-1 min-w-[200px]">
                      <Input value={emailTo} onChange={(e) => setEmailTo(e.target.value)}
                        placeholder="correo@paciente.com" className="text-xs flex-1" />
                      <Btn v="outline" onClick={() => enviarEmail()} disabled={sendingMail}>
                        <I name="mail" className="text-sm" />{sendingMail ? "Enviando…" : "Enviar"}
                      </Btn>
                    </div>
                  </div>

                  <div className="flex gap-2 mb-3">
                    <button type="button" onClick={() => setModoFirma("digital")} className="text-xs px-3 py-1.5 rounded-lg font-bold border" style={modoFirma === "digital" ? { background: TEAL, color: "#fff", borderColor: TEAL } : { borderColor: "var(--ns-card-b)" }}>Firma digital</button>
                    <button type="button" onClick={() => setModoFirma("fisico")} className="text-xs px-3 py-1.5 rounded-lg font-bold border" style={modoFirma === "fisico" ? { background: TEAL, color: "#fff", borderColor: TEAL } : { borderColor: "var(--ns-card-b)" }}>Firmado en papel</button>
                  </div>
                  {modoFirma === "fisico" && (
                    <p className="text-xs mb-3 p-2 rounded-lg" style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                      Marque como diligenciado en consultorio. Deberá adjuntar el escaneado antes de emitir el informe Pro.
                    </p>
                  )}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs">Nombre del firmante *</Label>
                      <Input value={nombreFirmante} onChange={(e) => setNombreFirmante(e.target.value)} placeholder="Nombre completo" />
                    </div>
                    <div>
                      <Label className="text-xs">Documento *</Label>
                      <Input value={docFirmante} onChange={(e) => setDocFirmante(e.target.value)} placeholder="CC / TI / CE" />
                    </div>
                    <div>
                      <Label className="text-xs">Relación con el paciente</Label>
                      <Sel value={relacion} onChange={(e) => setRelacion(e.target.value)}>
                        <option value="titular">Titular (paciente mayor de edad)</option>
                        <option value="padre">Padre</option>
                        <option value="madre">Madre</option>
                        <option value="tutor_legal">Tutor legal</option>
                        <option value="representante">Representante legal</option>
                        <option value="otro">Otro familiar</option>
                      </Sel>
                    </div>
                    {modoFirma === "digital" && (
                      <div className="col-span-2">
                        <Label className="text-xs">Firma manuscrita *</Label>
                        <SignatureCanvas value={firma} onChange={setFirma} />
                      </div>
                    )}
                    <label className="col-span-2 flex items-start gap-2 cursor-pointer">
                      <input type="checkbox" checked={aceptado} onChange={(e) => setAceptado(e.target.checked)} className="w-4 h-4 mt-0.5" />
                      <span className="text-xs">
                        He leído y entiendo el contenido. Acepto voluntariamente y autorizo el tratamiento de datos (Ley 1581/2012).
                      </span>
                    </label>
                  </div>
                  <div className="flex justify-end gap-2 mt-4">
                    <Btn v="outline" onClick={onClose}>Más tarde</Btn>
                    <Btn onClick={firmar} disabled={saving || !nombreFirmante || !docFirmante || !aceptado || (modoFirma === "digital" && !firma)}>
                      <I name="draw" className="text-sm" />{saving ? "Guardando…" : (modoFirma === "fisico" ? "Marcar diligenciado" : "Firmar digitalmente")}
                    </Btn>
                  </div>
                </SectionCard>
              )}

              <div>
                <p className="text-sm font-bold mb-3 flex items-center gap-2">
                  <I name="task_alt" style={{ color: "#059669" }} />
                  Firmados ({firmados.filter((f) => !f.fecha_revocado).length})
                </p>
                {firmados.length === 0 ? (
                  <p className="text-xs text-center py-6" style={{ color: "var(--ns-muted)" }}>Sin consentimientos previos</p>
                ) : (
                  <div className="space-y-2">
                    {firmados.map((f) => {
                      const revocado = !!f.fecha_revocado;
                      return (
                        <div key={f.id} className="p-3 rounded-lg border flex items-center justify-between gap-2 flex-wrap"
                          style={{ borderColor: "var(--ns-card-b)", background: revocado ? "#fef2f2" : "var(--ns-subtle)", opacity: revocado ? 0.6 : 1 }}>
                          <div className="flex-1 min-w-[180px]">
                            <p className="text-xs font-bold">
                              {CONSENT_LABELS[f.tipo]?.titulo || f.tipo}
                              <span className="font-normal text-[10px]" style={{ color: "var(--ns-muted)" }}> v{f.version_texto}</span>
                            </p>
                            <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                              {f.nombre_firmante} ({f.relacion_firmante}) · {f.documento_firmante}
                            </p>
                            <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                              Firmado: {f.fecha_firma ? new Date(f.fecha_firma).toLocaleDateString("es-CO") : "—"}
                            </p>
                            {revocado && (
                              <p className="text-[10px] text-red-600 font-bold mt-1">
                                REVOCADO el {new Date(f.fecha_revocado).toLocaleDateString("es-CO")}
                              </p>
                            )}
                          </div>
                          {!revocado && (
                            <div className="flex gap-1 shrink-0">
                              <button type="button" onClick={() => imprimirFirmado(f.id)}
                                className="text-xs px-2 py-1 rounded border" style={{ borderColor: TEAL, color: TEAL }} title="Imprimir PDF">
                                <I name="print" className="text-sm" />
                              </button>
                              <button type="button" onClick={() => enviarEmail(f.id)}
                                className="text-xs px-2 py-1 rounded border" style={{ borderColor: TEAL, color: TEAL }} title="Enviar copia por correo">
                                <I name="mail" className="text-sm" />
                              </button>
                              <button type="button" onClick={() => revocar(f.id)}
                                className="text-xs p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-600" title="Revocar">
                                <I name="block" className="text-base" />
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {pdfOverlay && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 10050,
          background: "rgba(0,0,0,0.85)",
          display: "flex", flexDirection: "column",
        }}>
          <div style={{
            background: "#1e293b", padding: "12px 20px",
            display: "flex", gap: 8, alignItems: "center", flexShrink: 0,
          }}>
            <I name="picture_as_pdf" style={{ color: "#f87171", fontSize: 22 }} />
            <span style={{ color: "#fff", fontWeight: "bold", flex: 1, fontSize: 14 }}>
              {pdfOverlay.filename}
            </span>
            <button
              type="button"
              onClick={() => {
                const w = window.open(pdfOverlay.url, "_blank");
                if (!w) {
                  const iframe = document.createElement("iframe");
                  iframe.style.display = "none";
                  iframe.src = pdfOverlay.url;
                  document.body.appendChild(iframe);
                  iframe.contentWindow?.print();
                }
              }}
              style={{
                padding: "8px 14px", background: "#0d9488", color: "#fff",
                border: "none", borderRadius: 8, fontWeight: "bold", cursor: "pointer",
              }}
            >
              <I name="print" style={{ fontSize: 18 }} /> Imprimir
            </button>
            <button
              type="button"
              onClick={closePdfOverlay}
              style={{
                padding: "8px 14px", background: "#475569", color: "#fff",
                border: "none", borderRadius: 8, fontWeight: "bold", cursor: "pointer",
              }}
            >
              <I name="close" style={{ fontSize: 18 }} /> Cerrar
            </button>
          </div>
          <iframe
            src={pdfOverlay.url}
            title={pdfOverlay.filename}
            style={{ flex: 1, border: "none", background: "#525659" }}
          />
        </div>
      )}
    </div>
  );
}
