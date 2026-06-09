import { useCallback, useState } from "react";

/** Estado de formulario con setter por campo — reemplaza el patrón [f, sF] + set(k,v). */
export function useFormState(initial) {
  const [values, setValues] = useState(initial);
  const set = useCallback((key, val) => {
    setValues((prev) => ({ ...prev, [key]: val }));
  }, []);
  const reset = useCallback((next = initial) => {
    setValues(typeof next === "function" ? next : { ...next });
  }, [initial]);
  return { values, setValues, set, reset };
}
