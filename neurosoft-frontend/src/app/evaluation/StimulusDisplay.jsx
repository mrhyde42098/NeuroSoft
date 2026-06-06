/* ═══════════════════════════════════════════════════════════════════════

 * src/app/evaluation/StimulusDisplay.jsx — Referencia visual nativa (SVG)

 * Imágenes solo si el clínico las subió en Config → Estímulos (mapeadas).

 * ═══════════════════════════════════════════════════════════════════════ */



import React from "react";

import { I } from "../../ui/primitives.jsx";

import { TEAL } from "../../ui/tokens.js";

import { NativeStimuli } from "../../data/stimuli.jsx";

import { esVerbatim, estadoProteccion, registrarAccesoItem } from "../../data/pearsonProtected.js";

import { SelloProtegidoBadge } from "../../ui/SelloProtegidoBadge.jsx";

import ApoyoClinicoPanel from "../../ui/ApoyoClinicoPanel.jsx";

import { useEffect, useRef } from "react";

import { itemMappedStimuli } from "./stimulusHelpers.js";



export default function StimulusDisplay({ testId, stimuli, itemIndex = null }) {

  const mapped = itemMappedStimuli(stimuli, testId);

  const Native = NativeStimuli[testId];

  const accessLoggedRef = useRef(false);

  const verbatim = esVerbatim(testId);

  const prot = estadoProteccion(testId);



  useEffect(() => {

    if (!verbatim || !prot.aceptado) return;

    if (accessLoggedRef.current) return;

    accessLoggedRef.current = true;

    registrarAccesoItem(testId, itemIndex).catch(() => {});

  }, [verbatim, prot.aceptado, testId, itemIndex]);



  const filtered = itemIndex != null

    ? mapped.filter(

      (s) => String(s.item_id) === String(itemIndex)

        || String(s.item_id) === `item_${itemIndex}`,

    )

    : mapped.filter((s) => !s.item_id);

  const showCustom = filtered.length > 0;

  if (!showCustom && !Native) return null;



  return (

    <div className="w-full max-w-3xl mx-auto mb-3">

      <div className="rounded-xl p-3 relative" style={{ background: "var(--ns-subtle)", border: "1px solid var(--ns-card-b)" }}>

        {verbatim && prot.aceptado && <SelloProtegidoBadge testId={testId} mode="corner" />}

        <p className="text-[10px] font-extrabold uppercase tracking-wider mb-2" style={{ color: "var(--ns-muted)" }}>

          <I name="image" className="text-[10px] mr-1" />

          {showCustom ? `Material adjunto (${filtered.length})` : "Referencia visual (NeuroSoft)"}

        </p>

        {showCustom ? (

          <div className="flex gap-2 overflow-x-auto pb-1">

            {filtered.map((s) => (

              <div key={s.id} className="shrink-0">

                {s.tipo === "imagen" && s.contenido_base64 ? (

                  <img src={s.contenido_base64} alt={s.nombre} className="h-56 rounded-lg border bg-white" />

                ) : (

                  <div className="h-40 w-40 flex flex-col items-center justify-center rounded-lg border bg-white p-2">

                    <I name={s.tipo === "lista_palabras" ? "format_list_numbered" : s.tipo === "audio" ? "volume_up" : "description"} className="text-3xl" style={{ color: TEAL }} />

                    <p className="text-[10px] font-bold mt-1 text-center">{s.nombre}</p>

                  </div>

                )}

                <p className="text-[9px] text-center mt-1 truncate w-40" style={{ color: "var(--ns-muted)" }}>{s.nombre}</p>

              </div>

            ))}

          </div>

        ) : Native ? (

          <div className="min-h-[12rem] flex items-center justify-center bg-white rounded-lg border p-3">

            <Native />

          </div>

        ) : null}

        {verbatim && (
          <div className="mt-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
            <p className="text-[10px] font-extrabold uppercase tracking-wider mb-2 flex items-center gap-1" style={{ color: TEAL }}>
              <I name="support" className="text-[12px]" />Apoyo clínico
            </p>
            <ApoyoClinicoPanel testId={testId} variant="compact" />
          </div>
        )}

      </div>

    </div>

  );

}

