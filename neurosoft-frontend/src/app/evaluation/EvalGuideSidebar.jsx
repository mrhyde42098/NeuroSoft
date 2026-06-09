import React from "react";
import { Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import FloatingTimer from "../../ui/FloatingTimer.jsx";
import GuideFormatter, { GuideRichSection } from "./GuideFormatter.jsx";
import { GUIA_HC, GUIA_INFORME, INSTRUCCIONES } from "../../data/clinical.js";
import { getNeuronormaInfo } from "../../data/neuronormaColombia.js";

/** Panel lateral de guía clínica + cronómetro embebido. */
export default function EvalGuideSidebar({
  guiaOpen,
  onToggleGuia,
  guiaTab,
  onGuiaTabChange,
  testId,
  mode,
  portadaOk,
  hasTimer,
  manualTimer,
  onToggleManualTimer,
  timer,
  timerOn,
  onTimerStart,
  onTimerPause,
  onTimerReset,
  maxTime,
}) {
  return (
    <div className={`xl:shrink-0 xl:sticky xl:top-4 self-start transition-all duration-300 order-last xl:order-none ${guiaOpen ? "w-full xl:w-80" : "w-10"}`}>
      <button
        type="button"
        onClick={onToggleGuia}
        className="w-10 h-10 rounded-full flex items-center justify-center shadow-md mb-3 xl:ml-auto"
        style={{ background: TEAL }}
        aria-label={guiaOpen ? "Cerrar guía clínica" : "Abrir guía clínica"}
        title={guiaOpen ? "Cerrar guía" : "Abrir guía"}
      >
        <I name={guiaOpen ? "chevron_right" : "menu_book"} className="text-white text-lg" />
      </button>
      {guiaOpen && (
        <Card className="p-5 space-y-4 overflow-y-auto" style={{ maxHeight: "calc(100vh - 180px)" }}>
          <h3 className="font-bold text-sm flex items-center gap-2">
            <I name="menu_book" style={{ color: TEAL }} />
            Guía Clínica
          </h3>
          <div className="flex gap-1">
            {[["conductas", "Administración"], ["informe", "Informe"], ["hc", "HC"]].map(([k, l]) => (
              <button
                key={k}
                type="button"
                onClick={() => onGuiaTabChange(k)}
                className={`px-3 py-1.5 rounded-full text-[10px] font-bold transition-all ${guiaTab === k ? "bg-teal-600 text-white" : ""}`}
                style={guiaTab === k ? {} : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }}
              >
                {l}
              </button>
            ))}
          </div>
          {guiaTab === "conductas" && (
            <div className="space-y-4">
              {(() => {
                const nn = getNeuronormaInfo(testId);
                return nn ? (
                  <div className="p-3 rounded-xl border-l-3" style={{ borderColor: "#fb923c", background: "rgba(251,191,36,0.08)" }}>
                    <p className="text-[10px] font-extrabold uppercase tracking-wider" style={{ color: "#7c2d12" }}>
                      Norma Colombia · cap. {nn.capitulo}
                    </p>
                    <p className="text-[11px] mt-1" style={{ color: "#9a3412" }}>
                      Ajuste: {nn.ajuste.join(" + ")} · Salida: {nn.tipoPuntuacion === "ambos" ? "percentil + T" : nn.tipoPuntuacion.replace("_", " ")}
                    </p>
                  </div>
                ) : null;
              })()}
              <GuideFormatter instructions={INSTRUCCIONES[testId]} />
            </div>
          )}
          {guiaTab === "informe" && (
            <div className="space-y-3">
              <p className="text-[11px] p-2 rounded-lg" style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                Estos bloques se integran al <strong>informe PDF</strong> desde Resultados → Generar informe.
              </p>
              {Object.entries(GUIA_INFORME).map(([k, v]) => (
                <GuideRichSection
                  key={k}
                  title={k}
                  body={v}
                  icon="description"
                  accent={TEAL}
                />
              ))}
            </div>
          )}
          {guiaTab === "hc" && (
            <div className="space-y-3">
              <p className="text-[11px] p-2 rounded-lg" style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
                La <strong>historia clínica</strong> del paciente recibe antecedentes y motivo.
              </p>
              {Object.entries(GUIA_HC).map(([k, v]) => (
                <GuideRichSection key={k} title={k} body={v} icon="assignment_ind" accent="#6366f1" />
              ))}
            </div>
          )}
        </Card>
      )}
      {guiaOpen && mode === "apply" && portadaOk && (hasTimer || manualTimer) && (
        <Card className="p-4 mt-3 space-y-2">
          <p className="text-[10px] font-bold uppercase tracking-wider flex items-center gap-1" style={{ color: TEAL }}>
            <I name="timer" className="text-sm" />
            Cronómetro de aplicación
          </p>
          <FloatingTimer
            embedded
            visible
            timer={timer}
            timerOn={timerOn}
            maxTime={maxTime || 0}
            onStart={onTimerStart}
            onPause={onTimerPause}
            onReset={onTimerReset}
          />
        </Card>
      )}
      {guiaOpen && mode === "apply" && !hasTimer && (
        <Card className="p-4 mt-3">
          <button
            type="button"
            onClick={onToggleManualTimer}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all"
            style={manualTimer ? { background: TEAL, color: "#fff" } : { background: "var(--ns-subtle)", color: "var(--ns-muted)" }}
          >
            <I name="timer" className="text-sm" />
            {manualTimer ? "Ocultar cronómetro" : "Desplegar cronómetro"}
          </button>
        </Card>
      )}
    </div>
  );
}
