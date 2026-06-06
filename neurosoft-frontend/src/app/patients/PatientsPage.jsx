/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/PatientsPage.jsx — Listado y búsqueda de pacientes
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../../api/client.js";
import { Btn, Card, I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { SkeletonCard } from "../../ui/Skeleton.jsx";
import { useToast } from "../../contexts.jsx";

const TAG_PRESETS = ["Particular", "EPS", "Convenio universidad", "Prioritario", "Evaluación pendiente"];
const TAG_COLORS = ["#0d9488", "#7c3aed", "#d97706", "#dc2626", "#0891b2", "#6366f1"];

export default function PatientsPage({ setPage, _nav, setEvalCtx }) {
  const toast = useToast();
  const [pts, setPts] = useState([]);
  const [ld, setLd] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("Todos");
  const [tagFilter, setTagFilter] = useState("");

  const load = useCallback(async () => {
    setLd(true);
    try {
      const d = await api.get(`/api/v1/patients/panel?poblacion=${filter === "Todos" ? "" : filter.toLowerCase()}`);
      setPts(d.pacientes || d || []);
    } catch { setPts([]); }
    setLd(false);
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const allTags = useMemo(() => {
    const s = new Set(TAG_PRESETS);
    pts.forEach((p) => (p.etiquetas || []).forEach((t) => s.add(t)));
    return [...s];
  }, [pts]);

  const fl = pts.filter(p => {
    if (tagFilter && !(p.etiquetas || []).includes(tagFilter)) return false;
    if (!search) return true;
    const s = search.toLowerCase();
    return (p.nombre_completo || "").toLowerCase().includes(s)
        || (p.numero_documento || "").includes(s);
  });

  const addTag = async (patientId, tag) => {
    const p = pts.find((x) => x.id === patientId);
    if (!p || !tag?.trim()) return;
    const next = [...new Set([...(p.etiquetas || []), tag.trim()])].slice(0, 12);
    try {
      await api.patch(`/api/v1/patients/${patientId}`, { etiquetas: next });
      setPts((prev) => prev.map((x) => (x.id === patientId ? { ...x, etiquetas: next } : x)));
    } catch {
      toast.error("No se pudo guardar la etiqueta");
    }
  };
  const ini = (p) => (p.nombre_completo || p.primer_nombre || "")
    .split(" ").slice(0, 2).map(w => w[0]).join("").toUpperCase() || "?";
  const clr = [
    "bg-teal-100 text-teal-600",
    "bg-teal-100 text-teal-600",
    "bg-orange-100 text-orange-600",
    "bg-purple-100 text-purple-600",
  ];

  return (
    <>
      <TopBar title="Panel de Pacientes">
        <Btn onClick={() => setPage("register")}>
          <I name="person_add" className="text-lg" />Registrar
        </Btn>
      </TopBar>
      <main className="p-8">
        <div className="flex items-center justify-between mb-8 gap-4 flex-wrap">
          <div className="relative flex-1 max-w-md">
            <I name="search" className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-12 pr-4 py-3.5 rounded-2xl border-2 border-transparent focus:border-teal-500/20 focus:ring-0 text-sm"
              style={{ background: "var(--ns-input)", color: "var(--ns-text)" }}
              placeholder="Buscar por nombre o documento..." />{/* §dark-mode-fix */}
          </div>
          <div className="flex gap-2 flex-wrap">
            {tagFilter && (
              <button onClick={() => setTagFilter("")}
                className="px-3 py-2 rounded-xl text-xs font-bold border" style={{ borderColor: TEAL, color: TEAL }}>
                Etiqueta: {tagFilter} ×
              </button>
            )}
            {allTags.slice(0, 8).map((t, i) => (
              <button key={t} onClick={() => setTagFilter(tagFilter === t ? "" : t)}
                className={`px-3 py-2 rounded-xl text-xs font-bold transition-all ${tagFilter === t ? "text-white" : ""}`}
                style={tagFilter === t ? { background: TAG_COLORS[i % TAG_COLORS.length] } : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                {t}
              </button>
            ))}
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            {["Todos", "Infantil", "Adulto_joven", "Adulto_mayor"].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                  filter === f ? "text-white shadow-lg" : "bg-gray-100 text-gray-500"
                }`}
                style={filter === f ? { background: TEAL } : {}}>
                {f.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
        {ld ? (
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : null}
        <Card className="overflow-hidden" style={ld ? { display: "none" } : {}}>
          {fl.length === 0 && !ld ? (
            <div className="flex flex-col items-center py-20 text-gray-400">
              <I name="person_off" className="text-5xl mb-4" />
              <p className="font-bold">Sin pacientes</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="text-left text-[10px] font-extrabold uppercase tracking-[0.2em] border-b"
                  style={{ color: "#43465540", borderColor: "#efeeea" }}>
                  <th className="pb-4 pt-6 px-8">Paciente</th>
                  <th className="pb-4 pt-6 px-6">Documento</th>
                  <th className="pb-4 pt-6 px-6">Población</th>
                  <th className="pb-4 pt-6 px-6">Fecha</th>
                  <th className="pb-4 pt-6 px-8 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {fl.map((p, i) => (
                  <tr key={p.id || i}
                    className="group hover:bg-teal-50/30 transition-all cursor-pointer"
                    style={{ borderBottom: "1px solid #f5f3ef" }}>
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-4">
                        <div className={`w-11 h-11 rounded-xl flex items-center justify-center font-extrabold text-sm ${clr[i % clr.length]}`}>
                          {ini(p)}
                        </div>
                        <div>
                          <h4 className="font-bold group-hover:text-teal-600 transition-colors">
                            {p.nombre_completo || `${p.primer_nombre || ""} ${p.primer_apellido || ""}`}
                          </h4>
                          <p className="text-xs" style={{ color: "var(--ns-muted)" }}>{p.sexo === "H" ? "Masculino" : "Femenino"}</p>
                          {(p.etiquetas || []).length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1.5">
                              {(p.etiquetas || []).map((t, ti) => (
                                <span key={t} className="text-[9px] font-bold px-2 py-0.5 rounded-full text-white"
                                  style={{ background: TAG_COLORS[ti % TAG_COLORS.length] }}>{t}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-5 font-mono text-sm text-gray-500">{p.numero_documento}</td>
                    <td className="px-6 py-5">
                      <span className={`inline-flex px-2.5 py-1 text-[10px] font-extrabold uppercase rounded-lg border ${
                        p.poblacion === "infantil" ? "bg-teal-50 text-teal-600 border-teal-100"
                        : p.poblacion === "adulto_joven" ? "bg-teal-50 text-teal-600 border-teal-100"
                        : "bg-orange-50 text-orange-600 border-orange-100"
                      }`}>
                        {(p.poblacion || "—").replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-sm text-gray-500">{p.fecha_atencion || "—"}</td>
                    <td className="px-8 py-5 text-right">
                      <div className="flex justify-end gap-1">
                        <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-teal-600 hover:text-white text-gray-400 transition-all"
                          onClick={() => { localStorage.setItem("ns_sel_patient", p.id); setPage("clinical_history"); }}
                          title="HC">
                          <I name="clinical_notes" className="text-lg" />
                        </button>
                        <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-teal-600 hover:text-white text-gray-400 transition-all"
                          onClick={() => { if (setEvalCtx) setEvalCtx(c => ({ ...c, patientId: p.id })); setPage("eval_apply"); }}
                          title="Evaluar">
                          <I name="psychology" className="text-lg" />
                        </button>
                        <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-teal-600 hover:text-white text-gray-400 transition-all"
                          onClick={() => { localStorage.setItem("ns_sel_patient", p.id); setPage("history"); }}
                          title="Historial">
                          <I name="history" className="text-lg" />
                        </button>
                        <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-purple-600 hover:text-white text-gray-400 transition-all"
                          onClick={() => { localStorage.setItem("ns_sel_patient", p.id); setPage("compare"); }}
                          title="Pre-Post">
                          <I name="compare_arrows" className="text-lg" />
                        </button>
                        <button className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-amber-500 hover:text-white text-gray-400 transition-all"
                          onClick={() => {
                            const tag = window.prompt("Etiqueta para este paciente:", TAG_PRESETS[0]);
                            if (tag) addTag(p.id, tag);
                          }}
                          title="Etiqueta">
                          <I name="label" className="text-lg" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <footer className="px-8 py-4 border-t" style={{ background: "#fafaf8", borderColor: "#f0eee8" }}>
            <p className="text-xs font-bold text-gray-400">
              Mostrando <span className="text-gray-700">{fl.length}</span> pacientes
            </p>
          </footer>
        </Card>
      </main>
    </>
  );
}
