import React from "react";
import { Btn, I, Sel, TopBar } from "../../ui/primitives.jsx";
import { PatientSelect } from "../../ui/forms/PatientSelector.jsx";
import { ADAPTATIONS } from "../../utils/sattlerShortForms.js";

/** Barra superior + sub-header de modo y progreso en aplicación de evaluación. */
export default function EvalHeader({
  patients,
  patId,
  onPatIdChange,
  protos,
  proto,
  onProtoChange,
  adaptacion,
  onAdaptacionChange,
  goPage,
  onFinalizar,
  mode,
  onModeChange,
  doneCount,
  testsCount,
}) {
  return (
    <>
      <TopBar title="Evaluación Neuropsicológica">
        <PatientSelect
          bare
          patients={patients}
          value={patId}
          onChange={onPatIdChange}
          selectClassName="text-xs w-44 sm:w-52"
          placeholder="— Paciente —"
        />
        <Sel value={proto} onChange={(e) => onProtoChange(e.target.value)} className="text-xs w-28 sm:w-32">
          {Object.entries(protos).map(([k, v]) => (
            <option key={k} value={k}>{v.nombre}</option>
          ))}
        </Sel>
        <Sel
          value={adaptacion}
          onChange={(e) => onAdaptacionChange(e.target.value)}
          className="text-xs w-32 sm:w-40"
          title="Adaptación para casos especiales (Protocolos Alternos)"
        >
          {Object.entries(ADAPTATIONS).map(([k, v]) => (
            <option key={k} value={k}>{v.label}</option>
          ))}
        </Sel>
        {goPage && (
          <Btn className="text-xs whitespace-nowrap" onClick={() => goPage("screening")}>
            <I name="fact_check" className="text-sm mr-1" />
            Screening
          </Btn>
        )}
        <Btn v="danger" className="text-xs whitespace-nowrap" onClick={onFinalizar}>
          Finalizar
        </Btn>
      </TopBar>
      <div
        className="px-6 sm:px-8 py-3 border-b flex flex-wrap items-center gap-4"
        style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}
      >
        <div className="flex rounded-full overflow-hidden border shrink-0" style={{ borderColor: "var(--ns-card-b)" }}>
          <button
            type="button"
            onClick={() => onModeChange("apply")}
            className={`px-4 py-1.5 text-xs font-bold transition-all whitespace-nowrap ${mode === "apply" ? "bg-teal-600 text-white" : "bg-transparent"}`}
            style={mode === "apply" ? {} : { color: "var(--ns-muted)" }}
          >
            <I name="touch_app" className="text-sm mr-1" />
            Aplicación
          </button>
          <button
            type="button"
            onClick={() => onModeChange("table")}
            className={`px-4 py-1.5 text-xs font-bold transition-all whitespace-nowrap ${mode === "table" ? "bg-teal-600 text-white" : "bg-transparent"}`}
            style={mode === "table" ? {} : { color: "var(--ns-muted)" }}
          >
            <I name="table_chart" className="text-sm mr-1" />
            Registro
          </button>
        </div>
        <div className="flex items-center gap-3 flex-1 min-w-[200px]">
          <span className="text-xs font-bold whitespace-nowrap" style={{ color: "var(--ns-muted)" }}>
            Progreso: {doneCount}/{testsCount}
          </span>
          <div className="flex-1 max-w-xs h-1.5 rounded-full overflow-hidden" style={{ background: "var(--ns-subtle)" }}>
            <div
              className="h-full bg-teal-600 rounded-full transition-all"
              style={{ width: `${testsCount ? (doneCount / testsCount) * 100 : 0}%` }}
            />
          </div>
        </div>
      </div>
    </>
  );
}
