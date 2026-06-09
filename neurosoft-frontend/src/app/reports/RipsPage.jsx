/* Exportación RIPS mensual — preflight + descarga ZIP/TXT */
import React, { useEffect, useState } from "react";
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
  const [numeroFactura, setNumeroFactura] = useState("");
  const [codigoPrestador, setCodigoPrestador] = useState("");

  useEffect(() => {
    api.get("/api/v1/config/")
      .then((cfg) => {
        const nit = cfg?.institucion?.nit || "";
        if (nit && !codigoPrestador) setCodigoPrestador(String(nit).slice(0, 12));
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchAllPatients = async () => {
    const pacientes = [];
    let pagina = 1;
    let total = Infinity;
    while (pacientes.length < total) {
      const panel = await api.get(`/api/v1/patients/panel?por_pagina=100&pagina=${pagina}`);
      const batch = panel.pacientes || [];
      pacientes.push(...batch);
      total = panel.total ?? batch.length;
      if (!batch.length || pacientes.length >= total) break;
      pagina += 1;
    }
    return pacientes;
  };

  const runPreflight = async () => {
    setLoading(true);
    try {
      const { desde, hasta } = monthRange(mes);
      const pacientes = await fetchAllPatients();
      const rows = [];
      for (const p of pacientes) {
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
      const params = new URLSearchParams({ desde, hasta, format });
      if (numeroFactura.trim()) params.set("numero_factura", numeroFactura.trim());
      if (codigoPrestador.trim()) params.set("codigo_prestador", codigoPrestador.trim());
      const res = await fetch(
        `/api/v1/rips/export?${params.toString()}`,
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
      <main className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
        <SectionCard eyebrow="Normativa" title="Exportación mensual" subtitle="Res. 2275/2023 · CIE-10 en export · CIE-11 complementario en HC" icon="receipt_long">
          <div className="flex flex-wrap items-end gap-4 mb-4">
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-wide" style={{ color: "var(--ns-muted)" }}>Periodo (mes)</span>
              <Input type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="mt-1" />
            </label>
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-wide" style={{ color: "var(--ns-muted)" }}>Nº factura</span>
              <Input value={numeroFactura} onChange={(e) => setNumeroFactura(e.target.value)} placeholder="Opcional" className="mt-1 w-40" />
            </label>
            <label className="block">
              <span className="text-xs font-bold uppercase tracking-wide" style={{ color: "var(--ns-muted)" }}>Cód. prestador</span>
              <Input value={codigoPrestador} onChange={(e) => setCodigoPrestador(e.target.value)} placeholder="NIT" className="mt-1 w-40" />
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
            <p className="text-sm mb-3" style={{ color: "var(--ns-muted)" }}>
              {preflight.total} pacientes revisados · {preflight.rows.filter((r) => !r.ok).length} con observaciones
            </p>
            <div className="max-h-64 overflow-y-auto space-y-1">
              {preflight.rows.filter((r) => !r.ok).slice(0, 50).map((r, i) => (
                <p key={i} className="text-xs text-amber-800">{r.paciente}: {r.issues.join(", ")}</p>
              ))}
              {preflight.rows.filter((r) => !r.ok).length > 50 && (
                <p className="text-xs" style={{ color: "var(--ns-muted)" }}>… y más</p>
              )}
            </div>
          </SectionCard>
        )}
      </main>
    </>
  );
}
