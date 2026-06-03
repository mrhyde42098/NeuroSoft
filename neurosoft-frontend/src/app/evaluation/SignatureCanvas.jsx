/* ═══════════════════════════════════════════════════════════════════════
 * src/app/evaluation/SignatureCanvas.jsx — Captura de firma digital
 * ───────────────────────────────────────────────────────────────────────
 * Dos modos de captura intercambiables:
 *   • Dibujar:  canvas HTML5 con soporte mouse + touch.
 *   • Subir:    archivo de imagen (PNG/JPEG) → base64.
 *
 * En ambos casos onChange devuelve un Data URL base64 listo para enviar
 * al endpoint /api/v1/advanced/config/profesionales/:id/firma
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState } from "react";
import { I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const MAX_BYTES = 250 * 1024; // 250 KB — alineado a settings.max_firma_kb del backend

export default function SignatureCanvas({ value, onChange }) {
  const ref = useRef(null);
  const fileRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [mode, setMode] = useState("draw"); // "draw" | "upload"
  const [err, setErr] = useState("");

  /* Cargar valor inicial dentro del canvas. */
  useEffect(() => {
    if (mode !== "draw") return;
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext("2d");
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#1e293b";
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, c.width, c.height);
    if (value && value.startsWith("data:image")) {
      const img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 0, c.width, c.height);
      img.src = value;
    }
  }, [mode]);

  /* ─── Modo dibujar ─────────────────────────────────────────── */
  const pos = (e) => {
    const c = ref.current;
    const rect = c.getBoundingClientRect();
    const scaleX = c.width / rect.width;
    const scaleY = c.height / rect.height;
    const t = e.touches?.[0] || e;
    return { x: (t.clientX - rect.left) * scaleX, y: (t.clientY - rect.top) * scaleY };
  };
  const down = (e) => {
    e.preventDefault();
    setDrawing(true);
    const ctx = ref.current.getContext("2d");
    const { x, y } = pos(e);
    ctx.beginPath();
    ctx.moveTo(x, y);
  };
  const move = (e) => {
    if (!drawing) return;
    e.preventDefault();
    const ctx = ref.current.getContext("2d");
    const { x, y } = pos(e);
    ctx.lineTo(x, y);
    ctx.stroke();
  };
  const up = () => {
    if (!drawing) return;
    setDrawing(false);
    if (onChange) onChange(ref.current.toDataURL("image/png"));
  };
  const clearCanvas = () => {
    const c = ref.current;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, c.width, c.height);
    if (onChange) onChange("");
    setErr("");
  };

  /* ─── Modo subir archivo ───────────────────────────────────── */
  const onFile = (e) => {
    setErr("");
    const f = e.target.files?.[0];
    if (!f) return;
    if (!/^image\/(png|jpe?g|gif)$/i.test(f.type)) {
      setErr("Formato no soportado. Usa PNG, JPEG o GIF.");
      return;
    }
    if (f.size > MAX_BYTES) {
      setErr(`Archivo muy grande (${Math.round(f.size / 1024)} KB). Máximo ${MAX_BYTES / 1024} KB.`);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      if (onChange) onChange(String(reader.result || ""));
    };
    reader.onerror = () => setErr("No se pudo leer el archivo.");
    reader.readAsDataURL(f);
  };
  const removeUploaded = () => { if (onChange) onChange(""); setErr(""); if (fileRef.current) fileRef.current.value = ""; };

  return (
    <div className="space-y-2">
      {/* Selector de modo */}
      <div className="flex gap-1 p-1 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
        <button onClick={() => { setMode("draw"); setErr(""); }}
          className={`flex-1 text-[11px] font-bold py-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${mode === "draw" ? "text-white shadow" : ""}`}
          style={mode === "draw" ? { background: TEAL } : { color: "var(--ns-muted)" }}>
          <I name="draw" className="text-xs" />Dibujar
        </button>
        <button onClick={() => { setMode("upload"); setErr(""); }}
          className={`flex-1 text-[11px] font-bold py-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${mode === "upload" ? "text-white shadow" : ""}`}
          style={mode === "upload" ? { background: TEAL } : { color: "var(--ns-muted)" }}>
          <I name="upload_file" className="text-xs" />Subir imagen
        </button>
      </div>

      {/* Canvas (modo dibujar) */}
      {mode === "draw" && (
        <>
          <canvas ref={ref} width={500} height={160}
            className="w-full rounded-xl border-2 cursor-crosshair"
            style={{ borderColor: "var(--ns-card-b)", touchAction: "none", background: "#fff" }}
            onMouseDown={down} onMouseMove={move} onMouseUp={up} onMouseLeave={up}
            onTouchStart={down} onTouchMove={move} onTouchEnd={up} />
          <div className="flex justify-between items-center">
            <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
              <I name="touch_app" className="text-xs mr-1" />Firme con el mouse, lápiz óptico o dedo
            </p>
            <button onClick={clearCanvas} className="text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-red-50 text-red-500">
              <I name="refresh" className="text-xs mr-1" />Limpiar
            </button>
          </div>
        </>
      )}

      {/* Upload (modo subir) */}
      {mode === "upload" && (
        <div className="space-y-2">
          <div className="rounded-xl border-2 border-dashed p-6 text-center"
            style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
            {value && value.startsWith("data:image") ? (
              <div className="flex flex-col items-center gap-3">
                <img src={value} alt="firma cargada" className="max-h-28 rounded-lg bg-white p-2 border" style={{ borderColor: "var(--ns-card-b)" }} />
                <div className="flex gap-2">
                  <button onClick={() => fileRef.current?.click()} className="text-[11px] font-bold px-3 py-1.5 rounded-lg hover:bg-gray-100" style={{ color: TEAL }}>
                    <I name="swap_horiz" className="text-xs mr-1" />Cambiar
                  </button>
                  <button onClick={removeUploaded} className="text-[11px] font-bold px-3 py-1.5 rounded-lg hover:bg-red-50 text-red-500">
                    <I name="delete" className="text-xs mr-1" />Quitar
                  </button>
                </div>
              </div>
            ) : (
              <>
                <I name="cloud_upload" className="text-3xl mb-2" style={{ color: "var(--ns-muted)" }} />
                <p className="text-xs font-bold mb-1" style={{ color: "var(--ns-text)" }}>
                  Sube tu firma como imagen
                </p>
                <p className="text-[10px] mb-3" style={{ color: "var(--ns-muted)" }}>
                  PNG, JPEG o GIF · máximo 250 KB
                </p>
                <button onClick={() => fileRef.current?.click()}
                  className="px-4 py-2 rounded-xl text-white text-xs font-bold transition-all hover:shadow-md"
                  style={{ background: TEAL }}>
                  <I name="upload_file" className="text-sm mr-1" />Elegir archivo
                </button>
              </>
            )}
            <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/gif" onChange={onFile} className="hidden" />
          </div>
          {err && (
            <p className="text-[11px] font-bold flex items-center gap-1 text-rose-600">
              <I name="error" className="text-xs" />{err}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
