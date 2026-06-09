import { useReducer, useCallback } from "react";

const initialSession = {
  patId: "",
  proto: "wisc_iv",
  adaptacion: "estandar",
  cur: 0,
  puntajes: {},
  obs: {},
  itemScores: {},
  conductas_checked: {},
  mode: "apply",
  portadaOk: false,
  guiaOpen: typeof window !== "undefined" && window.matchMedia("(min-width:1280px)").matches,
  guiaTab: "conductas",
  manualTimer: false,
  timer: 0,
  timerOn: false,
  draftSavedAt: null,
  draftRestoredFrom: null,
};

function sessionReducer(state, action) {
  switch (action.type) {
    case "merge":
      return { ...state, ...action.payload };
    case "set_puntaje":
      return { ...state, puntajes: { ...state.puntajes, [action.testId]: action.value } };
    case "set_obs":
      return { ...state, obs: { ...state.obs, [action.testId]: action.value } };
    case "reset_scores":
      return {
        ...state,
        puntajes: {},
        obs: {},
        cur: 0,
        conductas_checked: {},
        itemScores: {},
        draftRestoredFrom: null,
        draftSavedAt: null,
      };
    default:
      return state;
  }
}

/** Estado centralizado de sesión de evaluación (useReducer). */
export function useEvalSession(overrides = {}) {
  const [state, dispatch] = useReducer(sessionReducer, { ...initialSession, ...overrides });

  const merge = useCallback((payload) => dispatch({ type: "merge", payload }), []);
  const setPuntaje = useCallback(
    (testId, value) => dispatch({ type: "set_puntaje", testId, value }),
    [],
  );
  const resetScores = useCallback(() => dispatch({ type: "reset_scores" }), []);

  return { session: state, dispatch, merge, setPuntaje, resetScores };
}

export function sanitizePuntajes(raw = {}) {
  return Object.fromEntries(
    Object.entries(raw)
      .filter(([, v]) => v != null && v !== "" && Number(v) !== 9999)
      .map(([k, v]) => [k, String(v)]),
  );
}
