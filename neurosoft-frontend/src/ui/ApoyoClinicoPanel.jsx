/* ═══════════════════════════════════════════════════════════════
 * src/ui/ApoyoClinicoPanel.jsx — Apoyo clínico por prueba verbatim
 * ───────────────────────────────────────────────────────────────
 * §S5.1x: Panel desplegable que se muestra junto a un ítem verbatim
 * con:
 *   1. Instrucciones resumidas de aplicación.
 *   2. Referencia exacta al manual original (página, ISBN, editorial).
 *   3. Errores frecuentes al aplicar y baremar.
 *   4. Alternativas de baremos abiertos cuando existen.
 *
 * NO reemplaza al manual original. Es un apoyo complementario para
 * reducir errores comunes; el clínico SIEMPRE debe tener acceso al
 * manual físico/digital oficial bajo su licencia.
 *
 * Uso:
 *   <ApoyoClinicoPanel testId="AdWAISV" inline />
 *   <ApoyoClinicoPanel testId="NiWiscDC" variant="compact" />
 * ═══════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { I } from "./primitives.jsx";
import { metadatosVerbatim, esVerbatim } from "../data/pearsonProtected.js";

/* Instrucciones resumidas por test. Construidas a partir del manual
 * (sin reproducir texto verbatim). Sirven como recordatorio rápido. */
const INSTRUCCIONES_RESUMIDAS = {
  AdWAISCC: "Presentar la clave de símbolos con 90 segundos por ítem. No corregir; puntuar aciertos hasta el último ítem completado en el tiempo. La prueba evalúa velocidad de procesamiento grafomotor.",
  AdWAISV: "Pedir definición de cada palabra. Puntuar 0/1/2 según precisión. No dar pistas. Evaluar conocimiento léxico cristalizado.",
  AdWAISRO: "Leer cada secuencia a 1 dígito/segundo. Solo una repetición por ensayo. Inverso y ordenamiento son停止 temprano tras 2 fallos consecutivos en un bloque.",
  AdWAISFI: "Mostrar cada lámina 20 segundos. Puntuar 0/1 según presencia de detalles esenciales. Evalúa percepción visual y atención al detalle.",
  AdWAISHI: "Leer cada historia en voz normal. Paciente evoca inmediatamente y luego en diferido. Puntuar literales y tema. Evalúa memoria lógica verbal.",
  AdWAISI: "Preguntas de cultura general. No admitir respuestas aproximadas en ítems clave. 停止 en 5 fallos consecutivos.",
  AdWAISL: "Mezcla letras y números. Secuencias de longitud creciente. 停止 en 3 ceros en un bloque. Evalúa memoria de trabajo.",
  NiWiscSem: "Pedir en qué se parecen dos conceptos. Puntuar 0/1/2. No ayudar tras la consigna. Evalúa razonamiento verbal abstracto.",
  NiWiscVoc: "Definir cada palabra. 0/1/2. Evalúa conocimiento léxico y desarrollo del lenguaje.",
  NiWiscDC: "9 diseños con cubos bicolor. Tiempo: 120 s para ítems 1-4, 120 s para 5-9. 停止 tras 2 fallos consecutivos. Evalúa percepción visuoespacial y construcción.",
  NiWiscConD: "Mostrar 2-3 filas de dibujos, paciente identifica atributo común. 0/1/2. Evalúa razonamiento categorial abstracto.",
  NiWiscMat: "Figura incompleta con 5 opciones. 0/1. 停止 en 4 fallos en 5 consecutivos. Evalúa razonamiento fluido no verbal.",
  NiWiscRDD: "Dígitos en orden directo (1-8) e inverso (1-7). 停止 tras 2 fallos en un ensayo.",
  NiWiscLN: "Mezcla letras y números; paciente reordena. 停止 en 3 ceros en un bloque. Memoria de trabajo.",
  NiWiscCl: "Hoja de codificación con claves simbólicas. Niño: 120 s total. Evalúa velocidad de procesamiento.",
  NiWiscBusSim: "Buscar símbolos objetivo en filas. 2 ensayos de 60 s cada uno. 停止 tras 2 fallos consecutivos. Velocidad perceptiva.",
};

const ERRORES_FRECUENTES = {
  AdWAISCC: [
    "Cronometrar mal (no son 30 s, son 90 s por fila)",
    "Continuar después de los 90 s cuando el paciente aún escribe",
    "No contar los ítems que el paciente saltó al saltar a la siguiente fila",
  ],
  AdWAISV: [
    "Aceptar definiciones funcionales como 2 puntos (p. ej. 'bicicleta es para transportarse')",
    "No registrar respuestas literales para el informe",
    "Puntuar ejemplos dados en la consigna",
  ],
  AdWAISRO: [
    "Leer la secuencia a más de 1 dígito/segundo",
    "Dar dos ensayos cuando la consigna dice uno",
    "En ordenamiento, leer la secuencia en orden natural cuando es mixto",
  ],
  AdWAISFI: [
    "Mostrar la lámina por más de 20 s",
    "Pasar al siguiente ítem sin puntuar el actual",
    "No registrar detalles omitidos (importante para el informe)",
  ],
  AdWAISHI: [
    "No evocar inmediatamente (es parte del puntaje)",
    "Cambiar pausas al leer la historia",
    "No puntuar tema central por contenido literal exacto",
  ],
  AdWAISI: [
    "Aceptar 'no sé' sin insistir en el primer ensayo",
    "Continuar más allá de 5 fallos consecutivos",
    "No tener en cuenta nivel educativo del paciente",
  ],
  AdWAISL: [
    "Leer la secuencia muy rápido",
    "Permitir que el paciente reorganice en su cabeza en lugar de reordenar en voz alta",
    "Continuar más allá de 3 ceros consecutivos en un bloque",
  ],
  NiWiscSem: [
    "Aceptar 'se parecen' sin elaboración",
    "No puntuar 1 punto cuando hay un atributo común parcial",
    "Pasar al siguiente par sin puntuar",
  ],
  NiWiscVoc: [
    "Confundir 'uso' con 'definición' (≠ 2 puntos)",
    "Puntuar 2 puntos definiciones imprecisas pero no protocolares",
    "No usar el sistema de scoring oficial",
  ],
  NiWiscDC: [
    "No respetar el límite de 120 s (importante para baremación)",
    "Permitir rotar el modelo 3D (afecta estrategias de solución)",
    "No registrar el patrón de errores",
  ],
  NiWiscConD: [
    "No rotar la hoja después del ensayo de ejemplo",
    "Aceptar respuestas concretas en lugar de abstractas",
    "No puntuar correctamente la fila de 2 (0/1/2 también)",
  ],
  NiWiscMat: [
    "Pasar al ensayo de opción múltiple sin agotar el ensayo libre",
    "Puntuar 1 cuando la respuesta es claramente incorrecta",
    "No registrar respuestas literales",
  ],
  NiWiscRDD: [
    "Invertir el orden directo por inverso (inverso se aplica después)",
    "Continuar tras 2 fallos sin registrar el punto de suspensión",
    "Cronometrar las pausas (no es relevante para esta prueba)",
  ],
  NiWiscLN: [
    "Leer números y letras con separación visual",
    "Permitir reorganización en silencio",
    "No suspender tras 3 ceros consecutivos",
  ],
  NiWiscCl: [
    "No usar el lápiz sin borrar",
    "Hacer que el paciente levante el lápiz entre símbolos",
    "No respetar los 120 s del ensayo completo",
  ],
  NiWiscBusSim: [
    "No explicar correctamente el ensayo de práctica",
    "Cronometrar mal los 60 s de cada ensayo",
    "Puntuar correctamente el objetivo si fue marcado parcialmente",
  ],
};

/* Alternativas con baremos abiertos o públicos cuando proceda.
 * Esto es orientación; el clínico debe verificar disponibilidad. */
const ALTERNATIVAS_BAREMOS = {
  AdWAISCC: [
    { nombre: "WAIS-IV (Weschsler, 2008)", nota: "Baremos actualizados en US y Colombia. License requerida." },
    { nombre: "WISC-V Claves (2014)", nota: "Para menores. License requerida." },
  ],
  NiWiscCl: [
    { nombre: "WISC-V Claves (Weschsler, 2014)", nota: "Baremos actualizados para población general." },
    { nombre: "NEPSY-II Atenuación visual (Korkman, 2007)", nota: "Alternativa con baremos hispanoparlantes publicados." },
  ],
};

export default function ApoyoClinicoPanel({
  testId,
  variant = "full", // "full" | "compact"
  defaultOpen = false,
}) {
  const [open, setOpen] = useState(defaultOpen);
  if (!esVerbatim(testId)) return null;

  const meta = metadatosVerbatim(testId);
  const instrucciones = INSTRUCCIONES_RESUMIDAS[testId] || "Consulte el manual original.";
  const errores = ERRORES_FRECUENTES[testId] || [];
  const alternativas = ALTERNATIVAS_BAREMOS[testId] || [];

  const compact = variant === "compact";

  return (
    <div
      className="rounded-xl"
      style={{
        background: "var(--ns-subtle)",
        border: "1px solid var(--ns-card-b)",
      }}
    >
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 text-xs font-bold"
        style={{ color: "var(--ns-accent, #0D9488)" }}
        aria-expanded={open}
        aria-controls={`apoyo-${testId}`}
      >
        <span className="flex items-center gap-2">
          <I name="medical_information" />
          Apoyo clínico — {meta?.nombre || testId}
        </span>
        <I
          name={open ? "expand_less" : "expand_more"}
          className="material-symbols-outlined"
        />
      </button>

      {open && (
        <div
          id={`apoyo-${testId}`}
          className={compact ? "px-3 pb-3 space-y-2" : "p-4 space-y-3"}
        >
          {/* ─── Instrucciones ─── */}
          <section>
            <h4
              className="text-[10px] font-extrabold uppercase tracking-wider mb-1"
              style={{ color: "var(--ns-muted)" }}
            >
              Instrucciones resumidas
            </h4>
            <p className="text-xs leading-relaxed">{instrucciones}</p>
          </section>

          {/* ─── Referencia al manual ─── */}
          {meta && (
            <section>
              <h4
                className="text-[10px] font-extrabold uppercase tracking-wider mb-1"
                style={{ color: "var(--ns-muted)" }}
              >
                Manual original (referencia oficial)
              </h4>
              <div
                className="text-xs rounded-lg p-2 space-y-0.5"
                style={{
                  background: "var(--ns-card)",
                  border: "1px solid var(--ns-card-b)",
                }}
              >
                <p><strong>{meta.manual}</strong></p>
                <p className="ns-mono" style={{ color: "var(--ns-muted)" }}>
                  {meta.editorial} · {meta.anio} · ISBN {meta.isbn}
                </p>
                <p className="text-[11px]" style={{ color: "var(--ns-muted)" }}>
                  {meta.pagina}
                </p>
              </div>
              <p
                className="text-[10px] mt-1 italic"
                style={{ color: "var(--ns-muted)" }}
              >
                Verifique SIEMPRE los criterios de puntuación y suspensión
                en el manual original. Este panel NO reemplaza la consulta del manual.
              </p>
            </section>
          )}

          {/* ─── Errores frecuentes ─── */}
          {errores.length > 0 && (
            <section>
              <h4
                className="text-[10px] font-extrabold uppercase tracking-wider mb-1"
                style={{ color: "var(--ns-muted)" }}
              >
                Errores frecuentes
              </h4>
              <ul className="text-xs space-y-1 list-disc ml-4">
                {errores.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </section>
          )}

          {/* ─── Alternativas baremos ─── */}
          {alternativas.length > 0 && (
            <section>
              <h4
                className="text-[10px] font-extrabold uppercase tracking-wider mb-1"
                style={{ color: "var(--ns-muted)" }}
              >
                Alternativas de baremos abiertos
              </h4>
              <ul className="text-xs space-y-1 list-disc ml-4">
                {alternativas.map((a, i) => (
                  <li key={i}>
                    <strong>{a.nombre}</strong> — {a.nota}
                  </li>
                ))}
              </ul>
              <p
                className="text-[10px] mt-1 italic"
                style={{ color: "var(--ns-muted)" }}
              >
                Verificar disponibilidad y pertinencia de la licencia para
                su contexto clínico antes de usar baremos alternativos.
              </p>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
