/* ═══════════════════════════════════════════════════════════════════════
 * TowerOfLondonActivity.jsx — Rehabilitación ejecutiva (planificación)
 * ───────────────────────────────────────────────────────────────────────
 * Torre de Londres simplificada: 3 postes, 3 discos de colores.
 * El paciente mueve discos con el mínimo de movimientos posibles para
 * replicar el estado objetivo. Incrementa dificultad (4 → 6 moves).
 *
 * Props: { params, onFinish, onCancel }
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState, useCallback, useEffect } from "react";
import { Btn, Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

/* ── Configuración de niveles ── */
const LEVELS = [
  /* nivel 1 — 2 movimientos */
  { goal: [[2],[1,0],[]], moves: 2 },
  /* nivel 2 — 3 movimientos */
  { goal: [[],[2,1,0],[]], moves: 3 },
  /* nivel 3 — 4 movimientos */
  { goal: [[0],[],[2,1]], moves: 4 },
  /* nivel 4 — 5 movimientos */
  { goal: [[1,0],[2],[]], moves: 5 },
  /* nivel 5 — 6 movimientos */
  { goal: [[],[0],[2,1]], moves: 6 },
];

const DISK_COLORS = ["#dc2626", "#2563eb", "#10b981"];
const DISK_LABELS = ["Rojo", "Azul", "Verde"];
const POST_W = 14, DISK_H = 22, BASE_Y = 160, POST_H = 120, GAP = 110;

function TowerSVG({ pegs, selected, onSelectPost }) {
  return (
    <svg viewBox="0 0 360 200" className="w-full" style={{ maxHeight: 220 }}>
      {/* Base */}
      <rect x="10" y="170" width="340" height="14" fill="#1e293b" rx="4"/>
      {[0,1,2].map(p => {
        const cx = 65 + p * GAP;
        const stack = pegs[p] || [];
        return (
          <g key={p} onClick={() => onSelectPost(p)} style={{ cursor: "pointer" }}>
            {/* Poste */}
            <rect
              x={cx - POST_W/2} y={BASE_Y - POST_H} width={POST_W} height={POST_H}
              fill={selected === p ? "#0D9488" : "#64748b"} rx="4"
              style={{ transition: "fill .15s" }}
            />
            {/* Discos (índice 0 = fondo, último = tope) */}
            {stack.map((diskId, di) => {
              const w = 40 + diskId * 20;
              const y = BASE_Y - DISK_H - di * (DISK_H + 3);
              return (
                <rect
                  key={diskId} x={cx - w/2} y={y} width={w} height={DISK_H}
                  fill={DISK_COLORS[diskId]} rx="6"
                  stroke={selected === p ? "#fff" : "none"} strokeWidth="2"
                />
              );
            })}
            {/* Etiqueta del poste */}
            <text x={cx} y="194" textAnchor="middle" fontSize="9" fill="#94a3b8">
              {["A","B","C"][p]}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export default function TowerOfLondonActivity({ params = {}, onFinish, onCancel }) {
  const maxLevel  = Math.min(params.levels ?? 5, LEVELS.length);
  const [level,   setLevel]   = useState(0);
  const [pegs,    setPegs]    = useState([[0,1,2],[],[]]);
  const [sel,     setSel]     = useState(null);   // poste seleccionado
  const [moves,   setMoves]   = useState(0);
  const [history, setHistory] = useState([]);     // para deshacer
  const [done,    setDone]    = useState(false);
  const [scores,  setScores]  = useState([]);
  const [started, setStarted] = useState(false);

  const goal     = LEVELS[level]?.goal ?? [];
  const minMoves = LEVELS[level]?.moves ?? 0;

  const pegsMatch = useCallback((a, b) =>
    a.every((peg, i) => peg.length === b[i].length && peg.every((v, j) => v === b[i][j])),
  []);

  /* Verificar solución tras cada movimiento */
  useEffect(() => {
    if (!started) return;
    if (pegsMatch(pegs, goal)) {
      const efficiency = Math.max(0, Math.round((minMoves / Math.max(moves, minMoves)) * 100));
      const newScores  = [...scores, { level: level + 1, moves, minMoves, efficiency }];
      setScores(newScores);
      if (level + 1 >= maxLevel) {
        setDone(true);
      } else {
        setTimeout(() => {
          setLevel(l => l + 1);
          setPegs([[0,1,2],[],[]]);
          setSel(null);
          setMoves(0);
          setHistory([]);
        }, 800);
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pegs]);

  function handlePost(p) {
    if (sel === null) {
      /* Seleccionar poste si tiene discos */
      if (pegs[p].length > 0) setSel(p);
      return;
    }
    if (sel === p) { setSel(null); return; }

    const from = pegs[sel], to = pegs[p];
    const top  = from[from.length - 1];
    /* Validar: el disco superior del destino debe ser mayor */
    if (to.length > 0 && to[to.length - 1] < top) {
      setSel(null); return;
    }
    /* Mover */
    setHistory(h => [...h, pegs.map(pp => [...pp])]);
    const next = pegs.map(pp => [...pp]);
    next[p].push(next[sel].pop());
    setPegs(next);
    setMoves(m => m + 1);
    setSel(null);
  }

  function undo() {
    if (history.length === 0) return;
    const prev = history[history.length - 1];
    setHistory(h => h.slice(0, -1));
    setPegs(prev);
    setMoves(m => Math.max(0, m - 1));
    setSel(null);
  }

  function reset() {
    setPegs([[0,1,2],[],[]]);
    setSel(null);
    setMoves(0);
    setHistory([]);
  }

  if (!started) {
    return (
      <Card className="p-8 max-w-xl mx-auto space-y-6 text-center">
        <I name="account_tree" style={{ color: TEAL, fontSize: 48 }}/>
        <h2 className="text-xl font-extrabold">Torre de Londres</h2>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>
          Mueva los discos uno a uno hasta que el lado derecho iguale el objetivo.
          Un disco mayor <strong>nunca</strong> puede ir encima de uno menor.
          Intente usar el <strong>mínimo de movimientos posibles</strong>.
        </p>
        <p className="text-sm font-bold" style={{ color: TEAL }}>
          {maxLevel} niveles de dificultad creciente
        </p>
        <Btn onClick={() => setStarted(true)}>Comenzar</Btn>
        <button onClick={onCancel} className="block mx-auto text-xs mt-2" style={{ color: "var(--ns-muted)" }}>Cancelar</button>
      </Card>
    );
  }

  if (done) {
    const avg = scores.length ? Math.round(scores.reduce((s, r) => s + r.efficiency, 0) / scores.length) : 0;
    return (
      <Card className="p-8 max-w-xl mx-auto space-y-6 text-center">
        <I name="emoji_events" fill style={{ color: "#f59e0b", fontSize: 56 }}/>
        <h2 className="text-xl font-extrabold">¡Completado!</h2>
        <p className="text-sm" style={{ color: "var(--ns-muted)" }}>Eficiencia promedio de planificación</p>
        <p className="text-5xl font-extrabold" style={{ color: avg >= 80 ? "#10b981" : avg >= 60 ? "#f59e0b" : "#dc2626" }}>
          {Math.round(avg)}%
        </p>
        <div className="space-y-1 text-left">
          {scores.map((s, i) => (
            <div key={i} className="flex items-center justify-between text-xs px-4 py-2 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
              <span className="font-bold">Nivel {s.level}</span>
              <span>{s.moves} movimientos (mín. {s.minMoves})</span>
              <span className="font-extrabold" style={{ color: s.efficiency >= 80 ? "#10b981" : "#f59e0b" }}>{s.efficiency}%</span>
            </div>
          ))}
        </div>
        <Btn onClick={() => onFinish({ scores, avg_efficiency: Math.round(avg) })}>
          Guardar resultados
        </Btn>
      </Card>
    );
  }

  return (
    <Card className="p-6 max-w-2xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-extrabold">Torre de Londres · Nivel {level + 1}/{maxLevel}</p>
          <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
            Mín. de movimientos: <strong>{minMoves}</strong> · Usados: <strong>{moves}</strong>
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={undo} disabled={history.length === 0}
            className="px-3 py-1.5 rounded-full text-xs font-bold border disabled:opacity-40"
            style={{ borderColor: "var(--ns-card-b)" }}>
            <I name="undo" className="text-sm"/> Deshacer
          </button>
          <button onClick={reset} className="px-3 py-1.5 rounded-full text-xs font-bold border"
            style={{ borderColor: "var(--ns-card-b)" }}>
            <I name="restart_alt" className="text-sm"/> Reiniciar
          </button>
        </div>
      </div>

      {/* Estado actual */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>Estado actual</p>
        <TowerSVG pegs={pegs} selected={sel} onSelectPost={handlePost}/>
      </div>

      {/* Objetivo */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>Objetivo (copie esta configuración)</p>
        <TowerSVG pegs={goal} selected={null} onSelectPost={() => {}}/>
      </div>

      {/* Instrucción */}
      {sel !== null ? (
        <p className="text-xs text-center font-bold" style={{ color: TEAL }}>
          Disco de poste {["A","B","C"][sel]} seleccionado — toque el poste destino
        </p>
      ) : (
        <p className="text-xs text-center" style={{ color: "var(--ns-muted)" }}>
          Toque un poste con discos para seleccionar el disco superior
        </p>
      )}

      {/* Leyenda de colores */}
      <div className="flex gap-3 justify-center flex-wrap">
        {DISK_COLORS.map((c, i) => (
          <span key={i} className="flex items-center gap-1.5 text-xs font-bold">
            <span className="inline-block w-5 h-4 rounded" style={{ background: c }}/>
            {DISK_LABELS[i]}
          </span>
        ))}
      </div>

      <button onClick={onCancel} className="w-full text-xs mt-2" style={{ color: "var(--ns-muted)" }}>
        Salir de la actividad
      </button>
    </Card>
  );
}
