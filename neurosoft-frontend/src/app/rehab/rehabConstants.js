import StroopActivity from "./StroopActivity.jsx";
import NBackActivity from "./NBackActivity.jsx";
import FluencyActivity from "./FluencyActivity.jsx";
import TachadoActivity from "./TachadoActivity.jsx";
import CorsiBlocks from "../evaluation/CorsiBlocks.jsx";
import SpacedRetrievalActivity from "./SpacedRetrievalActivity.jsx";
import MentalRotationActivity from "./MentalRotationActivity.jsx";
import EkmanRecognitionActivity from "./EkmanRecognitionActivity.jsx";
import CPTActivity from "./CPTActivity.jsx";
import GoNoGoActivity from "./GoNoGoActivity.jsx";
import SetShiftingActivity from "./SetShiftingActivity.jsx";
import DenominacionClavesActivity from "./DenominacionClavesActivity.jsx";
import TowerOfLondonActivity from "./TowerOfLondonActivity.jsx";
import MindInEyesActivity from "./MindInEyesActivity.jsx";
import AvdDineroActivity from "./AvdDineroActivity.jsx";

export const TABS = [
  { id: "plan", label: "Plan", icon: "assignment_ind" },
  { id: "actividades", label: "Actividades", icon: "extension" },
  { id: "sesiones", label: "Sesiones", icon: "monitoring" },
];

export const DOMINIO_LABELS = {
  atencion: "Atención",
  memoria: "Memoria",
  memoria_trabajo: "Memoria de trabajo",
  funciones_ejecutivas: "Funciones ejecutivas",
  lenguaje: "Lenguaje",
  visoespacial: "Visoespacial",
  velocidad_procesamiento: "Velocidad de procesamiento",
};

export const DOMINIO_COLORS = {
  atencion: "#6366f1",
  memoria: "#0d9488",
  memoria_trabajo: "#0891b2",
  funciones_ejecutivas: "#ec4899",
  lenguaje: "#d97706",
  visoespacial: "#7c3aed",
  velocidad_procesamiento: "#dc2626",
};

export const ACTIVITY_COMPONENTS = {
  stroop: StroopActivity,
  n_back: NBackActivity,
  fluency_verbal: FluencyActivity,
  tachado: TachadoActivity,
  corsi_forward: CorsiBlocks,
  corsi_backward: CorsiBlocks,
  spaced_retrieval: SpacedRetrievalActivity,
  mental_rotation: MentalRotationActivity,
  ekman_recognition: EkmanRecognitionActivity,
  cpt: CPTActivity,
  go_no_go: GoNoGoActivity,
  set_shifting: SetShiftingActivity,
  denominacion_claves: DenominacionClavesActivity,
  tower_of_london: TowerOfLondonActivity,
  mente_ojos: MindInEyesActivity,
  avd_dinero: AvdDineroActivity,
};
