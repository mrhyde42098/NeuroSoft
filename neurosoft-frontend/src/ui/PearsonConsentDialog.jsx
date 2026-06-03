/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/PearsonConsentDialog.jsx — Aceptación ÚNICA al instalar/iniciar
 * ───────────────────────────────────────────────────────────────────────
 * §S5.1x del plan de Frentes 5-8. Cumple el modelo "one-time install
 * acceptance" del material con copyright Pearson (WISC-IV, WAIS-III).
 *
 * Comportamiento:
 *   - Se muestra UNA SOLA VEZ al primer inicio del aplicativo.
 *   - Se persiste en localStorage con VERSION_ACUERDO.
 *   - Si el clínico no acepta, los ítems verbatim NO se muestran.
 *   - El clínico puede revocar en Configuración → Privacidad.
 *   - Cada aceptación/revocación se audita en backend.
 *
 * Cobertura legal mostrada al clínico:
 *   - Ley 23 de 1982 (Colombia) — Derechos de autor.
 *   - Ley 44 de 1993.
 *   - Decisión 486 de 2000 (CAN).
 *   - Tratados OMPI.
 *
 * Cobertura clínica (apoyo, no solo legal):
 *   - Compromiso de uso exclusivamente clínico.
 *   - No redistribución de los ítems.
 *   - Conservación de manuales originales.
 *   - Cumplimiento de condiciones de aplicación estandarizadas.
 *
 * Autor: NeuroSoft — 2026
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { I } from "./primitives.jsx";
import { useEscape, useFocusTrap } from "./a11y.jsx";
import {
  estadoAceptacionGlobal,
  registrarAceptacionGlobal,
  revocarAceptacionGlobal,
  VERSION_ACUERDO,
} from "../data/pearsonProtected.js";

/**
 * Componente principal: <PearsonConsentDialog/> — modal bloqueante
 * que se muestra solo si !estadoAceptacionGlobal().aceptado.
 *
 * Modos:
 *   - firstInstall: bloqueo completo hasta aceptar o rechazar
 *   - reConsent:    invitación amable a re-aceptar nueva versión
 *   - settings:     usado desde Config para revocar/aceptar voluntariamente
 */
export default function PearsonConsentDialog({
  open,
  onClose,
  user = null,
  mode = "firstInstall", // "firstInstall" | "reConsent" | "settings"
}) {
  const dialogRef = useRef(null);
  const [aceptando, setAceptando] = useState(false);
  const [rechazando, setRechazando] = useState(false);
  const [confirmado, setConfirmado] = useState(false);
  const [datosClinico, setDatosClinico] = useState({
    nombre: user?.nombre_completo || user?.username || "",
    documento: user?.documento || "",
    tarjetaProfesional: user?.tarjeta_profesional || "",
  });
  const estado = estadoAceptacionGlobal();
  const requiereReAceptacion = estado.requiereReAceptacion;
  const yaAceptado = estado.aceptado;

  useFocusTrap(open ? dialogRef : null);
  useEscape(open ? () => onClose?.(false) : null);

  // Reset al abrir
  useEffect(() => {
    if (open) {
      setConfirmado(false);
      setAceptando(false);
      setRechazando(false);
    }
  }, [open]);

  if (!open) return null;

  const handleAceptar = async () => {
    if (!confirmado) return;
    setAceptando(true);
    try {
      registrarAceptacionGlobal(
        user?.id || null,
        datosClinico.nombre || user?.username || null
      );
      onClose?.(true);
    } catch {
      setAceptando(false);
    }
  };

  const handleRechazar = () => {
    setRechazando(true);
    onClose?.(false);
  };

  const handleRevocar = () => {
    if (window.confirm?.(
      "¿Revocar la aceptación? La próxima vez que intente acceder a un ítem " +
        "protegido se le pedirá que acepte de nuevo el acuerdo."
    )) {
      revocarAceptacionGlobal();
      onClose?.(false);
    }
  };

  const esModal = mode === "firstInstall";
  const esReConsent = mode === "reConsent" && requiereReAceptacion && !yaAceptado;

  return (
    <div
      role="dialog"
      aria-modal={esModal ? "true" : "false"}
      aria-labelledby="pearson-consent-title"
      aria-describedby="pearson-consent-desc"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.55)" }}
    >
      <div
        ref={dialogRef}
        className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl"
        style={{
          background: "var(--ns-card)",
          color: "var(--ns-text)",
          border: "1px solid var(--ns-card-b)",
        }}
      >
        <header className="p-5 border-b" style={{ borderColor: "var(--ns-card-b)" }}>
          <div className="flex items-center gap-3">
            <I name="copyright" className="text-3xl" style={{ color: "var(--ns-accent, #0D9488)" }} />
            <div>
              <h2
                id="pearson-consent-title"
                className="text-lg font-extrabold"
              >
                Material con copyright — Acuerdo de uso clínico
              </h2>
              <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                Versión del acuerdo: <span className="ns-mono">{VERSION_ACUERDO}</span>
              </p>
            </div>
          </div>
        </header>

        <div id="pearson-consent-desc" className="p-5 space-y-4 text-sm leading-relaxed">
          {esReConsent && (
            <div
              className="p-3 rounded-lg text-xs"
              style={{
                background: "var(--ns-warn-bg, #FEF3C7)",
                color: "var(--ns-warn, #92400E)",
                border: "1px solid var(--ns-warn-b, #FCD34D)",
              }}
            >
              <strong>Cambio en el acuerdo:</strong> La versión del acuerdo de uso de
              material con copyright se actualizó. Por favor revise y acepte para
              continuar usando los ítems verbatim de WISC-IV y WAIS-III.
            </div>
          )}

          <p>
            NeuroSoft App incluye reactivos verbatim de las pruebas
            <strong> WISC-IV </strong>y <strong>WAIS-III</strong>, cuyo copyright
            pertenece a la <em>Editorial El Manual Moderno / Pearson</em>. Estos
            reactivos son entregados <strong>bajo licencia</strong> al profesional
            y NO se distribuyen libremente.
          </p>

          <section>
            <h3 className="font-bold text-sm uppercase tracking-wide mb-2">
              Cobertura legal
            </h3>
            <ul className="text-xs space-y-1 ml-4 list-disc">
              <li>
                <strong>Ley 23 de 1982</strong> (Colombia) — Derechos de autor.
              </li>
              <li>
                <strong>Ley 44 de 1993</strong> — Modificaciones a la Ley 23.
              </li>
              <li>
                <strong>Decisión 486 de 2000</strong> (Comunidad Andina) — Régimen
                Común sobre Propiedad Intelectual.
              </li>
              <li>
                <strong>Tratados OMPI</strong> (WIPO) sobre derechos de autor y
                obras intelectuales.
              </li>
              <li>
                <strong>Contrato de licenciamiento</strong> con Editorial El Manual
                Moderno / Pearson.
              </li>
            </ul>
          </section>

          <section>
            <h3 className="font-bold text-sm uppercase tracking-wide mb-2">
              Compromisos del clínico
            </h3>
            <ol className="text-xs space-y-1 ml-4 list-decimal">
              <li>
                Poseo licencia válida del material (WISC-IV, WAIS-III) emitida por
                el editor o su distribuidor autorizado.
              </li>
              <li>
                Usaré los ítems verbatim <strong>exclusivamente con fines clínicos</strong>
                {" "}(evaluación, diagnóstico, seguimiento) en el contexto de mis
                pacientes.
              </li>
              <li>
                No redistribuiré los ítems, ni los incluiré en informes, publicaciones
                o medios que salgan del flujo clínico-paciente.
              </li>
              <li>
                Conservaré los manuales originales como fuente de referencia y los
                consultaré ante cualquier duda sobre aplicación o baremación.
              </li>
              <li>
                Respetaré las condiciones de aplicación estandarizadas descritas en
                el manual original.
              </li>
              <li>
                Acepto que cada acceso a un ítem verbatim quede registrado en la
                bitácora de auditoría clínica del sistema.
              </li>
            </ol>
          </section>

          <section>
            <h3 className="font-bold text-sm uppercase tracking-wide mb-2">
              Apoyo clínico incluido
            </h3>
            <p className="text-xs">
              Al activar este acuerdo tendrás disponible en cada prueba con ítems
              verbatim:
            </p>
            <ul className="text-xs space-y-1 ml-4 list-disc">
              <li>
                <strong>Marca visual discreta</strong> sobre cada ítem (no interrumpe
                la aplicación).
              </li>
              <li>
                <strong>Referencia al manual original</strong> (página, ISBN, editorial).
              </li>
              <li>
                <strong>Errores frecuentes</strong> y alternativas baremos abiertos
                cuando proceda.
              </li>
              <li>
                <strong>Audit log</strong> automático por cada acceso.
              </li>
            </ul>
          </section>

          {!user && (
            <section
              className="p-3 rounded-lg space-y-2"
              style={{
                background: "var(--ns-subtle)",
                border: "1px solid var(--ns-card-b)",
              }}
            >
              <h3 className="font-bold text-sm">Identificación del clínico responsable</h3>
              <input
                className="w-full px-3 py-2 rounded text-sm"
                style={{
                  background: "var(--ns-card)",
                  border: "1px solid var(--ns-card-b)",
                  color: "var(--ns-text)",
                }}
                placeholder="Nombre completo"
                value={datosClinico.nombre}
                onChange={(e) =>
                  setDatosClinico((c) => ({ ...c, nombre: e.target.value }))
                }
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  className="px-3 py-2 rounded text-sm"
                  style={{
                    background: "var(--ns-card)",
                    border: "1px solid var(--ns-card-b)",
                    color: "var(--ns-text)",
                  }}
                  placeholder="Documento de identidad"
                  value={datosClinico.documento}
                  onChange={(e) =>
                    setDatosClinico((c) => ({ ...c, documento: e.target.value }))
                  }
                />
                <input
                  className="px-3 py-2 rounded text-sm"
                  style={{
                    background: "var(--ns-card)",
                    border: "1px solid var(--ns-card-b)",
                    color: "var(--ns-text)",
                  }}
                  placeholder="Tarjeta profesional (Ley 1090/2006)"
                  value={datosClinico.tarjetaProfesional}
                  onChange={(e) =>
                    setDatosClinico((c) => ({
                      ...c,
                      tarjetaProfesional: e.target.value,
                    }))
                  }
                />
              </div>
              <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                Estos datos se almacenan localmente en este dispositivo para registrar
                la aceptación. Se transmiten al backend solo como metadato de auditoría
                (no como PHI).
              </p>
            </section>
          )}

          <label className="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={confirmado}
              onChange={(e) => setConfirmado(e.target.checked)}
              className="mt-1"
            />
            <span className="text-xs">
              Confirmo que he leído el acuerdo, cumplo los compromisos listados y
              acepto el registro de auditoría de cada acceso a ítems verbatim.
            </span>
          </label>
        </div>

        <footer
          className="p-4 border-t flex flex-wrap gap-2 justify-end"
          style={{ borderColor: "var(--ns-card-b)" }}
        >
          {mode === "settings" && yaAceptado && (
            <button
              type="button"
              onClick={handleRevocar}
              className="px-4 py-2 rounded-lg text-xs font-bold"
              style={{
                background: "transparent",
                border: "1px solid #DC2626",
                color: "#DC2626",
              }}
            >
              Revocar aceptación
            </button>
          )}
          {esModal && (
            <button
              type="button"
              onClick={handleRechazar}
              disabled={rechazando || aceptando}
              className="px-4 py-2 rounded-lg text-xs font-bold"
              style={{
                background: "transparent",
                border: "1px solid var(--ns-card-b)",
                color: "var(--ns-text)",
              }}
            >
              No acepto
            </button>
          )}
          {!esModal && (
            <button
              type="button"
              onClick={() => onClose?.(yaAceptado)}
              className="px-4 py-2 rounded-lg text-xs font-bold"
              style={{
                background: "transparent",
                border: "1px solid var(--ns-card-b)",
                color: "var(--ns-text)",
              }}
            >
              Cerrar
            </button>
          )}
          <button
            type="button"
            onClick={handleAceptar}
            disabled={!confirmado || aceptando || rechazando}
            className="px-4 py-2 rounded-lg text-xs font-bold text-white"
            style={{
              background: !confirmado ? "var(--ns-muted)" : "var(--ns-accent, #0D9488)",
              cursor: !confirmado ? "not-allowed" : "pointer",
              opacity: !confirmado ? 0.6 : 1,
            }}
          >
            {aceptando
              ? "Registrando…"
              : mode === "settings"
              ? "Re-aceptar"
              : "Acepto y continúo"}
          </button>
        </footer>
      </div>
    </div>
  );
}
