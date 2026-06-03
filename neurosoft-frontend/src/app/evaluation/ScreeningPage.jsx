/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/ScreeningPage.jsx — Screening cognitivo y emocional
 * ───────────────────────────────────────────────────────────────────────
 * Soporta dos tipos de instrumento:
 *   • binary_domains: MMSE, MoCA, ACE-III (0/1 por dominios).
 *   • likert_flat:    PHQ-9, GAD-7 (0-3 escala Likert, lista plana).
 *
 * Calcula total + interpretación (cutoff único o severidad por rangos),
 * detecta red-flags (p.e. ítem 9 PHQ-9 = ideación suicida) y guarda como
 * observación clínica del paciente.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useState } from "react";
import { api, _parseError, exportCSV } from "../../api/client.js";
import {
  Btn, Card, I, Label, MsgBanner, Sel, TopBar, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { SCREENING_FORMS } from "../../data/screening.js";
import { useToast } from "../../contexts.jsx";
import ScreeningWizard from "./ScreeningWizard.jsx";

function scoreLikertItem(form, scores, i) {
  /* §M2-fix: parseInt SIEMPRE con radix 10 — Likert es 0-N, sin ambigüedad. */
  const v = parseInt(scores[`item_${i}`], 10);
  if (Number.isNaN(v)) return null;
  const max = form.scaleLabels.length - 1;
  return (form.reverseItems || []).includes(i) ? max - v : v;
}

/* ─── Calcula total + interpretación según tipo de instrumento ─── */
function computeResult(form, scores) {
  if (form.kind === "likert_flat") {
    let total = 0;
    form.items.forEach((_, i) => {
      const v = scoreLikertItem(form, scores, i);
      if (v != null) total += v;
    });
    const sev = form.severity.find((s) => total <= s.max) ||
                form.severity[form.severity.length - 1];
    /* Red flags: ítems específicos con respuesta ≥1 */
    const redFlags = (form.redFlagItems || [])
      .filter((i) => parseInt(scores[`item_${i}`] || 0, 10) >= 1);
    /* Subescalas: calcular puntaje parcial por sección */
    const subescalaScores = form.subescalas
      ? (() => {
          const maxPerItem = form.scaleLabels.length - 1;
          let offset = 0;
          return form.subescalas.map((se) => {
            let seTotal = 0;
            for (let i = offset; i < offset + se.items; i++) {
              const v = scoreLikertItem(form, scores, i);
              if (v != null) seTotal += v;
            }
            offset += se.items;
            return {
              nombre:      se.nombre,
              descripcion: se.descripcion || "",
              total:       seTotal,
              max:         se.items * maxPerItem,
              cutoff:      se.cutoff_propio ?? null,
            };
          });
        })()
      : [];
    return {
      total,
      label: sev.label,
      color: sev.color,
      cutoff: form.clinicalCutoff,
      aboveCutoff: total >= form.clinicalCutoff,
      redFlags,
      subescalaScores,
    };
  }
  /* binary_domains */
  const total = form.domains.reduce(
    (s, d) => s + d.items.reduce(
      (s2, _, i) => s2 + (parseInt(scores[`${d.name}_${i}`], 10) || 0),
      0,
    ),
    0,
  );
  const label =
    total >= form.cutoff ? "Normal"
    : total >= form.cutoff - 4 ? "Deterioro Leve"
    : total >= form.cutoff - 10 ? "Deterioro Moderado"
    : "Deterioro Severo";
  const color =
    label === "Normal" ? TEAL
    : label === "Deterioro Leve" ? "#f59e0b"
    : label === "Deterioro Moderado" ? "#ea580c"
    : "#dc2626";
  return { total, label, color, cutoff: form.cutoff, aboveCutoff: false, redFlags: [] };
}

export default function ScreeningPage() {
  const toast = useToast();
  const [test, setTest] = useState("MMSE");
  const [patId, setPatId] = useState("");
  const [patients, setPatients] = useState([]);
  const [scores, setScores] = useState({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [obs, setObs] = useState("");

  useEffect(() => {
    api.get("/api/v1/patients/panel")
      .then((d) => setPatients(d.pacientes || d || []))
      .catch(() => toast.error("Error cargando pacientes"));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const form = SCREENING_FORMS[test];
  const result = useMemo(() => computeResult(form, scores), [form, scores]);

  const setBin = (d, i, v) => setScores((s) => ({ ...s, [`${d}_${i}`]: v }));
  const setLik = (i, v) => setScores((s) => ({ ...s, [`item_${i}`]: v }));

  const domainTotal = (d) =>
    d.items.reduce((s, _, i) => s + (parseInt(scores[`${d.name}_${i}`], 10) || 0), 0);

  const save = async () => {
    if (!patId) { setMsg("Seleccione un paciente"); return; }
    setSaving(true);
    try {
      const flag = result.redFlags.length > 0
        ? `\n⚠ ${form.redFlagMessage}`
        : "";
      const cutoffLine = form.kind === "likert_flat"
        ? `${form.abbr}: ${result.total}/${form.maxScore} — ${result.label}` +
          (result.aboveCutoff ? ` (≥ corte clínico ${form.clinicalCutoff})` : "")
        : `${form.abbr}: ${result.total}/${form.maxScore} — ${result.label}`;
      const reverseLine = form.reverseItems?.length
        ? `\nItems inversos corregidos automaticamente: ${form.reverseItems.length}`
        : "";
      await api.post("/api/v1/observations/", {
        patient_id: patId,
        dominio: "screening",
        texto: `${cutoffLine}${reverseLine}${flag}\n${obs}`.trim(),
      });
      setMsg("ok");
    } catch (e) { setMsg(_parseError(e)); }
    setSaving(false);
  };

  const exportScreening = () => {
    const rows = [];
    if (form.kind === "likert_flat") {
      form.items.forEach((it, i) => rows.push({
        item: i + 1, pregunta: it,
        puntaje: scoreLikertItem(form, scores, i) ?? 0,
        respuesta_original: parseInt(scores[`item_${i}`] || 0, 10),
        inverso: (form.reverseItems || []).includes(i) ? "si" : "no",
        max_item: 3,
      }));
    } else {
      form.domains.forEach((d) =>
        d.items.forEach((it, i) =>
          rows.push({
            dominio: d.name, item: it,
            puntaje: scores[`${d.name}_${i}`] || 0,
            max_dominio: d.max,
          }),
        ),
      );
    }
    rows.push({ dominio: "TOTAL", item: form.abbr, puntaje: result.total, max_dominio: form.maxScore });
    exportCSV(rows, `${form.abbr}_${Date.now()}.csv`);
  };

  /* ─── Render del cuerpo según tipo ────────────────────────── */
  const renderBinary = () => (
    <div className="space-y-5">
      {form.domains.map((d) => (
        <div key={d.name}>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-bold flex items-center gap-2" style={{ color: TEAL }}>
              <I name="label" className="text-sm" />{d.name}
            </p>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: `${TEAL}15`, color: TEAL }}>
              {domainTotal(d)}/{d.max}
            </span>
          </div>
          <div className="space-y-1.5 pl-4">
            {d.items.map((it, i) => (
              <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                <span className="text-[10px] font-mono w-5" style={{ color: "var(--ns-muted)" }}>{i + 1}</span>
                <p className="flex-1 text-xs" style={{ color: "var(--ns-text)" }}>{it}</p>
                <div className="flex gap-1">
                  {[0, 1].map((v) => (
                    <button key={v} onClick={() => setBin(d.name, i, v)}
                      className={`w-8 h-8 rounded-lg text-xs font-bold transition-all ${parseInt(scores[`${d.name}_${i}`] || 0, 10) === v ? "text-white shadow" : ""}`}
                      style={parseInt(scores[`${d.name}_${i}`] || 0, 10) === v
                        ? { background: v ? "#22c55e" : "#ef4444" }
                        : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }
                      }>
                      {v ? "✓" : "✗"}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  const renderLikert = () => {
    /* Grid dinámica según N de etiquetas (PHQ-9/GAD-7 = 4, SCARED-5 = 3, etc.) */
    const N = form.scaleLabels.length;
    const gridCls = `grid-cols-1 md:grid-cols-[1fr_repeat(${N},72px)]`;

    /* Mapa de inicio de subescala: itemIndex → metadata subescala */
    const subscaleStarts = {};
    if (form.subescalas) {
      let offset = 0;
      form.subescalas.forEach((se) => {
        subscaleStarts[offset] = se;
        offset += se.items;
      });
    }

    return (
    <div className="space-y-3">
      {form.questionPrefix && (
        <p className="text-sm italic mb-2" style={{ color: "var(--ns-muted)" }}>
          {form.questionPrefix}
        </p>
      )}
      {/* Cabecera con etiquetas de la escala */}
      <div className={`hidden md:grid ${gridCls} gap-2 text-[10px] font-bold uppercase tracking-wider px-3 pb-1`} style={{ color: "var(--ns-muted)" }}>
        <span></span>
        {form.scaleLabels.map((l, i) => (
          <span key={i} className="text-center leading-tight">{i}<br/>{l}</span>
        ))}
      </div>
      {form.items.map((it, i) => {
        const cur = parseInt(scores[`item_${i}`], 10);
        const isRed = (form.redFlagItems || []).includes(i) && cur >= 1;
        const isReverse = (form.reverseItems || []).includes(i);
        const seStart = subscaleStarts[i];
        /* Puntaje parcial de la subescala que termina ANTES de este inicio */
        const prevSeScore = seStart && result.subescalaScores?.length > 0
          ? result.subescalaScores.find((s) => s.nombre === seStart.nombre)
          : null;
        return (
          <React.Fragment key={i}>
            {/* Header de subescala al inicio de cada sección */}
            {seStart && (
              <div className="flex items-center justify-between pt-2 pb-1 border-t"
                style={{ borderColor: "var(--ns-card-b)" }}>
                <div>
                  <p className="text-xs font-extrabold flex items-center gap-1.5" style={{ color: TEAL }}>
                    <I name="bookmark" className="text-xs" />{seStart.nombre}
                  </p>
                  {seStart.descripcion && (
                    <p className="text-[10px] italic" style={{ color: "var(--ns-muted)" }}>{seStart.descripcion}</p>
                  )}
                </div>
                {prevSeScore && (
                  <span className="text-xs font-bold px-2 py-0.5 rounded-full"
                    style={{ background: `${TEAL}15`, color: TEAL }}>
                    {prevSeScore.total}/{prevSeScore.max}
                    {prevSeScore.cutoff != null && (
                      <span className="ml-1" style={{ color: prevSeScore.total >= prevSeScore.cutoff ? "#dc2626" : "#10b981" }}>
                        {prevSeScore.total >= prevSeScore.cutoff ? "⚠" : "✓"}
                      </span>
                    )}
                  </span>
                )}
              </div>
            )}
            <div className={`grid ${gridCls} gap-2 items-center p-3 rounded-xl border ${isRed ? "border-red-300" : ""}`}
              style={{ background: isRed ? "rgba(239,68,68,0.08)" : "var(--ns-subtle)", borderColor: isRed ? "#fca5a5" : "transparent" }}>
              <div className="flex items-start gap-2">
                <span className="text-[10px] font-mono w-5 mt-0.5" style={{ color: "var(--ns-muted)" }}>{i + 1}</span>
                <p className="text-xs leading-snug" style={{ color: "var(--ns-text)" }}>
                  {it}
                  {isReverse && <span className="ml-2 text-[9px] font-bold px-1.5 py-0.5 rounded" style={{background:"rgba(251,191,36,0.2)",color:"#92400e"}}>inverso</span>}
                </p>
              </div>
              {form.scaleLabels.map((_, v) => (
                <button key={v} onClick={() => setLik(i, v)}
                  className={`h-9 rounded-lg text-xs font-bold transition-all ${cur === v ? "text-white shadow" : ""}`}
                  title={form.scaleLabels[v]}
                  style={cur === v
                    ? { background: TEAL }
                    : { background: "var(--ns-card)", color: "var(--ns-muted)", border: "1px solid var(--ns-card-b)" }
                  }>
                  {v}
                </button>
              ))}
            </div>
          </React.Fragment>
        );
      })}
      {/* Red flag alert */}
      {result.redFlags?.length > 0 && (
        <div className="p-4 rounded-xl border-2 border-red-400 flex items-start gap-3" style={{ background: "rgba(239,68,68,0.08)" }}>
          <I name="warning" fill className="text-2xl text-red-600 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-extrabold text-red-700">Alerta clínica</p>
            <p className="text-xs text-red-700 mt-1">{form.redFlagMessage}</p>
          </div>
        </div>
      )}
      {/* Resumen de subescalas */}
      {result.subescalaScores?.length > 0 && (
        <div className="p-4 rounded-xl border" style={{ borderColor: `${TEAL}30`, background: `${TEAL}06` }}>
          <p className="text-xs font-bold mb-3 flex items-center gap-1.5" style={{ color: TEAL }}>
            <I name="analytics" className="text-sm" />Puntajes por subescala
          </p>
          <div className="flex flex-wrap gap-3">
            {result.subescalaScores.map((se, idx) => {
              const positivoCutoff = se.cutoff != null && se.total >= se.cutoff;
              return (
                <div key={idx} className="text-center px-4 py-2 rounded-xl"
                  style={{ background: "var(--ns-card)", border: `1px solid ${positivoCutoff ? "#fca5a5" : "var(--ns-card-b)"}` }}>
                  <p className="text-[10px] font-bold mb-0.5" style={{ color: "var(--ns-muted)" }}>{se.nombre}</p>
                  {se.descripcion && (
                    <p className="text-[9px] italic mb-1" style={{ color: "var(--ns-muted)" }}>{se.descripcion}</p>
                  )}
                  <p className="text-2xl font-extrabold" style={{ color: positivoCutoff ? "#dc2626" : TEAL }}>{se.total}</p>
                  <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>/{se.max}</p>
                  {se.cutoff != null && (
                    <p className="text-[10px] font-bold mt-1"
                      style={{ color: positivoCutoff ? "#dc2626" : "#10b981" }}>
                      {positivoCutoff ? `⚠ ≥ corte ${se.cutoff}` : `✓ < corte ${se.cutoff}`}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>);
  };

  return (
    <>
      <TopBar title="Módulo de Screening">
        <span className="text-xs whitespace-nowrap" style={{ color: "var(--ns-muted)" }}>
          Cognitivo · Emocional · Conductual · Funcional
        </span>
      </TopBar>
      <main className="p-8 space-y-6 max-w-6xl mx-auto">
        <MsgBanner msg={msg === "ok" ? "ok" : msg} onDismiss={msg && msg !== "ok" ? () => setMsg("") : null} />

        {/* F8.2: Wizard de motivo de consulta — sugiere batería inicial */}
        <ScreeningWizard
          onPickTest={(tid) => { setTest(tid); setScores({}); setObs(""); }}
          edadInicial={null}
        />

        {/* Selector de instrumento: tarjeta por categoría clínica */}
        <Card className="p-5">
          <div className="flex items-center gap-2 mb-4">
            <I name="tune" className="text-lg" style={{ color: TEAL }} />
            <h3 className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>Seleccionar instrumento</h3>
            <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full font-semibold" style={{ background: `${TEAL}15`, color: TEAL }}>
              {Object.keys(SCREENING_FORMS).length} escalas disponibles
            </span>
          </div>
          <div className="space-y-3">
            {[
              { title: "Cognitivo",    icon: "psychology",         domains: ["Cognitivo", "Severidad demencia"] },
              { title: "Emocional",    icon: "sentiment_sad",      domains: ["Depresión", "Ansiedad", "Ansiedad / Depresión", "Ansiedad infantil"] },
              { title: "TDAH",         icon: "bolt",               domains: ["TDAH / oposicionista", "TDAH escolar", "TDAH adultos"] },
              { title: "Conductual",   icon: "manage_accounts",    domains: ["TEA (screening temprano)", "Síntomas neuropsiquiátricos"] },
              { title: "Funcional",    icon: "accessibility_new",  domains: ["Funcionalidad básica", "Funcionalidad instrumental", "Sobrecarga del cuidador"] },
              { title: "Trauma / PTSD", icon: "crisis_alert",      domains: ["Trauma / PTSD"] },
            ].map((group) => {
              const matching = Object.keys(SCREENING_FORMS)
                .filter((k) => group.domains.includes(SCREENING_FORMS[k].domain));
              if (matching.length === 0) return null;
              return (
                <div key={group.title} className="flex items-center gap-2 flex-wrap p-3 rounded-lg"
                  style={{ background: "var(--ns-subtle)" }}>
                  <div className="flex items-center gap-1.5 shrink-0" style={{ minWidth: 120 }}>
                    <I name={group.icon} className="text-sm" style={{ color: TEAL }} />
                    <span className="text-[11px] font-extrabold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                      {group.title}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {matching.map((k) => (
                      <button key={k}
                        onClick={() => { setTest(k); setScores({}); setObs(""); }}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${test === k ? "text-white shadow-md" : "hover:shadow-sm"}`}
                        title={SCREENING_FORMS[k].name}
                        style={test === k
                          ? { background: TEAL, boxShadow: `0 4px 12px -4px ${TEAL}60` }
                          : { background: "var(--ns-card)", color: "var(--ns-muted)", border: "1px solid var(--ns-card-b)" }}>
                        {SCREENING_FORMS[k].abbr}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        <Card className="p-5">
          <div className="flex flex-col sm:flex-row sm:items-end gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <I name="description" className="text-base" style={{ color: TEAL }} />
                <div>
                  <p className="text-sm font-bold" style={{ color: "var(--ns-text)" }}>{form.name}</p>
                  <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>{form.domain} · {form.ageRange}</p>
                </div>
              </div>
              <Label>Paciente</Label>
              <Sel value={patId} onChange={(e) => setPatId(e.target.value)}>
                <option value="">— Seleccione —</option>
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nombre_completo || `${p.primer_nombre} ${p.primer_apellido}`}
                  </option>
                ))}
              </Sel>
            </div>
            <div className="flex items-end gap-4 sm:flex-col sm:items-end">
              <div className="text-right">
                <p className="text-4xl font-extrabold tabular-nums" style={{ color: result.color }}>
                  {result.total}<span className="text-lg opacity-50">/{form.maxScore}</span>
                </p>
                <p className="text-xs font-bold uppercase tracking-wider mt-0.5" style={{ color: result.color }}>{result.label}</p>
                <p className="text-[10px] mt-0.5" style={{ color: "var(--ns-muted)" }}>
                  Corte: {form.kind === "likert_flat" ? `≥${form.clinicalCutoff}` : form.cutoff}
                </p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          {form.notes && (
            <p className="text-xs italic mb-4 flex items-start gap-1.5 p-3 rounded-lg"
              style={{ color: "var(--ns-muted)", background: "var(--ns-subtle)" }}>
              <I name="info" className="text-sm shrink-0 mt-0.5" />{form.notes}
            </p>
          )}
          {form.kind === "likert_flat" ? renderLikert() : renderBinary()}
        </Card>

        <Card className="p-6">
          <Label>Observaciones</Label>
          <Txta value={obs} onChange={(e) => setObs(e.target.value)}
            placeholder="Observaciones clínicas durante la aplicación..." />
        </Card>

        <div className="flex gap-3 justify-end">
          <Btn v="outline" onClick={exportScreening}>
            <I name="download" className="text-sm" />Exportar CSV
          </Btn>
          <Btn onClick={save} disabled={saving || !patId}>
            {saving ? "Guardando..." : "Guardar Resultados"}
          </Btn>
        </div>

        {form.license && (
          <p className="text-[10px] text-center" style={{ color: "var(--ns-muted)" }}>
            {form.license}
          </p>
        )}
      </main>
    </>
  );
}
