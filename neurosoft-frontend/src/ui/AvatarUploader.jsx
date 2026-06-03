/* ═══════════════════════════════════════════════════════════════════════
 * src/ui/AvatarUploader.jsx — Subida de foto del profesional
 * ───────────────────────────────────────────────────────────────────────
 * Componente circular para subir / reemplazar la foto del profesional.
 * Valida formato y tamaño (PNG/JPEG, máx 500 KB), devuelve Data URL
 * base64 vía onChange. Estado visual: vacío con inicial, foto cargada
 * con overlay hover para reemplazar/quitar.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useRef, useState } from "react";
import { I } from "./primitives.jsx";
import { TEAL } from "./tokens.js";

const MAX_BYTES = 500 * 1024; // 500 KB

export default function AvatarUploader({ value, onChange, name = "", size = 96 }) {
  const fileRef = useRef(null);
  const [err, setErr] = useState("");

  const initial = (name || "?").trim().charAt(0).toUpperCase();

  const onFile = (e) => {
    setErr("");
    const f = e.target.files?.[0];
    if (!f) return;
    if (!/^image\/(png|jpe?g|gif|webp)$/i.test(f.type)) {
      setErr("Formato no soportado. Usa PNG, JPEG, GIF o WEBP.");
      return;
    }
    if (f.size > MAX_BYTES) {
      setErr(`Archivo muy grande (${Math.round(f.size / 1024)} KB). Máximo ${MAX_BYTES / 1024} KB.`);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => onChange?.(String(reader.result || ""));
    reader.onerror = () => setErr("No se pudo leer el archivo.");
    reader.readAsDataURL(f);
  };

  const remove = () => {
    onChange?.("");
    setErr("");
    if (fileRef.current) fileRef.current.value = "";
  };

  const hasPhoto = value && value.startsWith("data:image");

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative group cursor-pointer" style={{ width: size, height: size }}
        onClick={() => fileRef.current?.click()}
        title={hasPhoto ? "Cambiar foto" : "Subir foto"}>
        {hasPhoto ? (
          <img src={value} alt={`Foto de ${name || "profesional"}`}
            className="w-full h-full rounded-full object-cover border-4 transition-all group-hover:opacity-80"
            style={{ borderColor: `${TEAL}40`, boxShadow: `0 8px 24px -8px ${TEAL}50` }} />
        ) : (
          <div className="w-full h-full rounded-full flex items-center justify-center font-extrabold transition-all group-hover:opacity-80"
            style={{ background: `linear-gradient(135deg,${TEAL},#0F766E)`, color: "white", fontSize: size * 0.4, border: `4px solid ${TEAL}40`, boxShadow: `0 8px 24px -8px ${TEAL}50` }}>
            {initial}
          </div>
        )}
        {/* Overlay con icono al pasar el cursor */}
        <div className="absolute inset-0 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all pointer-events-none"
          style={{ background: "rgba(15,23,42,0.5)" }}>
          <I name={hasPhoto ? "photo_camera" : "add_a_photo"} fill className="text-white text-2xl" />
        </div>
        <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/gif,image/webp"
          onChange={onFile} className="hidden" />
      </div>

      {/* Botones bajo el avatar */}
      {hasPhoto ? (
        <div className="flex gap-1">
          <button onClick={() => fileRef.current?.click()}
            className="text-[10px] font-bold px-2.5 py-1 rounded-lg hover:bg-gray-100 transition-all"
            style={{ color: TEAL }}>
            <I name="swap_horiz" className="text-xs mr-0.5" />Cambiar
          </button>
          <button onClick={remove}
            className="text-[10px] font-bold px-2.5 py-1 rounded-lg hover:bg-red-50 text-red-500 transition-all">
            <I name="delete" className="text-xs mr-0.5" />Quitar
          </button>
        </div>
      ) : (
        <button onClick={() => fileRef.current?.click()}
          className="text-[10px] font-bold px-3 py-1 rounded-lg transition-all"
          style={{ color: TEAL }}>
          <I name="upload" className="text-xs mr-0.5" />Subir foto
        </button>
      )}

      {err && (
        <p className="text-[10px] font-bold flex items-center gap-1 text-rose-600 max-w-[160px] text-center leading-tight">
          <I name="error" className="text-xs" />{err}
        </p>
      )}
    </div>
  );
}
