/* Exportación RIPS mensual — preflight + descarga ZIP/TXT */
import React, { useState } from "react";
import { api } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Btn, Input, TopBar } from "../../ui/primitives.jsx";
import SectionCard from "../../ui/SectionCard.jsx";

function monthRange(ym) {
  const [y, m] = ym.split("-").map(Number);
  const desde = `${y}-${String(m).padStart(2, "0")}-01`;
  const last = new Date(y, m, 0).getDate();
  const hasta = `${y}-${String(m).padStart(2, "0")}-${String(last).padStart(2, "0")}`;
  return { desde, hasta };
}

export default function RipsPage() {
  const toast = useToast();
  const now = new Date();
  const defaultYm = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const [mes, setMes] = useState(defaultYm);
  const [loading, setLoading] = useState(false);
  const [preflight, setPreflight] = useState(null);

  const runPreflight = async () => {
    setLoading(true);
    try {
      const { desde, hasta } = monthRange(mes);
      const panel = await api.get("/api/v1/patients/panel?por_pagina=200");
      const pacientes = panel.pacientes || [];
      const rows = [];
      for (const p of pacientes.slice(0, 100)) {
        const issues = [];
        if (!p.codigo_rips && !p.cups) issues.push("Falta Dx/CUPS");
        if (p.eps && p.eps !== "Particular (sin EPS)" && !p.orden_medica_no) issues.push("Falta autorización");
        if (issues.length) rows.push({ paciente: p.nombre_completo, issues, ok: false });
        else if (p.cups || p.codigo_rips) rows.push({ paciente: p.nombre_completo, issues: [], ok: true });
      }
      setPreflight({ desde, hasta, rows, total: pacientes.length });
    } catch {
      toast.error("No se pudo validar el periodo");
    } finally {
      setLoading(false);
    }
  };

  const download = async (format) => {
    setLoading(true);
    try {
      const { desde, hasta } = monthRange(mes);
      const token = localStorage.getItem("ns_token");
      const res = await fetch(
        `/api/v1/rips/export?desde=${desde}&hasta=${hasta}&format=${format}`,
        { headers: token ? { Authorization: `Bearer ${token}` } : {} }
      );
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `RIPS_${desde}_${hasta}.${format === "zip" ? "zip" : "txt"}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`RIPS ${format.toUpperCase()} descargado`);
    } catch (e) {
      toast.error(e.message || "Error exportando RIPS");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <TopBar title="RIPS" subtitle="Registro Individual de Prestación de Servicios — Colombia" />
      <main className="p-6 lg:p-8 space-y-6 max-w-4xl mx-auto">
        <SectionCard eyebrow="Normativa" title="Exportación mensual" subtitle="Res. 3374/2000 · Codificación dual CIE-10/CIE-11 en transición" icon="receipt_long">
          <div className="flex flex-wrap items-end gap-4 mb-4">
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-wide" style={{ color: "var(--ns-muted)" }}>Periodo (mes)</span>
              <Input type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="mt-1" />
            </label>
            <Btn variant="secondary" onClick={runPreflight} disabled={loading}>Validar periodo</Btn>
            <Btn onClick={() => download("zip")} disabled={loading}>Descargar ZIP</Btn>
            <Btn variant="outline" onClick={() => download("txt")} disabled={loading}>Descargar TXT</Btn>
          </div>
          <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
            Para EPS contributivo/subsidiado se requieren CUPS y número de autorización en cada paciente/cita.
          </p>
        </SectionCard>

        {preflight && (
          <SectionCard eyebrow="Preflight" title={`${preflight.desde} — ${preflight.hasta}`} icon="fact_check">
            <p className="text-sm mb-3">{preflight.rows.filter((r) => r.ok).length} listos · {preflight.rows.filter((r) => !r.ok).length} con observaciones</p>
            <ul className="space-y-2 text-sm max-h-64 overflow-y-auto">
              {preflight.rows.map((r, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${r.ok ? "bg-green-600" : "bg-amber-500"}`} />
                  <span className="flex-1">{r.paciente}</span>
                  {!r.ok && <span className="text-xs text-amber-700">{r.issues.join(", ")}</span>}
                </li>
              ))}
            </ul>
          </SectionCard>
        )}
      </main>
    </>
  );
}
