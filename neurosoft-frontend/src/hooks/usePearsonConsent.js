/* ═══════════════════════════════════════════════════════════════
 * src/hooks/usePearsonConsent.js — Hook de aceptación one-time
 * ───────────────────────────────────────────────────────────────
 * §S5.1x: Hook central que consulta y gestiona el estado de
 * aceptación del acuerdo de uso de material con copyright.
 *
 * Comportamiento:
 *   - Lee localStorage al montar.
 *   - Re-evalúa ante cambios (storage events).
 *   - Devuelve helpers para re-aceptar / revocar.
 *
 * Uso típico en App.jsx:
 *   const { aceptado, requiereAceptacion } = usePearsonConsent();
 *   if (requiereAceptacion) return <PearsonConsentDialog ... />
 * ═══════════════════════════════════════════════════════════════ */

import { useCallback, useEffect, useState } from "react";
import {
  estadoAceptacionGlobal,
  registrarAceptacionGlobal,
  revocarAceptacionGlobal,
} from "../data/pearsonProtected.js";

export function usePearsonConsent() {
  const [estado, setEstado] = useState(() => estadoAceptacionGlobal());

  const refresh = useCallback(() => {
    setEstado(estadoAceptacionGlobal());
  }, []);

  useEffect(() => {
    const onStorage = (e) => {
      if (
        e.key === "ns_pearson_consent_global" ||
        e.key === "ns_pearson_consent_version"
      ) {
        refresh();
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [refresh]);

  const aceptar = useCallback((userId = null, userName = null) => {
    registrarAceptacionGlobal(userId, userName);
    refresh();
  }, [refresh]);

  const revocar = useCallback(() => {
    revocarAceptacionGlobal();
    refresh();
  }, [refresh]);

  return {
    aceptado: estado.aceptado,
    requiereAceptacion: !estado.aceptado,
    requiereReAceptacion: estado.requiereReAceptacion,
    version: estado.version,
    versionActual: estado.versionActual,
    fechaAceptacion: estado.fechaAceptacion,
    aceptar,
    revocar,
    refresh,
  };
}
