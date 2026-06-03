/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/UpdateTab.jsx
 * ───────────────────────────────────────────────────────────────────────
 * Sistema de actualizacion manual offline.
 *
 * El profesional (Johan) genera un archivo .nsupdate desde su PC con:
 *   python build.py --make-update
 *
 * El clinico sube ese archivo aqui y la app se actualiza automaticamente.
 * Despues de actualizar, se muestra el changelog UNA sola vez.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useState } from "react";
import { api } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Btn, Card, I, MsgBanner } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { safeLS } from "../../utils/safeLS.js";
import WhatNewModal from "../dashboard/WhatNewModal.jsx";

export default function UpdateTab() {
  const toast = useToast();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showChangelog, setShowChangelog] = useState(false);

  /* Detectar si acaba de aplicarse una actualizacion */
  React.useEffect(() => {
    api.get("/health").then((h) => {
      const current = h?.version || "";
      const lastSeen = safeLS.get("ns_last_seen_version") || "";
      if (current && current !== lastSeen && lastSeen) {
        setShowChangelog(true);
      }
    }).catch(() => {});
  }, []);

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!f.name.endsWith(".nsupdate")) {
      setError("El archivo debe tener extension .nsupdate");
      return;
    }
    if (f.size > 200 * 1024 * 1024) {
      setError("Archivo demasiado grande (max 200 MB)");
      return;
    }
    setFile(f);
    setError(null);
    setResult(null);
  };

  const upload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch("/api/v1/system/update", {
        method: "POST",
        headers: { Authorization: "Bearer " + (localStorage.getItem("ns_token") || "") },
        body: fd,
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || "Error " + r.status);
      setResult(j);
      toast.success("Actualizacion aplicada. Recargando...");
      setTimeout(() => location.reload(), 2500);
    } catch (e) {
      setError(e.message || "Error al aplicar actualizacion");
    }
    setUploading(false);
  };

  return (
    <div className="space-y-6">
      <WhatNewModal show={showChangelog} onClose={() => setShowChangelog(false)} />

      <div>
        <h3 className="font-bold text-lg flex items-center gap-2" style={{ color: "var(--ns-text)" }}>
          <I name="system_update" className="text-2xl" style={{ color: TEAL }} />
          Actualizar Sistema
        </h3>
        <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
          Sube un archivo <code className="ns-mono text-xs px-1.5 py-0.5 rounded" style={{ background: "var(--ns-subtle)" }}>.nsupdate</code> proporcionado
          por el desarrollador para actualizar NeuroSoft App a una nueva version.
        </p>
      </div>

      <Card className="p-8 text-center space-y-6 border-2 border-dashed rounded-2xl"
        style={{ borderColor: file ? TEAL : "var(--ns-card-b)", background: file ? `${TEAL}05` : "var(--ns-card)" }}>
        <div className="w-20 h-20 mx-auto rounded-2xl flex items-center justify-center"
          style={{ background: file ? `${TEAL}15` : "var(--ns-subtle)" }}>
          <I name={file ? "upload_file" : "cloud_upload"} className="text-4xl"
            style={{ color: file ? TEAL : "var(--ns-muted)" }} />
        </div>

        {!file ? (
          <>
            <div>
              <p className="font-bold text-lg" style={{ color: "var(--ns-text)" }}>
                Arrastra tu archivo .nsupdate aqui
              </p>
              <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
                o haz clic para seleccionarlo
              </p>
            </div>
            <label className="inline-block cursor-pointer">
              <Btn as="span">Seleccionar archivo</Btn>
              <input type="file" accept=".nsupdate" onChange={handleFile} className="hidden" />
            </label>
          </>
        ) : (
          <>
            <div>
              <p className="font-bold text-lg" style={{ color: "var(--ns-text)" }}>{file.name}</p>
              <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
                {(file.size / 1024 / 1024).toFixed(1)} MB · listo para instalar
              </p>
            </div>
            <div className="flex justify-center gap-3">
              <Btn v="outline" onClick={() => setFile(null)}>Cancelar</Btn>
              <Btn onClick={upload} disabled={uploading}>
                {uploading ? "Instalando..." : "Instalar actualizacion"}
              </Btn>
            </div>
          </>
        )}
      </Card>

      {error && <MsgBanner msg={error} onDismiss={() => setError(null)} />}

      {result && (
        <Card className="p-5 border-l-4" style={{ borderColor: "#10b981", background: "rgba(16,185,129,0.06)" }}>
          <div className="flex items-center gap-3">
            <I name="check_circle" fill className="text-2xl" style={{ color: "#10b981" }} />
            <div>
              <p className="font-bold text-sm" style={{ color: "#065f46" }}>Actualizacion aplicada</p>
              <p className="text-xs" style={{ color: "#047857" }}>Version {result.version}. El sistema se reiniciara en unos segundos.</p>
            </div>
          </div>
        </Card>
      )}

      <Card className="p-5" style={{ background: "var(--ns-subtle)" }}>
        <h4 className="font-bold text-sm mb-2 flex items-center gap-2" style={{ color: "var(--ns-text)" }}>
          <I name="info" className="text-base" style={{ color: TEAL }} />
          Como funciona
        </h4>
        <ul className="space-y-2 text-sm" style={{ color: "var(--ns-muted)" }}>
          <li className="flex items-start gap-2">
            <span className="font-bold" style={{ color: TEAL }}>1.</span>
            El desarrollador genera un archivo .nsupdate con los cambios mas recientes.
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold" style={{ color: TEAL }}>2.</span>
            Te envia el archivo por correo, WhatsApp o USB.
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold" style={{ color: TEAL }}>3.</span>
            Lo subes aqui y NeuroSoft se actualiza automaticamente.
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold" style={{ color: TEAL }}>4.</span>
            El registro de cambios aparece una sola vez para que sepas que hay de nuevo.
          </li>
        </ul>
      </Card>
    </div>
  );
}
