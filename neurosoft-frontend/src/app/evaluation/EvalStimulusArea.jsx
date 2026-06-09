import React from "react";
import { Card } from "../../ui/primitives.jsx";
import { REACTIVOS } from "../../data/clinical.js";
import { NativeStimuli } from "../../data/stimuli.jsx";
import ReactivePanel from "./ReactivePanel.jsx";
import StimulusDisplay from "./StimulusDisplay.jsx";
import ValidezPanel from "./ValidezPanel.jsx";
import { itemMappedStimuli } from "./stimulusHelpers.js";

/** Área de estímulos + reactivos interactivos de la prueba actual. */
export default function EvalStimulusArea({
  test,
  proto,
  adaptacion,
  estimulos,
  puntajes,
  setPuntajes,
  itemScores,
  setItemScores,
  onInsertValidezObs,
}) {
  const tid = test.test_id.split(" ")[0].trim();
  const mapped = itemMappedStimuli(estimulos, tid);
  const reactive = REACTIVOS[test.test_id];
  const hideDupNative = reactive?.type === "items" && (tid === "NiWiscDC" || tid === "AdWAISCC");
  const showStim = mapped.length > 0 || (NativeStimuli[tid] && !hideDupNative && reactive?.type !== "fcro");

  return (
    <>
      {showStim && (
        <Card className="p-5">
          <StimulusDisplay testId={tid} stimuli={mapped} />
        </Card>
      )}
      {reactive && (
        <ReactivePanel
          testId={tid}
          puntajes={puntajes}
          setPuntajes={setPuntajes}
          itemScores={itemScores}
          setItemScores={setItemScores}
          estimulos={itemMappedStimuli(estimulos, tid)}
          textScale={proto === "adulto_mayor" || adaptacion === "alto_contraste" ? "large" : "normal"}
        />
      )}
      {(proto === "validez" || test.test_id === "REY15" || test.test_id === "TOMM") && (
        <ValidezPanel onInsertObs={onInsertValidezObs} />
      )}
    </>
  );
}
