/* ═══════════════════════════════════════════════════════════════════════
 * src/app/patients/PatientsPage.jsx — Listado y búsqueda de pacientes
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client.js";
import { Btn, Card, I, TopBar } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { SkeletonCard } from "../../ui/Skeleton.jsx";

export default function PatientsPage({ setPage, _nav, setEvalCtx }) {
  const [pts, setPts] = useState([]);
  const [ld, setLd] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("Todos");

  const load = useCallback(async () => {
    setLd(true);
    try {
      const d = await api.get(`/api/v1/patients/panel?poblacion=${filter === "Todos" ? "" : filter.toLowerCase()}`);
      setPts(d.pacientes || d || []);
    } catch { setPts([]); }
    setLd(false);
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const fl = pts.filter(p => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (p.nombre_completo || "").toLowerCase().includes(s)
        || (p.numero_documento || "").includes(s);
  });
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
          <div className="flex gap-2">
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
                          <p className="text-xs text-gray-400">{p.sexo === "H" ? "Masculino" : "Femenino"}</p>
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
