/* ═══════════════════════════════════════════════════════════════════════
 * src/app/config/ComunicacionesTab.jsx
 * ───────────────────────────────────────────────────────────────────────
 * §QW-2 + QW-3 — Tab "Comunicaciones" en ConfigPage.
 *
 *   • Configuración SMTP (host/puerto/user/password/from/TLS/SSL)
 *   • Botón "Probar configuración" (envía email de prueba)
 *   • Editor de plantillas (asunto + cuerpo) por tipo de envío
 *
 * Variables disponibles en plantillas:
 *   {patient_nombre}, {patient_doc}, {fecha}, {profesional}, {institucion}
 *   {hora}, {tipo_cita} (sólo en plantilla 'recordatorio')
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";
import { api, _parseError } from "../../api/client.js";
import {
  Btn, Card, I, Input, Label, MsgBanner, Txta,
} from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";

const TIPOS_LABELS = {
  informe: "Informe al paciente/familia",
  remision: "Remisión a colega/médico",
  evolucion: "Evolución terapéutica",
  rips: "RIPS (EPS/aseguradora)",
  recordatorio: "Recordatorio de cita",
  otro: "Otro documento clínico",
};

export default function ComunicacionesTab() {
  const [seccion, setSeccion] = useState("smtp"); // smtp | plantillas
  const [smtp, setSmtp] = useState(null);
  const [pwd, setPwd] = useState("");      // input password (no se muestra el guardado)
  const [pwdTouched, setPwdTouched] = useState(false);
  const [msg, setMsg] = useState("");
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testTo, setTestTo] = useState("");

  /* Plantillas */
  const [tpls, setTpls] = useState([]);
  const [tplOpenId, setTplOpenId] = useState(null);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [s, t] = await Promise.all([
        api.get("/api/v1/config/smtp"),
        api.get("/api/v1/config/email-templates"),
      ]);
      setSmtp(s);
      setTpls(t || []);
    } catch (e) {
      setMsg(_parseError(e));
    }
  };

  const saveSmtp = async () => {
    setSaving(true); setMsg("");
    try {
      const body = {
        host: smtp.host || "",
        port: Number(smtp.port) || 587,
        user: smtp.user || "",
        from_addr: smtp.from_addr || "",
        from_name: smtp.from_name || "NeuroSoft",
        use_tls: !!smtp.use_tls,
        use_ssl: !!smtp.use_ssl,
        timeout_s: Number(smtp.timeout_s) || 30,
        activo: !!smtp.activo,
        // password: solo se envía si el usuario lo tocó
        ...(pwdTouched ? { password: pwd } : {}),
      };
      await api.put("/api/v1/config/smtp", body);
      setMsg("ok");
      setPwd(""); setPwdTouched(false);
      loadAll();
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  const testSmtp = async () => {
    if (!testTo.trim()) { setMsg("Indica un email para la prueba"); return; }
    setTesting(true); setMsg("");
    try {
      await api.post("/api/v1/config/smtp/test", { to: testTo.trim() });
      setMsg("test_ok");
      loadAll();
    } catch (e) {
      setMsg(_parseError(e));
    }
    setTesting(false);
  };

  const updateTpl = async (tpl) => {
    setSaving(true); setMsg("");
    try {
      await api.put(`/api/v1/config/email-templates/${tpl.tipo}`, {
        tipo: tpl.tipo,
        subject: tpl.subject,
        body: tpl.body,
        activo: tpl.activo !== false,
      });
      setMsg("ok"); loadAll();
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  const restoreTpl = async (tipo) => {
    setSaving(true); setMsg("");
    try {
      await api.del(`/api/v1/config/email-templates/${tipo}`);
      setMsg("ok"); loadAll();
    } catch (e) {
      setMsg(_parseError(e));
    }
    setSaving(false);
  };

  if (!smtp) {
    return (
      <div className="p-8 flex items-center justify-center h-40">
        <div className="animate-spin w-6 h-6 border-4 border-teal-200 border-t-teal-600 rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Mensaje OK / Error */}
      {msg && msg !== "ok" && msg !== "test_ok" && (
        <MsgBanner msg={msg} onDismiss={() => setMsg("")} />
      )}
      {msg === "ok" && (
        <div className="rounded-lg p-3 text-sm font-bold flex items-center gap-2"
          style={{ background: "rgba(16,185,129,0.10)", color: "#047857" }}>
          <I name="check_circle" />Cambios guardados
        </div>
      )}
      {msg === "test_ok" && (
        <div className="rounded-lg p-3 text-sm font-bold flex items-center gap-2"
          style={{ background: "rgba(16,185,129,0.10)", color: "#047857" }}>
          <I name="mark_email_read" />Email de prueba enviado correctamente
        </div>
      )}

      {/* Pestañas internas */}
      <div className="flex gap-2 border-b" style={{ borderColor: "var(--ns-card-b)" }}>
        {["smtp", "plantillas"].map(s => (
          <button key={s} onClick={() => setSeccion(s)}
            className="px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors"
            style={{
              color: seccion === s ? TEAL : "var(--ns-muted)",
              borderColor: seccion === s ? TEAL : "transparent",
            }}>
            {s === "smtp" ? "Servidor SMTP" : "Plantillas de correo"}
          </button>
        ))}
      </div>

      {seccion === "smtp" && (
        <Card className="p-6 space-y-5">
          <div className="flex items-center gap-3">
            <I name="mail" style={{ color: TEAL, fontSize: 24 }} />
            <div>
              <h3 className="font-bold">Servidor SMTP</h3>
              <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                Configura el correo saliente para enviar informes, recordatorios y remisiones.
                Origen actual: <span className="font-bold ns-mono">{smtp.source}</span>
                {smtp.ultima_prueba && (
                  <> · última prueba {smtp.ultima_prueba_ok ? "✅" : "❌"} {new Date(smtp.ultima_prueba).toLocaleString("es-CO")}</>
                )}
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <Label>Servidor (host)</Label>
              <Input value={smtp.host || ""} onChange={e => setSmtp({...smtp, host: e.target.value})}
                placeholder="smtp.gmail.com / smtp.office365.com" />
            </div>
            <div>
              <Label>Puerto</Label>
              <Input type="number" value={smtp.port || 587}
                onChange={e => setSmtp({...smtp, port: Number(e.target.value)})} />
              <p className="text-[10px] mt-1" style={{ color: "var(--ns-muted)" }}>
                587 para STARTTLS · 465 para SSL directo
              </p>
            </div>
            <div>
              <Label>Usuario</Label>
              <Input value={smtp.user || ""} onChange={e => setSmtp({...smtp, user: e.target.value})}
                placeholder="correo@gmail.com" />
            </div>
            <div>
              <Label>Contraseña / App Password</Label>
              <Input type="password"
                value={pwd}
                onChange={e => { setPwd(e.target.value); setPwdTouched(true); }}
                placeholder={smtp.password_set ? "•••••••••••• (sin cambios si dejas vacío)" : "Ingresa contraseña"} />
              <p className="text-[10px] mt-1" style={{ color: "var(--ns-muted)" }}>
                Para Gmail usa App Password (no la contraseña normal).
                <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noreferrer" style={{ color: TEAL, marginLeft: 4 }}>
                  Generar →
                </a>
              </p>
            </div>
            <div>
              <Label>Email "De" (From)</Label>
              <Input value={smtp.from_addr || ""} onChange={e => setSmtp({...smtp, from_addr: e.target.value})}
                placeholder="Si vacío usa el usuario" />
            </div>
            <div>
              <Label>Nombre "De"</Label>
              <Input value={smtp.from_name || ""} onChange={e => setSmtp({...smtp, from_name: e.target.value})}
                placeholder="NeuroSoft" />
            </div>
            <div>
              <Label>Cifrado</Label>
              <div className="flex gap-3 mt-2">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={!!smtp.use_tls}
                    onChange={e => setSmtp({...smtp, use_tls: e.target.checked, use_ssl: e.target.checked ? false : smtp.use_ssl})} />
                  STARTTLS (587)
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={!!smtp.use_ssl}
                    onChange={e => setSmtp({...smtp, use_ssl: e.target.checked, use_tls: e.target.checked ? false : smtp.use_tls})} />
                  SSL directo (465)
                </label>
              </div>
            </div>
            <div>
              <Label>Activo</Label>
              <label className="flex items-center gap-2 text-sm cursor-pointer mt-2">
                <input type="checkbox" checked={!!smtp.activo}
                  onChange={e => setSmtp({...smtp, activo: e.target.checked})} />
                Habilitar envío de correos
              </label>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 pt-3 border-t" style={{ borderColor: "var(--ns-card-b)" }}>
            <Btn onClick={saveSmtp} disabled={saving} style={{ background: TEAL, color: "#fff", borderColor: TEAL }}>
              {saving ? "Guardando…" : <><I name="save" className="mr-1.5" />Guardar configuración</>}
            </Btn>
          </div>

          {/* Prueba */}
          <div className="rounded-lg p-4" style={{ background: "var(--ns-subtle)" }}>
            <h4 className="font-bold text-sm mb-2 flex items-center gap-1.5">
              <I name="science" style={{ color: TEAL }} />Probar configuración
            </h4>
            <p className="text-xs mb-3" style={{ color: "var(--ns-muted)" }}>
              Envía un correo de prueba a la dirección que indiques para verificar
              que el servidor responde correctamente.
            </p>
            <div className="flex gap-2 flex-wrap">
              <Input type="email" value={testTo}
                onChange={e => setTestTo(e.target.value)}
                placeholder="tu@email.com"
                style={{ flex: 1, minWidth: 200 }} />
              <Btn onClick={testSmtp} disabled={testing || !testTo.trim()}>
                {testing ? "Enviando…" : <><I name="send" className="mr-1.5" />Enviar prueba</>}
              </Btn>
            </div>
          </div>
        </Card>
      )}

      {seccion === "plantillas" && (
        <Card className="p-6 space-y-4">
          <div className="flex items-center gap-3">
            <I name="article" style={{ color: TEAL, fontSize: 24 }} />
            <div>
              <h3 className="font-bold">Plantillas de correo</h3>
              <p className="text-xs" style={{ color: "var(--ns-muted)" }}>
                Edita el asunto y cuerpo predeterminado para cada tipo de envío.
                Variables: <code className="ns-mono">{"{patient_nombre}, {patient_doc}, {fecha}, {profesional}, {institucion}, {hora}, {tipo_cita}"}</code>
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {tpls.map(t => (
              <details key={t.tipo} open={tplOpenId === t.tipo}
                onToggle={(e) => e.target.open ? setTplOpenId(t.tipo) : null}
                className="rounded border" style={{ borderColor: "var(--ns-card-b)", background: "var(--ns-card)" }}>
                <summary className="p-3 cursor-pointer font-bold flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <I name="email" style={{ color: TEAL }} />
                    {TIPOS_LABELS[t.tipo] || t.tipo}
                  </span>
                  <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded"
                    style={{
                      background: t.source === "db" ? "rgba(13,148,136,0.1)" : "var(--ns-subtle)",
                      color: t.source === "db" ? TEAL : "var(--ns-muted)",
                    }}>
                    {t.source === "db" ? "Personalizada" : "Por defecto"}
                  </span>
                </summary>
                <div className="p-4 border-t space-y-3" style={{ borderColor: "var(--ns-card-b)" }}>
                  <div>
                    <Label>Asunto</Label>
                    <Input value={t.subject || ""}
                      onChange={(e) => setTpls(arr => arr.map(x => x.tipo === t.tipo ? {...x, subject: e.target.value} : x))} />
                  </div>
                  <div>
                    <Label>Cuerpo</Label>
                    <Txta rows={8} value={t.body || ""}
                      onChange={(e) => setTpls(arr => arr.map(x => x.tipo === t.tipo ? {...x, body: e.target.value} : x))} />
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <Btn onClick={() => updateTpl(t)} disabled={saving}
                      style={{ background: TEAL, color: "#fff", borderColor: TEAL }}>
                      <I name="save" className="mr-1.5" />Guardar
                    </Btn>
                    {t.source === "db" && (
                      <Btn variant="ghost" onClick={() => restoreTpl(t.tipo)} disabled={saving}>
                        <I name="restart_alt" className="mr-1.5" />Restaurar por defecto
                      </Btn>
                    )}
                  </div>
                </div>
              </details>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
