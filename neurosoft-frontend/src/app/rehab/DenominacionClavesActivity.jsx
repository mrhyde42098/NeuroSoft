/* ═══════════════════════════════════════════════════════════════════════
 * src/app/rehab/DenominacionClavesActivity.jsx — Denominación con claves
 * ───────────────────────────────────────────────────────────────────────
 * El paciente debe denominar una imagen/concepto.
 * Si falla: se ofrecen claves jerárquicas:
 *   Nivel 0 — Sin clave    (respuesta espontánea)
 *   Nivel 1 — Clave semántica  (categoría / función)
 *   Nivel 2 — Clave fonémica   (primera sílaba)
 *   Nivel 3 — No evocado       (necesitó el nombre completo)
 *
 * El clínico registra si la respuesta fue espontánea (0), con clave
 * semántica (1), con clave fonémica (2) o no evocado (3).
 *
 * Props: params { items: [{ word, semantic_cue, phonemic_cue }] }
 *        onFinish(result), onCancel()
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const DEFAULT_ITEMS = [
  { word: "MARIPOSA",   semantic: "Es un insecto que vuela y tiene alas coloridas.",    phonemic: "MA..." },
  { word: "TELESCOPIO", semantic: "Instrumento óptico para observar objetos lejanos.",  phonemic: "TE..." },
  { word: "CANGREJO",   semantic: "Animal marino que camina de lado y tiene pinzas.",   phonemic: "CAN..." },
  { word: "TERMÓMETRO", semantic: "Instrumento que mide la temperatura.",               phonemic: "TER..." },
  { word: "CASCADA",    semantic: "Caída de agua desde una altura.",                    phonemic: "CAS..." },
  { word: "BRÚJULA",    semantic: "Instrumento de orientación que señala el norte.",    phonemic: "BRÚ..." },
  { word: "ESPÁRRAGO",  semantic: "Verdura alargada de color verde.",                   phonemic: "ES..." },
  { word: "PELÍCANO",   semantic: "Ave grande con bolsa en el pico para pescar.",       phonemic: "PE..." },
  { word: "TROMBÓN",    semantic: "Instrumento musical de viento, familiar del trombón.", phonemic: "TROM..." },
  { word: "CINTURÓN",   semantic: "Accesorio de tela o cuero que rodea la cintura.",    phonemic: "CIN..." },
];

const LEVEL_LABELS = ["Espontánea", "Clave semántica", "Clave fonémica", "No evocado"];
const LEVEL_COLORS = ["#22c55e",    "#f59e0b",          "#f97316",        "#dc2626"];
const LEVEL_ICONS  = ["star",       "category",         "record_voice_over","block"];

export default function DenominacionClavesActivity({ params = {}, onFinish, onCancel }) {
  const items = (params.items && params.items.length > 0) ? params.items : DEFAULT_ITEMS;

  const [phase, setPhase]     = useState("intro");
  const [idx, setIdx]         = useState(0);
  const [revealed, setRevealed] = useState(0); // nivel de clave mostrado (0=ninguno)
  const [results, setResults] = useState([]); // { word, level }
  const [levelPick, setLevelPick] = useState(null);

  const item = items[idx];

  const record = (level) => {
    const newResults = [...results, { word: item.word, level }];
    setResults(newResults);
    if (idx + 1 >= items.length) {
      setPhase("done");
      onFinish?.({
        items: newResults,
        spontaneous: newResults.filter(r => r.level === 0).length,
        with_semantic: newResults.filter(r => r.level === 1).length,
        with_phonemic: newResults.filter(r => r.level === 2).length,
        not_evoked: newResults.filter(r => r.level === 3).length,
      });
    } else {
      setIdx(i => i + 1);
      setRevealed(0);
      setLevelPick(null);
    }
  };

  if (phase === "intro") return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="text-center">
        <I name="record_voice_over" className="text-5xl mb-3" style={{color:TEAL}}/>
        <h2 className="text-xl font-extrabold">Denominación con jerarquía de claves</h2>
        <p className="text-sm mt-2 text-left" style={{color:"var(--ns-muted)"}}>
          Se mostrará el nombre en pantalla (o puede usarse con imágenes físicas). El clínico registra
          en qué nivel de ayuda el paciente logró denominar:
        </p>
        <div className="mt-4 space-y-2 text-left">
          {LEVEL_LABELS.map((l,i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="material-symbols-outlined text-base" style={{color:LEVEL_COLORS[i]}}>{LEVEL_ICONS[i]}</span>
              <span className="text-xs"><b style={{color:LEVEL_COLORS[i]}}>Nivel {i}</b>: {l}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="flex gap-3 justify-center">
        <Btn v="outline" onClick={onCancel}>Cancelar</Btn>
        <Btn onClick={() => setPhase("running")}>Comenzar</Btn>
      </div>
    </Card>
  );

  if (phase === "done") {
    const summary = results.reduce((acc, r) => { acc[r.level] = (acc[r.level]||0)+1; return acc; }, {});
    return (
      <Card className="p-8 space-y-6 max-w-lg mx-auto">
        <div className="text-center"><I name="task_alt" fill className="text-5xl text-teal-500 mb-2"/><h2 className="text-lg font-extrabold">Actividad completada</h2></div>
        <div className="grid grid-cols-2 gap-3">
          {LEVEL_LABELS.map((l,i) => (
            <div key={i} className="p-4 rounded-xl text-center" style={{background:`${LEVEL_COLORS[i]}15`}}>
              <p className="text-xs uppercase font-bold" style={{color:LEVEL_COLORS[i]}}>{l}</p>
              <p className="font-extrabold text-2xl" style={{color:LEVEL_COLORS[i]}}>{summary[i]||0}</p>
            </div>
          ))}
        </div>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {results.map((r,i) => (
            <div key={i} className="flex items-center justify-between text-xs p-2 rounded-lg" style={{background:"var(--ns-subtle)"}}>
              <span className="font-bold">{r.word}</span>
              <span className="flex items-center gap-1" style={{color:LEVEL_COLORS[r.level]}}>
                <span className="material-symbols-outlined text-sm">{LEVEL_ICONS[r.level]}</span>
                {LEVEL_LABELS[r.level]}
              </span>
            </div>
          ))}
        </div>
        <Btn onClick={() => onFinish?.({ items:results, spontaneous:summary[0]||0, with_semantic:summary[1]||0, with_phonemic:summary[2]||0, not_evoked:summary[3]||0 })}>
          Guardar resultados
        </Btn>
      </Card>
    );
  }

  return (
    <Card className="p-8 space-y-6 max-w-lg mx-auto">
      <div className="flex justify-between text-xs" style={{color:"var(--ns-muted)"}}>
        <span>Ítem {idx+1}/{items.length}</span>
        <div className="flex gap-3">
          {LEVEL_LABELS.map((l,i)=>(
            <span key={i} style={{color:LEVEL_COLORS[i]}}>
              {results.filter(r=>r.level===i).length}
            </span>
          ))}
        </div>
      </div>
      {/* §H3-fix: guard div/0. */}
      <div className="w-full h-1.5 bg-gray-200 rounded-full"><div className="h-full rounded-full" style={{width:`${items.length>0?(idx/items.length)*100:0}%`,background:TEAL}}/></div>

      {/* Estímulo */}
      <div className="py-8 flex flex-col items-center gap-4 rounded-2xl" style={{background:"var(--ns-subtle)"}}>
        <p className="text-4xl font-extrabold tracking-widest">{item.word}</p>
      </div>

      {/* Claves progresivas */}
      <div className="space-y-2">
        {revealed >= 1 && (
          <div className="p-3 rounded-xl flex items-start gap-2 border-l-4" style={{borderColor:"#f59e0b",background:"#fffbeb"}}>
            <I name="category" className="text-amber-600 shrink-0"/>
            <p className="text-sm text-amber-800"><b>Clave semántica:</b> {item.semantic}</p>
          </div>
        )}
        {revealed >= 2 && (
          <div className="p-3 rounded-xl flex items-start gap-2 border-l-4" style={{borderColor:"#f97316",background:"#fff7ed"}}>
            <I name="record_voice_over" className="text-orange-600 shrink-0"/>
            <p className="text-sm text-orange-800"><b>Clave fonémica:</b> {item.phonemic}</p>
          </div>
        )}
      </div>

      {/* Botones de acción */}
      <div className="space-y-2">
        <p className="text-xs font-bold text-gray-400 uppercase">¿Cómo respondió el paciente?</p>
        <div className="grid grid-cols-2 gap-2">
          <Btn onClick={() => record(0)} className="text-xs" style={{background:LEVEL_COLORS[0]}}>
            <I name="star" className="text-sm"/>Espontánea (sin ayuda)
          </Btn>
          <Btn onClick={() => { setRevealed(1); setLevelPick(1); }} v="outline" className="text-xs" disabled={revealed >= 1}>
            <I name="category" className="text-sm"/>Mostrar clave semántica
          </Btn>
        </div>
        {revealed >= 1 && (
          <div className="grid grid-cols-2 gap-2">
            <Btn onClick={() => record(1)} className="text-xs" style={{background:LEVEL_COLORS[1]}}>
              Con clave semántica
            </Btn>
            <Btn onClick={() => { setRevealed(2); }} v="outline" className="text-xs" disabled={revealed >= 2}>
              <I name="record_voice_over" className="text-sm"/>Mostrar clave fonémica
            </Btn>
          </div>
        )}
        {revealed >= 2 && (
          <div className="grid grid-cols-2 gap-2">
            <Btn onClick={() => record(2)} className="text-xs" style={{background:LEVEL_COLORS[2]}}>
              Con clave fonémica
            </Btn>
            <Btn onClick={() => record(3)} className="text-xs" style={{background:LEVEL_COLORS[3]}}>
              No evocó la palabra
            </Btn>
          </div>
        )}
      </div>
    </Card>
  );
}
