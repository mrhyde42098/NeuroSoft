/* ═══════════════════════════════════════════════════════════════════════
 * UpdateTab.jsx — Actualizaciones offline (frontend .nsupdate + binario)
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useState } from "react";
import { api } from "../../api/client.js";
import { useToast } from "../../contexts.jsx";
import { Btn, Card, I, MsgBanner } from "../../ui/primitives.jsx";
import SectionCard from "../../ui/SectionCard.jsx";
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
  const [updateCheck, setUpdateCheck] = useState(null);
  const [applyingBinary, setApplyingBinary] = useState(false);

  const loadUpdateCheck = useCallback(async () => {
    try {
      const r = await api.get("/api/v1/system/update/check");
      setUpdateCheck(r);
    } catch {
      setUpdateCheck(null);
    }
  }, []);

  React.useEffect(() => {
    api.get("/health").then((h) => {
      const current = h?.version || "";
      const lastSeen = safeLS.get("ns_last_seen_version") || "";
      if (current && current !== lastSeen && lastSeen) {
        setShowChangelog(true);
      }
    }).catch(() => {});
    loadUpdateCheck();
  }, [loadUpdateCheck]);

  const handleFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!f.name.endsWith(".nsupdate")) {
      setError("El archivo debe tener extensión .nsupdate");
      return;
    }
    if (f.size > 200 * 1024 * 1024) {
      setError("Archivo demasiado grande (máx. 200 MB)");
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
      toast.success("Actualización aplicada. Recargando…");
      setTimeout(() => location.reload(), 2500);
    } catch (e) {
      setError(e.message || "Error al aplicar actualización");
    }
    setUploading(false);
  };

  const applyBinaryUpdate = async () => {
    setApplyingBinary(true);
    setError(null);
    try {
      const r = await api.post("/api/v1/system/update/apply-binary");
      setResult(r);
      toast.success("Actualización programada. Cierre NeuroSoft para completar.");
    } catch (e) {
      setError(e.message || "No se pudo programar la actualización del ejecutable");
    }
    setApplyingBinary(false);
  };

  const binaryAvailable = updateCheck?.update_available && (
    updateCheck?.artifacts?.windows_x64_dir_zip || updateCheck?.artifacts?.windows_x64_exe
  );

  return (
    <div className="space-y-6">
      <WhatNewModal show={showChangelog} onClose={() => setShowChangelog(false)} />

      <div>
        <h3 className="font-bold text-lg flex items-center gap-2" style={{ color: "var(--ns-text)" }}>
          <I name="system_update" className="text-2xl" style={{ color: TEAL }} />
          Actualizar sistema
        </h3>
        <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
          Versión actual: <strong>{updateCheck?.current_version || "—"}</strong>
          {updateCheck?.latest_version && (
            <> · Última disponible: <strong>{updateCheck.latest_version}</strong></>
          )}
        </p>
      </div>

      {binaryAvailable && (
        <Card className="p-5 border-l-4" style={{ borderColor: TEAL, background: `${TEAL}08` }}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <p className="font-bold" style={{ color: "var(--ns-text)" }}>
                Actualización de aplicación disponible
              </p>
              <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
                v{updateCheck.latest_version}
                {updateCheck.released ? ` · ${updateCheck.released}` : ""}
                {updateCheck.source ? ` · fuente: ${updateCheck.source}` : ""}
              </p>
              <p className="text-xs mt-2" style={{ color: "var(--ns-muted)" }}>
                No requiere descargar el instalador completo (~1,4 GB). Se actualiza solo la carpeta de la app.
              </p>
            </div>
            <Btn onClick={applyBinaryUpdate} disabled={applyingBinary}>
              {applyingBinary ? "Programando…" : "Instalar actualización"}
            </Btn>
          </div>
        </Card>
      )}

      {!binaryAvailable && updateCheck?.update_available && (
        <MsgBanner msg="Hay una actualización firmada, pero no incluye paquete de aplicación local. Use un archivo .nsupdate para la interfaz." />
      )}

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
                Actualizar interfaz (.nsupdate)
              </p>
              <p className="text-sm mt-1" style={{ color: "var(--ns-muted)" }}>
                Archivo ligero (~1 MB) para cambios de pantallas sin tocar el ejecutable
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
                {uploading ? "Instalando…" : "Instalar actualización"}
              </Btn>
            </div>
          </>
        )}
      </Card>

      {error && <MsgBanner msg={error} onDismiss={() => setError(null)} />}

      {result && (
        <SectionCard
          title="Actualización programada"
          icon="check_circle"
          eyebrow="Éxito"
          subtitle={result.mensaje || result.message || "Cierre la aplicación para aplicar los cambios."}
        />
      )}

      <Card className="p-5" style={{ background: "var(--ns-subtle)" }}>
        <h4 className="font-bold text-sm mb-2 flex items-center gap-2" style={{ color: "var(--ns-text)" }}>
          <I name="info" className="text-base" style={{ color: TEAL }} />
          Cómo funciona
        </h4>
        <ul className="space-y-2 text-sm" style={{ color: "var(--ns-muted)" }}>
          <li><strong>Interfaz (.nsupdate):</strong> cambios de pantallas sin reinstalar (~1 MB).</li>
          <li><strong>Aplicación (update.json):</strong> parche firmado de la carpeta NeuroSoft (~50 MB), sin Ollama.</li>
          <li><strong>USB:</strong> copie <code>update.json</code> y el ZIP junto al .exe instalado.</li>
          <li><strong>Red:</strong> configure <code>NEUROSOFT_UPDATE_URL</code> apuntando al manifest público.</li>
        </ul>
      </Card>
    </div>
  );
}
