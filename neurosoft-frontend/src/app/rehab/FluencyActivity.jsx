/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/FluencyActivity.jsx — Fluencia verbal cronometrada
 * ───────────────────────────────────────────────────────────────────────
 * Mide acceso lexical y flexibilidad cognitiva.
 *
 * Mecánica:
 *   1. Se muestra un criterio (categoría semántica o letra inicial).
 *   2. Cuenta atrás de N segundos.
 *   3. El paciente escribe palabras separadas por enter o espacio.
 *   4. Resultado: total únicas, duplicados ignorados, palabras cortas (<3 letras)
 *      no cuentan.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useMemo, useRef, useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const CRITERIOS = {
  animales: { label: "Animales", tipo: "categoria" },
  frutas:   { label: "Frutas y verduras", tipo: "categoria" },
  ropa:     { label: "Prendas de vestir", tipo: "categoria" },
  pais:     { label: "Países", tipo: "categoria" },
  letra_p:  { label: "Palabras que comiencen con P", tipo: "letra", letra: "p" },
  letra_m:  { label: "Palabras que comiencen con M", tipo: "letra", letra: "m" },
};

export default function FluencyActivity({ params = {}, onFinish, onCancel }) {
  const duration = params.duration_sec ?? 60;
  const criterio = params.criterio ?? "animales";
  const cfg = CRITERIOS[criterio] || CRITERIOS.animales;

  const [phase, setPhase] = useState("intro");
  const [text, setText] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(duration);
  const startedAtRef = useRef(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (phase !== "running") return;
    startedAtRef.current = Date.now();
    intervalRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startedAtRef.current) / 1000);
      const left = Math.max(0, duration - elapsed);
      setSecondsLeft(left);
      if (left <= 0) finish();
    }, 250);
    return () => clearInterval(intervalRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  const palabras = useMemo(() => {
    if (!text) return { unicas: [], duplicados: 0, cortas: 0, fueraCriterio: 0 };
    const tokens = text
      .split(/[\n,;\s]+/)
      .map((t) => t.trim().toLowerCase())
      .filter(Boolean);
    const set = new Set();
    let duplicados = 0;
    let cortas = 0;
    let fueraCriterio = 0;
    const unicas = [];
    for (const t of tokens) {
      if (t.length < 3) {
        cortas += 1;
        continue;
      }
      if (cfg.tipo === "letra" && !t.startsWith(cfg.letra)) {
        fueraCriterio += 1;
        continue;
      }
      if (set.has(t)) {
        duplicados += 1;
        continue;
      }
      set.add(t);
      unicas.push(t);
    }
    return { unicas, duplicados, cortas, fueraCriterio };
  }, [text, cfg]);

  const finish = () => {
    clearInterval(intervalRef.current);
    const elapsed = Math.min(duration, Math.floor((Date.now() - startedAtRef.current) / 1000));
    const score = palabras.unicas.length; // total de palabras válidas únicas
    const result = {
      score,
      aciertos: palabras.unicas.length,
      errores: palabras.duplicados + palabras.fueraCriterio + palabras.cortas,
      duracion_seg: elapsed,
      total_validas: palabras.unicas.length,
      duplicados: palabras.duplicados,
      cortas: palabras.cortas,
      fuera_criterio: palabras.fueraCriterio,
      palabras_lista: palabras.unicas,
      criterio,
      params: { duration_sec: duration, criterio },
    };
    setPhase("done");
    if (onFinish) onFinish(result);
  };

  /* ─── INTRO ─────────────────────────────────────────────── */
  if (phase === "intro") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: `${TEAL}15`, color: TEAL }}
        >
          <I name="edit_note" className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-3">Fluencia verbal</h3>
        <p className="text-sm leading-relaxed mb-6" style={{ color: "var(--ns-muted)" }}>
          Tienes <strong>{duration} segundos</strong> para escribir tantas palabras como puedas
          que cumplan este criterio:
        </p>
        <div
          className="rounded-2xl p-6 mb-8"
          style={{ background: `${TEAL}10`, border: `2px solid ${TEAL}40` }}
        >
          <p className="text-xl font-extrabold" style={{ color: TEAL }}>
            {cfg.label}
          </p>
        </div>
        <p className="text-xs mb-8" style={{ color: "var(--ns-muted)" }}>
          Separa cada palabra con un Enter o un espacio. No se cuentan repetidas
          ni palabras de menos de 3 letras.
        </p>
        <div className="flex justify-center gap-3">
          {onCancel && (
            <Btn v="outline" onClick={onCancel}>
              Cancelar
            </Btn>
          )}
          <Btn onClick={() => setPhase("running")}>
            <I name="play_arrow" />
            Comenzar
          </Btn>
        </div>
      </Card>
    );
  }

  /* ─── DONE ──────────────────────────────────────────────── */
  if (phase === "done") {
    return (
      <Card className="p-8 max-w-2xl mx-auto text-center">
        <div
          className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
          style={{ background: "#10b98115", color: "#10b981" }}
        >
          <I name="check_circle" fill className="text-4xl" />
        </div>
        <h3 className="text-2xl font-extrabold mb-2">¡Tiempo!</h3>
        <p className="text-sm mb-6" style={{ color: "var(--ns-muted)" }}>
          Has escrito <strong>{palabras.unicas.length}</strong> palabras válidas
          que cumplen el criterio.
        </p>
        <div className="grid grid-cols-3 gap-3 mb-6">
          <Card className="p-4">
            <p className="text-3xl font-extrabold" style={{ color: TEAL }}>{palabras.unicas.length}</p>
            <p className="text-[10px] font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Válidas
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-3xl font-extrabold text-orange-500">{palabras.duplicados}</p>
            <p className="text-[10px] font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Repetidas
            </p>
          </Card>
          <Card className="p-4">
            <p className="text-3xl font-extrabold text-red-500">{palabras.fueraCriterio + palabras.cortas}</p>
            <p className="text-[10px] font-bold uppercase tracking-wider mt-1" style={{ color: "var(--ns-muted)" }}>
              Fuera de criterio
            </p>
          </Card>
        </div>
        <div className="flex flex-wrap gap-1.5 justify-center">
          {palabras.unicas.map((p, i) => (
            <span key={i} className="text-xs font-bold px-2 py-0.5 rounded" style={{ background: `${TEAL}15`, color: TEAL }}>
              {p}
            </span>
          ))}
        </div>
      </Card>
    );
  }

  /* ─── RUNNING ───────────────────────────────────────────── */
  const pctTime = ((duration - secondsLeft) / duration) * 100;
  const urgent = secondsLeft <= 10;
  return (
    <div className="max-w-2xl mx-auto">
      <Card className="p-6 mb-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
              Criterio
            </p>
            <p className="text-base font-extrabold" style={{ color: TEAL }}>
              {cfg.label}
            </p>
          </div>
          <div className="text-right">
            <p
              className="text-5xl font-extrabold tabular-nums"
              style={{ color: urgent ? "#dc2626" : TEAL }}
            >
              {secondsLeft}
            </p>
            <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
              segundos
            </p>
          </div>
        </div>
        <div className="h-2 rounded-full" style={{ background: "var(--ns-subtle)" }}>
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{
              width: `${pctTime}%`,
              background: urgent ? "#dc2626" : TEAL,
            }}
          />
        </div>
      </Card>

      <Card className="p-2">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          autoFocus
          placeholder={`Escribe palabras separadas por Enter...`}
          className="w-full px-4 py-3 rounded-xl text-base bg-transparent border-none focus:outline-none focus:ring-0 resize-none"
          style={{ color: "var(--ns-text)", minHeight: "200px" }}
        />
      </Card>

      <div className="flex items-center justify-between mt-4">
        <span className="text-xs font-bold" style={{ color: TEAL }}>
          {palabras.unicas.length} palabra(s) válidas
        </span>
        <Btn v="outline" onClick={finish}>
          Terminar antes
        </Btn>
      </div>
    </div>
  );
}
