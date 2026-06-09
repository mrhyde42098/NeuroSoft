/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/BackupTab.jsx — Respaldo y restauracion de la base de datos
 * QW-8: schedule configurable + backups cifrados unificados
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useState } from "react";
import { api, API, _parseError } from "../../api/client.js";
import { useToast, useConfirm } from "../../contexts.jsx";
import {
  Btn, Card, I, Input, MsgBanner, Sel,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const BACKUP_PREFS_KEY = "ns_backup_prefs";

export default function BackupTab() {
  const [list, setList] = useState([]);
  const [schedule, setSchedule] = useState(null);
  const [ld, setLd] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [notas, setNotas] = useState("");
  const [restoreFile, setRestoreFile] = useState(null);
  const [confirmRestore, setConfirmRestore] = useState(false);
  const [prefs, setPrefs] = useState(() => {
    try { return JSON.parse(localStorage.getItem(BACKUP_PREFS_KEY) || "{}"); }
    catch { return {}; }
  });
  const toast = useToast();
  const confirm = useConfirm();

  const savePrefs = (next) => {
    setPrefs(next);
    try { localStorage.setItem(BACKUP_PREFS_KEY, JSON.stringify(next)); } catch { /* noop */ }
  };

  const load = useCallback(async () => {
    setLd(true);
    try {
      const [backups, sched] = await Promise.all([
        api.get("/api/v1/backup/list"),
        api.get("/api/v1/backup/schedule").catch(() => null),
      ]);
      setList(backups || []);
      if (sched) setSchedule(sched);
    } catch {
      setList([]);
    }
    setLd(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (!prefs.recordar_semanal) return;
    const dow = new Date().getDay();
    if (dow !== 1) return;
    const key = `ns_backup_reminder_${new Date().toISOString().slice(0, 10)}`;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, "1");
    toast.info("Recuerde revisar sus backups de NeuroSoft esta semana.");
  }, [prefs.recordar_semanal, toast]);

  const doDownload = async () => {
    try {
      const token = localStorage.getItem("ns_token") || "";
      const r = await fetch(API + "/api/v1/backup/download", {
        headers: { Authorization: "Bearer " + token },
      });
      if (!r.ok) throw new Error("HTTP " + r.status);
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `neurosoft_backup_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, "")}.db`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      toast.success("Backup descargado");
    } catch (e) {
      toast.error("Error al descargar: " + (e.message || e));
    }
  };

  const doCreate = async () => {
    setSaving(true);
    setMsg("");
    try {
      await api.post("/api/v1/backup/", { notas: notas.trim() || null });
      toast.success("Backup cifrado creado en el servidor");
      setNotas("");
      await load();
      if (prefs.descargar_tras_crear) await doDownload();
    } catch (e) {
      toast.error(_parseError(e));
    }
    setSaving(false);
  };

  const saveSchedule = async (patch) => {
    setSaving(true);
    try {
      const next = { ...schedule, ...patch };
      const saved = await api.patch("/api/v1/backup/schedule", next);
      setSchedule(saved);
      toast.success("Programación de backup actualizada");
    } catch (e) {
      toast.error(_parseError(e));
    }
    setSaving(false);
  };

  const doDelete = async (nombre) => {
    if (!(await confirm({
      title: "Eliminar backup",
      message: `El archivo "${nombre}" se borrará permanentemente.\nEsta acción no se puede deshacer.`,
      confirmText: "Eliminar",
      dangerous: true,
    }))) return;
    try {
      await api.del("/api/v1/backup/" + encodeURIComponent(nombre));
      toast.success("Backup eliminado");
      load();
    } catch (e) {
      toast.error(_parseError(e));
    }
  };

  const handleRestoreFile = (f) => {
    if (!f) return;
    if (!f.name.endsWith(".db")) { toast.error("Solo archivos .db"); return; }
    if (f.size < 1024) { toast.error("Archivo demasiado pequeño"); return; }
    setRestoreFile(f);
    setConfirmRestore(false);
  };

  const doRestore = async () => {
    if (!restoreFile || !confirmRestore) return;
    setSaving(true);
    setMsg("");
    try {
      const fd = new FormData();
      fd.append("archivo", restoreFile);
      const token = localStorage.getItem("ns_token") || "";
      const r = await fetch(API + "/api/v1/backup/restore", {
        method: "POST",
        headers: { Authorization: "Bearer " + token },
        body: fd,
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({ detail: "HTTP " + r.status }));
        throw new Error(j.detail || "HTTP " + r.status);
      }
      const j = await r.json();
      toast.success("BD restaurada. Reinicie para aplicar cambios.");
      setMsg(`Restaurado: ${j.bytes_restaurados} bytes. Snapshot previo: ${j.safety_snapshot}`);
      setRestoreFile(null);
      setConfirmRestore(false);
      load();
    } catch (e) {
      toast.error("Error al restaurar: " + (e.message || e));
    }
    setSaving(false);
  };

  const fmtKB = (kb) => kb == null ? "—" : kb < 1024 ? `${kb.toFixed(1)} KB` : `${(kb / 1024).toFixed(1)} MB`;
  const fmtDate = (s) => {
    if (!s) return "—";
    try { return new Date(s).toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" }); }
    catch { return s; }
  };

  const fileName = (b) => b.ruta_destino?.split(/[\\/]/).pop() || b.nombre || b.archivo || "—";

  return (
    <Card className="p-8 space-y-6">
      <div>
        <h3 className="text-lg font-bold flex items-center gap-2">
          <I name="cloud_download" style={{ color: TEAL }} />Respaldo de la Base de Datos
        </h3>
        <p className="text-xs mt-1" style={{ color: "var(--ns-muted)" }}>
          Copias cifradas Fernet (AES). Retención automática configurable. Exporte .db para portabilidad.
        </p>
      </div>
      <MsgBanner msg={msg === "ok" ? "ok" : msg} onDismiss={msg && msg !== "ok" ? () => setMsg("") : null} />

      {/* Schedule QW-8 */}
      <div className="p-5 rounded-xl border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-subtle)" }}>
        <p className="text-sm font-bold flex items-center gap-2">
          <I name="schedule" style={{ color: TEAL }} />Backup automático programado
        </p>
        {schedule ? (
          <div className="grid sm:grid-cols-2 gap-4 mt-4">
            <label className="flex items-center gap-2 cursor-pointer text-xs sm:col-span-2">
              <input
                type="checkbox"
                checked={!!schedule.enabled}
                onChange={(e) => saveSchedule({ enabled: e.target.checked })}
                className="w-4 h-4"
              />
              Activar backup automático cifrado
            </label>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>Frecuencia</p>
              <Sel
                value={schedule.frequency || "daily"}
                onChange={(e) => saveSchedule({ frequency: e.target.value })}
                className="text-xs w-full"
              >
                <option value="daily">Diario</option>
                <option value="weekly">Semanal (domingo)</option>
                <option value="monthly">Mensual (día 1)</option>
              </Sel>
            </div>
            <div className="flex gap-2">
              <div className="flex-1">
                <p className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>Hora</p>
                <Input
                  type="number" min={0} max={23}
                  value={schedule.hour ?? 2}
                  onChange={(e) => saveSchedule({ hour: parseInt(e.target.value, 10) || 0 })}
                  className="text-xs"
                />
              </div>
              <div className="flex-1">
                <p className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>Minuto</p>
                <Input
                  type="number" min={0} max={59}
                  value={schedule.minute ?? 0}
                  onChange={(e) => saveSchedule({ minute: parseInt(e.target.value, 10) || 0 })}
                  className="text-xs"
                />
              </div>
            </div>
            <div className="sm:col-span-2">
              <p className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--ns-muted)" }}>
                Retener últimos {schedule.mantener_total ?? 5} archivos
              </p>
              <input
                type="range" min={3} max={30}
                value={schedule.mantener_total ?? 5}
                onChange={(e) => saveSchedule({ mantener_total: parseInt(e.target.value, 10) })}
                className="w-full"
              />
            </div>
            <div className="sm:col-span-2 text-xs" style={{ color: "var(--ns-muted)" }}>
              {schedule.last_run_at && <span>Último: {fmtDate(schedule.last_run_at)} · </span>}
              {schedule.next_run_at && <span>Próximo: {fmtDate(schedule.next_run_at)}</span>}
            </div>
          </div>
        ) : (
          <p className="text-xs mt-2" style={{ color: "var(--ns-muted)" }}>Cargando programación…</p>
        )}

        <div className="grid sm:grid-cols-2 gap-4 mt-4 pt-4 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider mb-2" style={{ color: "var(--ns-muted)" }}>Copia externa recomendada</p>
            <Input
              value={prefs.carpeta_destino || schedule?.external_path || ""}
              onChange={(e) => {
                savePrefs({ ...prefs, carpeta_destino: e.target.value });
                if (schedule) saveSchedule({ external_path: e.target.value || null });
              }}
              placeholder="Ej: D:\Backups\NeuroSoft"
              className="text-xs"
            />
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2 cursor-pointer text-xs">
              <input type="checkbox" checked={!!prefs.recordar_semanal} onChange={(e) => savePrefs({ ...prefs, recordar_semanal: e.target.checked })} className="w-4 h-4" />
              Recordarme revisar backups cada lunes
            </label>
            <label className="flex items-center gap-2 cursor-pointer text-xs">
              <input type="checkbox" checked={!!prefs.descargar_tras_crear} onChange={(e) => savePrefs({ ...prefs, descargar_tras_crear: e.target.checked })} className="w-4 h-4" />
              Descargar .db tras crear backup manual
            </label>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-5 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
          <p className="text-sm font-bold mb-2 flex items-center gap-2"><I name="download" style={{ color: TEAL }} />Descargar BD actual</p>
          <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>SQLite plano para portabilidad o migración.</p>
          <Btn onClick={doDownload}><I name="download" className="text-sm" />Descargar .db</Btn>
        </div>
        <div className="p-5 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
          <p className="text-sm font-bold mb-2 flex items-center gap-2"><I name="save" style={{ color: TEAL }} />Crear backup cifrado</p>
          <Input value={notas} onChange={(e) => setNotas(e.target.value)} placeholder="Notas (opcional)" className="mb-2 text-xs" />
          <Btn onClick={doCreate} disabled={saving}><I name="save" className="text-sm" />{saving ? "Guardando..." : "Crear backup"}</Btn>
        </div>
      </div>

      <div className="p-5 rounded-xl border-2" style={{ borderColor: "var(--ns-danger-border, #fca5a5)", background: "var(--ns-danger-bg, rgba(220,38,38,0.08))" }}>
        <p className="text-sm font-bold mb-2 flex items-center gap-2" style={{ color: "var(--ns-danger, #b91c1c)" }}>
          <I name="restore" />Restaurar desde archivo .db
        </p>
        <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>
          Irreversible. Se crea snapshot <code className="text-[10px]">pre_restore_*.db</code> antes de reemplazar.
        </p>
        <div className="flex items-center gap-3 mb-3">
          <input type="file" accept=".db" onChange={(e) => handleRestoreFile(e.target.files[0])} className="text-xs" />
          {restoreFile && (
            <span className="text-xs font-mono" style={{ color: "var(--ns-muted)" }}>
              {restoreFile.name} ({(restoreFile.size / 1024).toFixed(1)} KB)
            </span>
          )}
        </div>
        {restoreFile && (
          <label className="flex items-center gap-2 cursor-pointer mb-3">
            <input type="checkbox" checked={confirmRestore} onChange={(e) => setConfirmRestore(e.target.checked)} className="w-4 h-4" />
            <span className="text-xs font-bold" style={{ color: "var(--ns-danger, #991b1b)" }}>Entiendo que los datos actuales serán reemplazados</span>
          </label>
        )}
        <Btn onClick={doRestore} disabled={!restoreFile || !confirmRestore || saving} style={{ background: "#dc2626" }}>
          <I name="restore" className="text-sm" />{saving ? "Restaurando..." : "Restaurar BD"}
        </Btn>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-bold">Historial de backups ({list.length})</p>
          <button onClick={load} className="text-xs flex items-center gap-1 hover:underline" style={{ color: TEAL }}>
            <I name="refresh" className="text-sm" />Refrescar
          </button>
        </div>
        {ld ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full" />
          </div>
        ) : list.length === 0 ? (
          <div className="text-center py-8" style={{ color: "var(--ns-muted)" }}>
            <I name="folder_off" className="text-4xl opacity-30 mb-2" />
            <p className="text-sm font-bold">Sin backups guardados</p>
          </div>
        ) : (
          <Card className="overflow-hidden">
            <table className="w-full text-sm">
              <thead style={{ background: "var(--ns-subtle)" }}>
                <tr>
                  <th className="px-4 py-3 text-left font-bold text-xs">Archivo</th>
                  <th className="px-4 py-3 text-left font-bold text-xs">Fecha</th>
                  <th className="px-4 py-3 text-left font-bold text-xs">Tamaño</th>
                  <th className="px-4 py-3 text-left font-bold text-xs">Tipo</th>
                  <th className="px-4 py-3 text-left font-bold text-xs">Notas</th>
                  <th className="px-4 py-3 w-16" />
                </tr>
              </thead>
              <tbody>
                {list.map((b, i) => (
                  <tr key={b.id || i} className="border-b" style={{ borderColor: "var(--ns-card-b)" }}>
                    <td className="px-4 py-3 font-mono text-[11px]">{fileName(b)}</td>
                    <td className="px-4 py-3 text-xs" style={{ color: "var(--ns-muted)" }}>{fmtDate(b.fecha)}</td>
                    <td className="px-4 py-3 text-xs" style={{ color: "var(--ns-muted)" }}>{fmtKB(b.tamano_kb)}</td>
                    <td className="px-4 py-3">
                      <span className="text-[9px] font-bold px-2 py-0.5 rounded-full text-white"
                        style={{ background: b.cifrado ? TEAL : "#6b7280" }}>
                        {b.cifrado ? "cifrado" : "plano"}
                      </span>
                      {b.tipo && <span className="text-[9px] ml-1" style={{ color: "var(--ns-muted)" }}>{b.tipo}</span>}
                    </td>
                    <td className="px-4 py-3 text-xs" style={{ color: "var(--ns-muted)" }}>{b.notas || "—"}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => doDelete(fileName(b))}
                        className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500"
                        title="Eliminar"
                        aria-label="Eliminar este respaldo"
                      >
                        <I name="delete" className="text-lg" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </div>
    </Card>
  );
}
