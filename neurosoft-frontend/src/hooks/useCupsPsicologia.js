import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { CUPS_PSICOLOGIA_FALLBACK } from "../data/cupsPsicologia.js";

/** Catálogo CUPS desde GET /api/v1/cups/psicologia; fallback offline mínimo. */
export function useCupsPsicologia() {
  const [cups, setCups] = useState(CUPS_PSICOLOGIA_FALLBACK);
  const [source, setSource] = useState("local");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api.get("/api/v1/cups/psicologia")
      .then((j) => {
        if (cancelled) return;
        const items = (j.codigos || []).map((c) => ({
          codigo: c.codigo,
          nombre: c.nombre,
        }));
        if (items.length) {
          setCups(items);
          setSource("backend");
        }
        setLoading(false);
      })
      .catch(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  return { cups, source, loading };
}
