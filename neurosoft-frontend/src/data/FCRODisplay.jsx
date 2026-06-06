/* FCRO: lámina PNG (original + numerada superpuesta) o SVG de respaldo */

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
  const overlayNumbers = scoringMode || showNumbers;

  if (!useSvg) {
    return (
      <div className="w-full flex flex-col items-center gap-2">
        <div className="relative w-full" style={{ maxHeight: scoringMode ? "min(58vh, 560px)" : "380px" }}>
          <img
            src={LAMINA}
            alt="Figura Compleja de Rey-Osterrieth — original"
            className="w-full h-auto object-contain bg-white"
            onError={() => setUseSvg(true)}
          />
          {overlayNumbers && (
            <img
              src={LAMINA_NUM}
              alt=""
              aria-hidden
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
              style={{ opacity: 0.75, mixBlendMode: "multiply" }}
            />
          )}
        </div>
        {scoringMode && (
          <p className="text-[9px] text-center" style={{ color: "var(--ns-muted)" }}>
            Original + capa numerada (Taylor, 18 elementos)
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
