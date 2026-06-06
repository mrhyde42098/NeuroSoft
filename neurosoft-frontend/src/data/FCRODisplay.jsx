/* FCRO: lámina de protocolo (PNG) o SVG de respaldo */

import React, { useState } from "react";
import { FCROFigure } from "./PatronFCRO.jsx";

const LAMINA = "/assets/fcro/fcro-lamina.png";
const LAMINA_NUM = "/assets/fcro/fcro-lamina-numerada.png";

export default function FCRODisplay({
  scores = {},
  highlight = -1,
  showNumbers = false,
  scoringMode = false,
}) {
  const [useSvg, setUseSvg] = useState(false);
  const src = scoringMode || showNumbers ? LAMINA_NUM : LAMINA;

  if (!useSvg) {
    return (
      <div className="w-full flex flex-col items-center gap-2">
        <img
          src={src}
          alt="Figura Compleja de Rey-Osterrieth"
          className="max-w-full h-auto object-contain bg-white"
          style={{ maxHeight: scoringMode ? "min(58vh, 560px)" : "380px" }}
          onError={() => setUseSvg(true)}
        />
        {scoringMode && (
          <p className="text-[9px] text-center" style={{ color: "var(--ns-muted)" }}>
            Lámina Taylor (18 elementos) · Compare con el dibujo del paciente
          </p>
        )}
      </div>
    );
  }

  return (
    <FCROFigure
      scores={scores}
      showNumbers={showNumbers}
      highlight={highlight}
      size={scoringMode ? "lg" : "md"}
    />
  );
}
