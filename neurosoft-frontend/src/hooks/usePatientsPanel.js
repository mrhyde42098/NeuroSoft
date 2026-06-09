import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { useToast } from "../contexts.jsx";

/** Lista de pacientes para selectores — fetch único compartido. */
export function usePatientsPanel() {
  const toast = useToast();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .get("/api/v1/patients/panel")
      .then((d) => {
        if (!cancelled) setPatients(d.pacientes || d || []);
      })
      .catch(() => {
        if (!cancelled) toast.error("Error cargando pacientes");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { patients, loading, setPatients };
}
