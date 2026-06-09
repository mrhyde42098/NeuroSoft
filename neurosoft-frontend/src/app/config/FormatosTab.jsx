/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/FormatosTab.jsx — Formatos administrativos clínicos
 * ───────────────────────────────────────────────────────────────────────
 * Genera PDFs precargados con datos institucionales + paciente +
 * profesional para los formatos del workflow clínico estándar documentados en
 * "Manual de uso formatos":
 *
 *   • Volante de entrega de informe
 *   • Declaración de retiro voluntario
 *   • Declaración de retiro voluntario por motivos de salud
 *   • Autorización de entrega de informes a terceros
 *   • Reporte de evento adverso
 *
 * El render de PDF se hace 100% client-side con jsPDF (lib estándar
 * vendor) — no hay dependencia del backend. Cada formato genera un
 * documento listo para firma manuscrita.
 *
 * Esta primera versión usa generación HTML→print del navegador como
 * fallback hasta integrar jsPDF: abre una ventana imprimible con el
 * formato precargado.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import { Btn, Card, I, Input, Label, MsgBanner, Sel, Txta } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { usePatientsPanel } from "../../hooks/usePatientsPanel.js";
import { PatientSelect } from "../../ui/forms/PatientSelector.jsx";

/* Catálogo de formatos disponibles */
const FORMATS = [
  {
    id: "volante",
    title: "Volante de entrega",
    icon: "receipt_long",
    description: "Comprobante para el usuario sobre cómo y cuándo recibirá el informe.",
    needs: ["paciente"],
  },
  {
    id: "retiro_voluntario",
    title: "Retiro voluntario",
    icon: "exit_to_app",
    description: "Cuando el usuario decide retirarse de la consulta sin completar el proceso.",
    needs: ["paciente", "motivo"],
  },
  {
    id: "retiro_salud",
    title: "Retiro por motivos de salud",
    icon: "medical_information",
    description: "Cuando el paciente presenta complicaciones de salud durante la consulta.",
    needs: ["paciente", "motivo"],
  },
  {
    id: "autorizacion_terceros",
    title: "Autorización entrega a terceros",
    icon: "assignment_ind",
    description: "Cuando el usuario autoriza que el informe se entregue a otra persona.",
    needs: ["paciente", "tercero", "motivo"],
  },
  {
    id: "evento_adverso",
    title: "Reporte de evento adverso",
    icon: "report",
    description: "Documenta cualquier evento que afecte al usuario durante la atención.",
    needs: ["paciente", "motivo"],
  },
  /* §10 — Formatos adicionales */
  {
    id: "consentimiento_rehab",
    title: "Consentimiento terapéutico rehabilitación",
    icon: "assignment_turned_in",
    description: "Consentimiento informado específico para el proceso de rehabilitación cognitiva/neuropsicológica.",
    needs: ["paciente"],
  },
  {
    id: "recibido_informe",
    title: "Recibido informe físico",
    icon: "mail",
    description: "Constancia de entrega presencial del informe en formato impreso al paciente o representante.",
    needs: ["paciente"],
  },
  {
    id: "pqrs",
    title: "PQRS — Peticiones, Quejas, Reclamos y Sugerencias",
    icon: "feedback",
    description: "Formulario de atención a solicitudes, quejas o sugerencias del paciente sobre la atención.",
    needs: ["paciente", "pqrs_tipo", "motivo"],
  },
  {
    id: "reporte_irregular",
    title: "Reporte de situación irregular",
    icon: "warning",
    description: "Documenta situaciones éticas o disciplinarias irregulares durante la atención.",
    needs: ["paciente", "motivo"],
  },
  {
    id: "retiro_datos_investigacion",
    title: "Declaración retiro datos investigación",
    icon: "person_off",
    description: "El participante ejerce derecho de retirar sus datos de un estudio o protocolo de investigación.",
    needs: ["paciente", "motivo"],
  },
];

/* HTML template render (imprimible, listo para firma) */
function buildHTML(formatId, data) {
  const today = new Date().toLocaleDateString("es-CO");
  const inst = data.institucion || {};
  const pac = data.paciente || {};
  const head = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #0d9488;padding-bottom:12px;margin-bottom:24px">
      <div>
        <h2 style="margin:0;color:#0d9488;font-size:18pt">${inst.nombre || "Institución"}</h2>
        <p style="margin:0;font-size:9pt;color:#555">${[inst.nit, inst.direccion, inst.telefono].filter(Boolean).join(" · ")}</p>
      </div>
      <div style="text-align:right;font-size:9pt;color:#555">
        <p style="margin:0"><b>Fecha:</b> ${today}</p>
      </div>
    </div>`;

  const datosPaciente = `
    <div style="background:#f5f5f0;padding:12px;border-radius:8px;margin-bottom:18px;font-size:10pt">
      <p style="margin:0"><b>Paciente:</b> ${pac.nombre_completo || ((pac.primer_nombre || "") + " " + (pac.primer_apellido || "")).trim()}</p>
      <p style="margin:4px 0 0"><b>Documento:</b> ${pac.tipo_documento || ""} ${pac.numero_documento || ""}</p>
      ${pac.fecha_nacimiento ? `<p style="margin:4px 0 0"><b>Fecha de nacimiento:</b> ${pac.fecha_nacimiento}</p>` : ""}
    </div>`;

  const firmaBlock = `
    <div style="margin-top:48px;display:grid;grid-template-columns:1fr 1fr;gap:32px">
      <div style="border-top:1px solid #333;padding-top:6px;text-align:center;font-size:9pt">
        Firma del usuario o acompañante autorizado<br>
        <i style="color:#666">CC __________________</i>
      </div>
      <div style="border-top:1px solid #333;padding-top:6px;text-align:center;font-size:9pt">
        Firma del profesional / Sello<br>
        <i style="color:#666">${data.profesional || "_______________________"}</i>
      </div>
    </div>`;

  let body = "";
  if (formatId === "volante") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Volante de entrega de informe</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.5">
        El informe de evaluación neuropsicológica del paciente arriba identificado
        será entregado en formato PDF al correo electrónico autorizado en el
        consentimiento informado. El plazo máximo es de <b>10 días hábiles</b>
        desde la fecha de la consulta.
      </p>
      <p style="font-size:11pt;line-height:1.5">
        Si el paciente requiere copia impresa, deberá solicitarla a Admisiones
        presentando documento de identidad.
      </p>
      <p style="font-size:10pt;color:#666;margin-top:24px">
        Cualquier inquietud puede comunicarse al ${inst.telefono || "[teléfono]"}
        o ${inst.email || "[email]"}.
      </p>`;
  } else if (formatId === "retiro_voluntario") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Declaración de retiro voluntario</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        Yo, ${pac.nombre_completo || "_____________________________"},
        identificado(a) con ${pac.tipo_documento || "CC"} N° ${pac.numero_documento || "_____________"},
        declaro que en la fecha de hoy <b>${today}</b> he decidido <u>de manera
        libre y voluntaria</u> retirarme del proceso de atención neuropsicológica
        que se estaba realizando en ${inst.nombre || "esta institución"}.
      </p>
      <p style="font-size:11pt;line-height:1.6">
        Manifiesto haber sido informado(a) sobre las implicaciones de no completar
        el proceso, incluyendo la imposibilidad de emitir un informe diagnóstico
        concluyente.
      </p>
      ${data.motivo ? `<p style="font-size:11pt;line-height:1.6"><b>Motivo:</b> ${data.motivo}</p>` : ""}
      ${firmaBlock}`;
  } else if (formatId === "retiro_salud") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Retiro por motivos de salud</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        En la fecha de hoy <b>${today}</b>, durante la consulta de evaluación
        neuropsicológica, el paciente arriba identificado presentó condiciones
        de salud que impidieron continuar con el proceso de evaluación.
      </p>
      ${data.motivo ? `<p style="font-size:11pt;line-height:1.6"><b>Condición presentada:</b> ${data.motivo}</p>` : ""}
      <p style="font-size:11pt;line-height:1.6">
        Se acordó suspender la consulta y se informa al paciente y/o
        acompañante sobre la necesidad de reagendar una nueva cita una vez
        superada la condición.
      </p>
      ${firmaBlock}`;
  } else if (formatId === "autorizacion_terceros") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Autorización de entrega a terceros</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        Yo, ${pac.nombre_completo || "_____________________________"},
        identificado(a) con ${pac.tipo_documento || "CC"} N° ${pac.numero_documento || "_____________"},
        en mi calidad de paciente o representante legal, <b>autorizo expresamente</b>
        a ${data.tercero || "_____________________________"} (${data.tercero_doc || "CC _____________"})
        para recibir el informe de evaluación neuropsicológica en mi nombre.
      </p>
      ${data.motivo ? `<p style="font-size:11pt;line-height:1.6"><b>Motivo de la autorización:</b> ${data.motivo}</p>` : ""}
      <p style="font-size:11pt;line-height:1.6">
        La presente autorización es individual y se otorga únicamente para el
        evento de evaluación realizado en ${inst.nombre || "esta institución"}
        en la fecha indicada.
      </p>
      ${firmaBlock}`;
  } else if (formatId === "evento_adverso") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Reporte de evento adverso</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        Durante la atención del paciente arriba identificado, en la fecha
        <b>${today}</b>, se presentó la siguiente situación que afectó su
        proceso o bienestar:
      </p>
      <div style="border:1px solid #ddd;border-radius:8px;padding:14px;background:#fafafa;font-size:11pt;line-height:1.6;min-height:120px">
        ${(data.motivo || "").replace(/\n/g, "<br>")}
      </div>
      <p style="font-size:10pt;color:#666;margin-top:12px">
        Este reporte se diligencia inmediatamente posterior al evento por parte
        de la persona implicada y se envía a
        atencionusuario@${(inst.email || "@").split("@")[1] || "institucion.com"}
        para análisis del Comité de Seguridad del Paciente.
      </p>
      ${firmaBlock}`;
  }

  /* ── §10 Nuevos formatos ── */
  if (formatId === "consentimiento_rehab") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Consentimiento informado — Rehabilitación Neuropsicológica</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        Yo, ${pac.nombre_completo || "_____________________________"},
        identificado(a) con ${pac.tipo_documento || "CC"} N° ${pac.numero_documento || "_____________"},
        habiendo recibido información suficiente sobre los objetivos, metodología, duración y posibles
        riesgos del proceso de <b>rehabilitación neuropsicológica</b>, manifiesto:
      </p>
      <ol style="font-size:11pt;line-height:1.8;margin:12px 0 0 18px">
        <li>He comprendido la naturaleza y el propósito del tratamiento de rehabilitación cognitiva.</li>
        <li>He recibido explicación sobre las sesiones, frecuencia y duración estimada del proceso.</li>
        <li>Conozco que puedo retirarme en cualquier momento sin que esto afecte mi atención médica.</li>
        <li>Autorizo el uso de mis datos con fines clínicos y, si aplica, con fines de investigación anonimizada.</li>
        <li>He podido hacer preguntas y mis dudas han sido resueltas satisfactoriamente.</li>
      </ol>
      ${firmaBlock}`;
  } else if (formatId === "recibido_informe") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Constancia de recibido — Informe Neuropsicológico</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        Por medio de la presente hago constar que el día <b>${today}</b> recibí de forma física
        y a entera satisfacción el informe de evaluación neuropsicológica elaborado por
        ${data.profesional || "${inst.nombre || 'la institución'}"}, correspondiente al proceso de atención
        realizado en ${inst.nombre || "esta institución"}.
      </p>
      <p style="font-size:11pt;line-height:1.6">
        El documento recibido consta de _____ folios y cuenta con firma y sello del profesional responsable.
      </p>
      ${firmaBlock}`;
  } else if (formatId === "pqrs") {
    const tipoLabel = data.pqrs_tipo || "Petición";
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">PQRS — ${tipoLabel}</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        <b>Tipo de solicitud:</b> ${tipoLabel} &nbsp;|&nbsp; <b>Radicado:</b> PQRS-${today.replace(/\//g,"")}
      </p>
      <div style="border:1px solid #ddd;border-radius:8px;padding:14px;background:#fafafa;font-size:11pt;line-height:1.6;min-height:100px">
        ${(data.motivo || "").replace(/\n/g, "<br>") || "Sin descripción"}
      </div>
      <p style="font-size:10pt;color:#666;margin-top:12px">
        De acuerdo con la Ley 1755 de 2015, esta solicitud será atendida en un plazo no mayor a
        <b>15 días hábiles</b>. Será enviada respuesta al correo o dirección registrados en el expediente del paciente.
      </p>
      ${firmaBlock}`;
  } else if (formatId === "reporte_irregular") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Reporte de situación irregular</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        En la fecha de hoy <b>${today}</b>, quien suscribe reporta la siguiente situación
        que puede constituir una irregularidad ética, disciplinaria o institucional durante
        la atención al paciente arriba identificado:
      </p>
      <div style="border:1px solid #f87171;border-radius:8px;padding:14px;background:#fef2f2;font-size:11pt;line-height:1.6;min-height:120px">
        ${(data.motivo || "").replace(/\n/g, "<br>") || "[Descripción detallada de la situación]"}
      </div>
      <p style="font-size:10pt;color:#666;margin-top:12px">
        Este reporte se remite al Comité de Ética institucional para su análisis y seguimiento.
        Radicado: IRR-${today.replace(/\//g,"")}.
      </p>
      ${firmaBlock}`;
  } else if (formatId === "retiro_datos_investigacion") {
    body = `
      <h1 style="text-align:center;font-size:14pt;margin:0 0 24px">Declaración de retiro de datos de investigación</h1>
      ${datosPaciente}
      <p style="font-size:11pt;line-height:1.6">
        Yo, ${pac.nombre_completo || "_____________________________"},
        identificado(a) con ${pac.tipo_documento || "CC"} N° ${pac.numero_documento || "_____________"},
        en ejercicio de mi derecho de retiro consagrado en la <b>Ley 1581 de 2012</b> (Ley de Protección
        de Datos Personales) y en los principios éticos de la investigación con seres humanos,
        declaro que <u>retiro mi autorización</u> para el uso de mis datos personales y clínicos
        en el(los) estudio(s) de investigación en que participé como sujeto de información.
      </p>
      ${data.motivo ? `<p style="font-size:11pt;line-height:1.6"><b>Estudio/protocolo al que aplica:</b> ${data.motivo}</p>` : ""}
      <p style="font-size:11pt;line-height:1.6">
        Entiendo que este retiro no afecta los datos ya recolectados antes de esta fecha ni
        los resultados publicados de manera anonimizada previo a este aviso.
      </p>
      ${firmaBlock}`;
  }

  return `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
    <title>${FORMATS.find(f => f.id === formatId)?.title || "Formato"} — ${pac.nombre_completo || ""}</title>
    <style>
      @page { size: letter; margin: 22mm; }
      body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif; color: #222; line-height: 1.4; }
      h1, h2 { font-weight: 700; }
      @media print { .no-print { display: none } button { display: none } }
    </style>
    </head><body>
    ${head}
    ${body}
    <div class="no-print" style="margin-top:36px;text-align:center">
      <button onclick="window.print()" style="padding:10px 24px;background:#0d9488;color:#fff;border:0;border-radius:8px;font-weight:bold;cursor:pointer">
        Imprimir / Guardar PDF
      </button>
    </div>
    </body></html>`;
}

export default function FormatosTab() {
  const { patients, loading: patientsLoading } = usePatientsPanel();
  const [patId, setPatId] = useState("");
  const [profs, setProfs] = useState([]);
  const [profId, setProfId] = useState("");
  const [inst, setInst] = useState({});
  const [selectedFormat, setSelectedFormat] = useState(null);
  const [extra, setExtra] = useState({});
  const [msg, setMsg] = useState("");
  /* Vista previa in-page para pywebview (window.open bloqueado) */
  const [previewHtml, setPreviewHtml] = useState(null);
  const iframeRef = React.useRef(null);

  useEffect(() => {
    Promise.all([
      api.get("/api/v1/config/profesionales").catch(() => []),
      api.get("/api/v1/config/").catch(() => null),
    ]).then(([ps, cfg]) => {
      setProfs(ps || []);
      if (cfg?.institucion) setInst(cfg.institucion);
    });
  }, []);

  const generate = (fmt) => {
    if (!patId) {
      setMsg("Seleccione un paciente.");
      return;
    }
    const pac = patients.find((p) => p.id === patId);
    if (!pac) {
      setMsg("Paciente no encontrado.");
      return;
    }
    const prof = profs.find((p) => p.id === profId);
    const data = {
      institucion: inst,
      paciente: pac,
      profesional: prof?.nombre_completo || "",
      ...extra,
    };
    const html = buildHTML(fmt.id, data);
    /* Intentar window.open (funciona en navegador web estándar).
     * En pywebview los popups están bloqueados → fallback a overlay in-page. */
    const w = window.open("", "_blank", "width=900,height=1100");
    if (w) {
      w.document.write(html);
      w.document.close();
      setMsg("ok");
    } else {
      setPreviewHtml(html);
    }
  };

  return (
    <>
    <Card className="p-8 space-y-5">
      <div>
        <h3 className="text-lg font-bold flex items-center gap-2">
          <I name="description" style={{ color: TEAL }} />Formatos administrativos clínicos
        </h3>
        <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
          Genera documentos precargados con datos institucionales + paciente listos para firmar.
        </p>
      </div>

      <MsgBanner msg={msg === "ok" ? "ok" : msg} onDismiss={msg && msg !== "ok" ? () => setMsg("") : null} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PatientSelect
          patients={patients}
          loading={patientsLoading}
          label="Paciente"
          value={patId}
          onChange={setPatId}
          placeholder="— Seleccione —"
        />
        <div>
          <Label>Profesional firmante</Label>
          <Sel value={profId} onChange={(e) => setProfId(e.target.value)}>
            <option value="">— Sin profesional asignado —</option>
            {profs.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre_completo}</option>
            ))}
          </Sel>
        </div>
      </div>

      {/* Selector de formato */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {FORMATS.map((f) => (
          <button key={f.id}
            onClick={() => { setSelectedFormat(f); setExtra({}); }}
            className={`p-4 rounded-xl border-2 text-left transition-all ${selectedFormat?.id === f.id ? "shadow-lg" : "hover:border-teal-300"}`}
            style={{
              borderColor: selectedFormat?.id === f.id ? TEAL : "var(--ns-card-b)",
              background: selectedFormat?.id === f.id ? `${TEAL}08` : "var(--ns-card)",
            }}>
            <div className="flex items-center gap-3">
              <I name={f.icon} className="text-2xl" style={{ color: TEAL }} />
              <div className="flex-1">
                <p className="font-bold text-sm">{f.title}</p>
                <p className="text-[10px] mt-0.5" style={{ color: "var(--ns-muted)" }}>{f.description}</p>
              </div>
              {selectedFormat?.id === f.id && <I name="check_circle" fill style={{ color: TEAL }} />}
            </div>
          </button>
        ))}
      </div>

      {/* Campos adicionales según el formato */}
      {selectedFormat && (
        <div className="p-4 rounded-xl space-y-3" style={{ background: "var(--ns-subtle)" }}>
          <p className="text-sm font-bold">{selectedFormat.title}</p>
          {selectedFormat.needs.includes("pqrs_tipo") && (
            <div>
              <Label>Tipo de solicitud</Label>
              <Sel value={extra.pqrs_tipo||"Petición"} onChange={e=>setExtra(x=>({...x,pqrs_tipo:e.target.value}))}>
                {["Petición","Queja","Reclamo","Sugerencia","Felicitación"].map(t=><option key={t} value={t}>{t}</option>)}
              </Sel>
            </div>
          )}
          {selectedFormat.needs.includes("motivo") && (
            <div>
              <Label>{selectedFormat.id === "evento_adverso" ? "Descripción del evento" : selectedFormat.id === "pqrs" ? "Descripción detallada" : selectedFormat.id === "retiro_datos_investigacion" ? "Estudio/protocolo al que aplica" : "Motivo"}</Label>
              <Txta value={extra.motivo || ""}
                onChange={(e) => setExtra((x) => ({ ...x, motivo: e.target.value }))}
                placeholder={selectedFormat.id === "evento_adverso"
                  ? "Describa con detalle qué sucedió, hora, personas involucradas, acciones tomadas..."
                  : "Indique el motivo (opcional)..."} />
            </div>
          )}
          {selectedFormat.needs.includes("tercero") && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <Label>Nombre del tercero autorizado</Label>
                <Input value={extra.tercero || ""}
                  onChange={(e) => setExtra((x) => ({ ...x, tercero: e.target.value }))}
                  placeholder="Nombre completo" />
              </div>
              <div>
                <Label>Documento del tercero</Label>
                <Input value={extra.tercero_doc || ""}
                  onChange={(e) => setExtra((x) => ({ ...x, tercero_doc: e.target.value }))}
                  placeholder="CC 12345" />
              </div>
            </div>
          )}
          <div className="flex justify-end pt-1">
            <Btn onClick={() => generate(selectedFormat)} disabled={!patId}>
              <I name="print" className="text-sm" />Generar e imprimir
            </Btn>
          </div>
        </div>
      )}

      <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
        Los formatos se abren listos para imprimir o guardar como PDF desde el visor integrado.
      </p>
    </Card>

    {/* ── Overlay in-page para pywebview (fallback cuando window.open devuelve null) ── */}
    {previewHtml && (
      <div style={{
        position: "fixed", inset: 0, zIndex: 9999,
        background: "rgba(0,0,0,0.7)",
        display: "flex", flexDirection: "column",
      }}>
        {/* Barra de herramientas */}
        <div style={{
          background: "#1e293b", padding: "12px 20px",
          display: "flex", gap: 12, alignItems: "center",
          flexShrink: 0,
        }}>
          <button
            onClick={() => iframeRef.current?.contentWindow?.print()}
            style={{
              padding: "8px 20px", background: TEAL, color: "#fff",
              border: "none", borderRadius: 8, fontWeight: "bold",
              cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
            }}>
            <I name="print" style={{ fontSize: 18 }} /> Imprimir / PDF
          </button>
          <button
            onClick={() => setPreviewHtml(null)}
            style={{
              padding: "8px 20px", background: "#475569", color: "#fff",
              border: "none", borderRadius: 8, fontWeight: "bold",
              cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
            }}>
            <I name="close" style={{ fontSize: 18 }} /> Cerrar
          </button>
          <span style={{ color: "#94a3b8", fontSize: 12, marginLeft: "auto" }}>
            Use "Imprimir / PDF" → "Guardar como PDF" para exportar el documento
          </span>
        </div>
        {/* Vista previa del formato */}
        <iframe
          ref={iframeRef}
          srcDoc={previewHtml}
          title="Vista previa del formato"
          style={{ flex: 1, border: "none", background: "white" }}
        />
      </div>
    )}
  </>
  );
}
