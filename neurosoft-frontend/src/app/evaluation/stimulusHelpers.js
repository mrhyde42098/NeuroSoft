/** Importaciones masivas de referencia (no mapeadas por ítem) — no duplicar en evaluación. */
export function isPdfReferenceStimulus(s) {
  if (!s) return false;
  const tid = s.test_id || "";
  return (
    tid.includes("Stim_p")
    || tid.startsWith("NiWiscStim")
    || tid.startsWith("AdStim")
    || tid.startsWith("EstímuloStim")
  );
}

/** Solo estímulos subidos por el clínico para esta subprueba. */
export function itemMappedStimuli(stimuli, testId) {
  return (stimuli || []).filter(
    (s) => !isPdfReferenceStimulus(s) && (!testId || s.test_id === testId),
  );
}
