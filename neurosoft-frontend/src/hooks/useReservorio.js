import { useEffect, useState } from "react";
import { api } from "../api/client";
import { RECOMMENDATIONS_LIB } from "../data/datosClinicos.js";

const POBLACION_TO_GRUPO = {
  infantil: "infantil",
  adulto_joven: "adulto",
  adulto: "adulto",
  adulto_mayor: "adulto_mayor",
};

function adaptBackendCuadro(backendCuadro) {
  const todas = backendCuadro.recomendaciones || [];
  return {
    id: backendCuadro.id,
    nombre: backendCuadro.label || backendCuadro.id,
    grupo: backendCuadro.grupo,
    grupo_label: backendCuadro.grupo_label,
    cie: "",
    categorias: {
      general: todas,
    },
  };
}

export function useReservorio(poblacion) {
  const [cuadros, setCuadros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [source, setSource] = useState("local");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    const grupo = POBLACION_TO_GRUPO[poblacion] || "";
    const url = grupo
      ? `/api/v1/reservorio/cuadros?poblacion=${grupo}`
      : `/api/v1/reservorio/cuadros`;
    api.get(url)
      .then((j) => {
        if (cancelled) return;
        const adaptados = (j.cuadros || []).map(adaptBackendCuadro);
        setCuadros(adaptados);
        setSource("backend");
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[reservorio] backend no disponible, usando local:", e?.message || e);
        const localEntries = Object.entries(RECOMMENDATIONS_LIB)
          .filter(([k]) => k !== "_meta" && k !== "_notas")
          .map(([id, r]) => ({
            id,
            nombre: r.nombre || id,
            grupo: poblacion || "",
            grupo_label: poblacion || "",
            cie: r.cie || "",
            categorias: r.categorias || { general: [] },
          }));
        setCuadros(localEntries);
        setSource("local");
        setError(e?.message || "Backend no disponible");
        setLoading(false);
      });
    return () => { cancelled = true; };
  }, [poblacion]);

  return { cuadros, loading, error, source };
}

export async function fetchCuadroDetalle(grupo, id) {
  const url = `/api/v1/reservorio/cuadros/${grupo}/${id}`;
  const j = await api.get(url);
  return {
    id: j.id,
    nombre: j.label,
    grupo: j.grupo,
    grupo_label: j.grupo_label,
    cie: "",
    categorias: { general: j.recomendaciones || [] },
  };
}

