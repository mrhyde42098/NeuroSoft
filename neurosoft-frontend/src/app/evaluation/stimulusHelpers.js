/** Láminas extraídas de PDFs de capacitación — no se muestran en evaluación. */
export function isPdfReferenceStimulus(s) {
  if (!s) return false;
  const tid = s.test_id || "";
  const nombre = String(s.nombre || "").toUpperCase();
  return (
    tid.includes("Stim_p")
    || tid.startsWith("NiWiscStim")
    || tid.startsWith("AdStim")
    || tid.startsWith("EstímuloStim")
    || nombre.includes("IN&S")
    || nombre.includes(" IN&")
    || (s.descripcion && String(s.descripcion).includes(".pdf"))
  );
}

/** Solo estímulos subidos por el clínico para esta subprueba. */
export function itemMappedStimuli(stimuli, testId) {
  return (stimuli || []).filter(
    (s) => !isPdfReferenceStimulus(s) && (!testId || s.test_id === testId),
  );
}
