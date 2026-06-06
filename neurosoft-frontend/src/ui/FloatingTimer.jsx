/* Widget de cronómetro — modo embebido (guía clínica) o flotante arrastrable */
import React, { useEffect, useRef, useState } from "react";
import { I } from "./primitives.jsx";
import { safeLS } from "../utils/safeLS.js";

const POS_KEY = "ns_floating_timer_pos";
const PIN_KEY = "ns_floating_timer_pinned";

function fmt(s) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

export default function FloatingTimer({
  timer,
  timerOn,
  maxTime = 300,
  onStart,
  onPause,
  onReset,
  visible = true,
  embedded = false,
}) {
  const [minimized, setMinimized] = useState(false);
  const [pinned, setPinned] = useState(() => !embedded && safeLS.get(PIN_KEY) === "1");
  const [pos, setPos] = useState(() => {
    if (embedded) return { x: null, y: null };
    try {
      const raw = safeLS.get(POS_KEY);
      if (raw) return JSON.parse(raw);
    } catch { /* ignore */ }
    return { x: null, y: null };
  });
  const dragRef = useRef(null);
  const dragging = useRef(false);
  const offset = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (!embedded && pos.x != null) safeLS.set(POS_KEY, JSON.stringify(pos));
  }, [pos, embedded]);
  useEffect(() => {
    if (!embedded) safeLS.set(PIN_KEY, pinned ? "1" : "0");
  }, [pinned, embedded]);

  if (!visible) return null;

  const pct = Math.max(0, Math.min(timer / Math.max(maxTime, 1), 1));
  const remaining = Math.max(0, maxTime - timer);
  const over = maxTime > 0 && timer > maxTime;
  const warning = !over && maxTime > 0 && pct >= 0.85;
  const ringColor = over ? "#ef4444" : warning ? "#f59e0b" : "#2dd4bf";
  const R = embedded ? 44 : 52;
  const C = 2 * Math.PI * R;

  const capturePosition = () => {
    if (embedded || !dragRef.current) return;
    const rect = dragRef.current.getBoundingClientRect();
    setPos({ x: rect.left, y: rect.top });
  };

  const togglePin = () => {
    if (embedded) return;
    setPinned((p) => {
      if (!p) capturePosition();
      return !p;
    });
  };

  const onPointerDown = (e) => {
    if (embedded || pinned) return;
    if (e.target.closest("button")) return;
    dragging.current = true;
    const rect = dragRef.current.getBoundingClientRect();
    offset.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    e.currentTarget.setPointerCapture?.(e.pointerId);
  };
  const onPointerMove = (e) => {
    if (!dragging.current || embedded) return;
    setPos({
      x: Math.max(8, e.clientX - offset.current.x),
      y: Math.max(8, e.clientY - offset.current.y),
    });
  };
  const onPointerUp = () => { dragging.current = false; };

  const style = embedded
    ? { position: "relative", zIndex: 1 }
    : {
        position: "fixed",
        zIndex: 60,
        ...(pos.x != null
          ? { left: pos.x, top: pos.y, right: "auto", bottom: "auto" }
          : { right: 24, bottom: 100 }),
      };

  if (minimized && !embedded) {
    return (
      <button
        type="button"
        ref={dragRef}
        style={style}
        className={`px-4 py-2 rounded-full font-mono text-sm font-bold text-white shadow-lg ${over ? "ns-pulse-red" : ""}`}
        onClick={() => setMinimized(false)}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        aria-label="Expandir cronómetro"
      >
        {fmt(timer)} {timerOn ? "▶" : "⏸"}
      </button>
    );
  }

  return (
    <div
      ref={dragRef}
      style={style}
      className={`select-none w-full ${over ? "ns-pulse-red" : ""}`}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      role="timer"
      aria-live="polite"
    >
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-2xl ${embedded || pinned ? "cursor-default" : "cursor-grab active:cursor-grabbing"}`}
        style={{
          background: over
            ? "linear-gradient(135deg,#7f1d1d,#1e293b)"
            : "linear-gradient(135deg,#0f2a3d,#1e293b)",
          boxShadow: over
            ? "0 0 60px -12px #ef4444"
            : embedded
            ? "0 4px 12px -4px rgba(13,148,136,0.35)"
            : "0 8px 24px -8px rgba(13,148,136,0.4)",
        }}
      >
        <div className="relative flex items-center justify-center shrink-0" style={{ width: embedded ? 88 : 100, height: embedded ? 88 : 100 }}>
          <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 120 120">
            <defs>
              <linearGradient id="ns-clk-grad-float" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor={ringColor} />
                <stop offset="100%" stopColor={ringColor} stopOpacity="0.5" />
              </linearGradient>
            </defs>
            <circle cx="60" cy="60" r={R} fill="transparent" stroke="#1e3a4d" strokeWidth="7" />
            <circle
              cx="60" cy="60" r={R} fill="transparent"
              stroke="url(#ns-clk-grad-float)" strokeWidth="7"
              strokeDasharray={`${pct * C} ${C}`}
              strokeLinecap="round"
            />
          </svg>
          <div className="flex flex-col items-center pointer-events-none">
            <span className={`${embedded ? "text-lg" : "text-xl"} font-mono font-extrabold text-white tabular-nums leading-none`}>
              {fmt(timer)}
            </span>
            {maxTime > 0 && (
              <span className="text-[10px] mt-1 font-mono" style={{ color: over ? "#fca5a5" : "#94a3b8" }}>
                {over ? `+${fmt(timer - maxTime)}` : fmt(remaining)}
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-col items-stretch gap-2 flex-1">
          <div className="flex gap-1.5 flex-wrap">
            <button type="button" onClick={onStart} disabled={timerOn}
              className="w-9 h-9 rounded-xl bg-teal-600 text-white flex items-center justify-center disabled:opacity-40"
              title="Iniciar (Espacio)" aria-label="Iniciar">
              <I name="play_arrow" fill />
            </button>
            <button type="button" onClick={onPause} disabled={!timerOn}
              className="w-9 h-9 rounded-xl bg-amber-500 text-white flex items-center justify-center disabled:opacity-40"
              title="Pausa" aria-label="Pausar">
              <I name="pause" fill />
            </button>
            <button type="button" onClick={onReset}
              className="w-9 h-9 rounded-xl bg-slate-600 text-white flex items-center justify-center"
              title="Reiniciar" aria-label="Reiniciar">
              <I name="restart_alt" />
            </button>
            {!embedded && (
              <button type="button" onClick={togglePin}
                className={`w-9 h-9 rounded-xl text-white flex items-center justify-center ${pinned ? "bg-teal-600" : "bg-slate-700/80"}`}
                title={pinned ? "Desfijar (puede arrastrar)" : "Fijar en esta posición"}
                aria-label="Fijar cronómetro">
                <I name="push_pin" fill={pinned} />
              </button>
            )}
            {!embedded && (
              <button type="button" onClick={() => setMinimized(true)}
                className="w-9 h-9 rounded-xl bg-slate-700/80 text-white flex items-center justify-center"
                title="Minimizar" aria-label="Minimizar">
                <I name="remove" />
              </button>
            )}
          </div>
          <span
            className={`text-[9px] font-bold uppercase tracking-widest text-center px-2 py-1 rounded-lg ${
              over ? "bg-red-500/20 text-red-200" :
              warning ? "bg-amber-500/20 text-amber-200" :
              timerOn ? "bg-teal-500/20 text-teal-200" :
              "bg-slate-500/20 text-slate-300"
            }`}
          >
            {over ? "TIEMPO EXCEDIDO" : warning ? "Casi se acaba" : timerOn ? "Grabando" : "En pausa"}
          </span>
        </div>
      </div>
    </div>
  );
}
