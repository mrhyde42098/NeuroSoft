/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/OrdenClinicoBanner.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §M-6 — Indicador de orden clínico de aplicación + timer de recobro.
 *
 * Se embebe en EvalApplyPage. Reactivo a:
 *   • testIdActual    — qué prueba está aplicándose ahora
 *   • completados     — { test_id: timestamp } pruebas ya completadas
 *
 * Muestra:
 *   • Hito clínico actual (de la lista de hitos del protocolo)
 *   • Siguiente prueba recomendada
 *   • Si la prueba actual es un RECOBRO: timer de intervalo respecto a
 *     su codificación. Bloquea visualmente si no han pasado los minutos
 *     mínimos (no impide aplicar, solo advierte clínicamente).
 *   • Si hay INTERFERENCIA entre actual y siguiente, advierte.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useMemo, useEffect, useState } from "react";
import { I } from "../../ui/primitives.jsx";
import {
  PROTOCOLOS_ORDEN, parRecobroPara, siguienteTestRecomendado, detectarInterferencia, nombrePrueba,
} from "../../data/protocolosOrden.js";

export default function OrdenClinicoBanner({ testIdActual, completados = {}, protocoloId = null }) {
  const proto = useMemo(() =>
    protocoloId
      ? PROTOCOLOS_ORDEN.find(p => p.id === protocoloId)
      : PROTOCOLOS_ORDEN.find(p => p.orden_recomendado.includes(testIdActual)),
    [protocoloId, testIdActual]);

  const par = useMemo(() => parRecobroPara(testIdActual), [testIdActual]);
  const siguienteId = useMemo(
    () => testIdActual ? siguienteTestRecomendado(testIdActual, proto?.id) : null,
    [testIdActual, proto]
  );
  const interferencia = useMemo(
    () => detectarInterferencia(testIdActual, siguienteId),
    [testIdActual, siguienteId]
  );

  /* Si esta prueba es un recobro, calcular si ya pasaron los minutos requeridos */
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!par) return;
    const id = setInterval(() => setNow(Date.now()), 5000);
    return () => clearInterval(id);
  }, [par]);

  const codifTs = par ? completados[par.codificacion] : null;
  const minutosTranscurridos = par && codifTs
    ? Math.round((now - codifTs) / 60000)
    : null;
  const minutosFaltantes = par && minutosTranscurridos != null
    ? Math.max(0, par.min_minutos - minutosTranscurridos)
    : null;
  const recobroListo = par
    ? (minutosTranscurridos != null && minutosFaltantes === 0)
    : true;

  if (!proto && !par) return null;

  return (
    <div className="rounded-lg border-l-[3px] p-3 mb-3"
      style={{
        borderColor: par && !recobroListo ? "#dc2626" : "#0D9488",
        background: par && !recobroListo ? "rgba(220,38,38,0.04)" : "rgba(13,148,136,0.04)",
      }}>

      {/* Banner principal: hito clínico actual */}
      {proto && (
        <div className="flex items-start gap-2 mb-2">
          <I name="route" style={{ color: "#0D9488", fontSize: 18 }} />
          <div className="flex-1 min-w-0">
            <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "#0D9488" }}>
              Protocolo: {proto.nombre}
            </p>
          </div>
        </div>
      )}

      {/* Bloque de RECOBRO con timer */}
      {par && (
        <div className="rounded p-2 mt-1"
          style={{ background: recobroListo ? "rgba(16,185,129,0.08)" : "rgba(220,38,38,0.06)" }}>
          <div className="flex items-center gap-2 mb-1">
            <I name={recobroListo ? "check_circle" : "timer"} fill
              style={{ color: recobroListo ? "#10b981" : "#dc2626", fontSize: 18 }} />
            <p className="text-xs font-bold flex-1" style={{ color: recobroListo ? "#047857" : "#7f1d1d" }}>
              {recobroListo
                ? `✓ Recobro diferido habilitado — ${par.nombre}`
                : codifTs
                  ? `⏱ Aún no — recobro requiere ≥${par.min_minutos} min desde codificación`
                  : `⚠ No se registró la codificación (${par.codificacion}) — el recobro NO debería aplicarse aún`
              }
            </p>
          </div>
          {codifTs && (
            <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
              Codificación aplicada: {new Date(codifTs).toLocaleTimeString("es-CO", {hour: "2-digit", minute: "2-digit"})}
              {minutosTranscurridos != null && (
                <> · Han pasado <strong>{minutosTranscurridos} min</strong>
                {minutosFaltantes > 0 && <> · Faltan <strong>{minutosFaltantes} min</strong></>}
                </>
              )}
            </p>
          )}
        </div>
      )}

      {/* Advertencia de interferencia */}
      {interferencia && (
        <div className="rounded p-2 mt-2 flex items-start gap-2"
          style={{ background: "rgba(245,158,11,0.08)" }}>
          <I name="warning" fill style={{ color: "#f59e0b", fontSize: 16 }} />
          <p className="text-xs" style={{ color: "#78350f" }}>
            <strong>Interferencia clínica:</strong> {interferencia.razon}.
            Considera intercalar otra prueba antes de <strong>{nombrePrueba(interferencia.b)}</strong>.
          </p>
        </div>
      )}
    </div>
  );
}
