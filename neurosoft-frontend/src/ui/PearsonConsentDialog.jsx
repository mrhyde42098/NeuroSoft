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
                Material con copyright — Acuerdo para usarlo
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
              <strong>El acuerdo se actualizó.</strong> Léelo de nuevo y acéptalo
              para seguir usando el texto original de las pruebas WISC-IV y WAIS-III
              dentro de la aplicación.
            </div>
          )}

          <p>
            Para que tu trabajo clínico sea más ágil, NeuroSoft trae el texto
            original — palabra por palabra — de los estímulos de las pruebas
            <strong> WISC-IV </strong> y <strong> WAIS-III</strong>. Ese texto es
            propiedad de la <em>Editorial El Manual Moderno / Pearson</em> y solo
            se te muestra porque tú tienes tu propia licencia. <strong>No se
            puede copiar ni compartir</strong>; es para tu consulta en consulta.
          </p>

          <section>
            <h3 className="font-bold text-sm mb-2">
              ¿Por qué te lo pedimos?
            </h3>
            <p className="text-xs">
              Las leyes colombianas y los tratados internacionales protegen los
              derechos de autor de los manuales. Al usar el texto original dentro
              de NeuroSoft te comprometes a respetar esas reglas — igual que
              cuando hojeas tu manual físico. En concreto, esto se apoya en:
            </p>
            <ul className="text-xs space-y-1 ml-4 list-disc mt-2">
              <li>Ley 23 de 1982 (Colombia) — Derechos de autor.</li>
              <li>Ley 44 de 1993 — Modificaciones a la Ley 23.</li>
              <li>Decisión 486 de 2000 (Comunidad Andina).</li>
              <li>Tratados internacionales de la OMPI (WIPO).</li>
              <li>Tu contrato de licenciamiento con el editor.</li>
            </ul>
          </section>

          <section>
            <h3 className="font-bold text-sm mb-2">
              Tu compromiso como profesional
            </h3>
            <p className="text-xs mb-2">
              Al aceptar, te comprometes a:
            </p>
            <ol className="text-xs space-y-1 ml-4 list-decimal">
              <li>
                Tener tu licencia personal vigente del WISC-IV y/o WAIS-III.
              </li>
              <li>
                Usar el texto original únicamente con tus pacientes (evaluar,
                diagnosticar, hacer seguimiento).
              </li>
              <li>
                No copiar los estímulos a informes, publicaciones, redes sociales
                ni a ningún medio fuera de la consulta.
              </li>
              <li>
                Conservar tus manuales físicos como referencia ante cualquier
                duda sobre cómo aplicar o cómo puntuar.
              </li>
              <li>
                Seguir las instrucciones de aplicación que trae cada manual
                original.
              </li>
              <li>
                Aceptar que cada vez que abras un estímulo quede un registro
                automático en la bitácora de la aplicación.
              </li>
            </ol>
          </section>

          <section>
            <h3 className="font-bold text-sm mb-2">
              ¿Qué te ofrece NeuroSoft a cambio?
            </h3>
            <p className="text-xs">
              Una vez aceptado, en cada prueba con texto protegido encontrarás:
            </p>
            <ul className="text-xs space-y-1 ml-4 list-disc mt-2">
              <li>
                Una <strong>marca visual discreta</strong> sobre el estímulo
                (no interrumpe tu aplicación).
              </li>
              <li>
                La <strong>referencia exacta al manual</strong>: página, ISBN y
                editorial para que lo consultes cuando quieras.
              </li>
              <li>
                <strong>Errores frecuentes</strong> y alternativas de puntuación
                cuando aplique.
              </li>
              <li>
                <strong>Registro automático</strong> de cada apertura para tu
                tranquilidad y la del paciente.
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
              acepto el registro de auditoría de cada vez que abra el texto original
              de un estímulo.
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
