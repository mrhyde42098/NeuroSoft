/* ═══════════════════════════════════════════════════════════════════════
 * PanelIA.jsx — Asistente de IA integrado NeuroSoft
 * ───────────────────────────────────────────────────────────────────────
 * Provee:
 *   · AIConfigPage    — página completa de configuración multi-proveedor
 *   · AIFloatingChat  — botón flotante + panel lateral de chat contextual
 *   · improveWithAI   — helper para corregir texto desde cualquier textarea
 *   · narrateWithAI   — helper para generar narrativa desde Z-scores
 *   · ImproveButton   — botón inline "Mejorar con IA"
 *
 * Backend: /api/v1/ai (app/presentation/api/v1/ai.py)
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useRef, useState, useCallback } from "react";
import { Card, I, Btn, TopBar } from "../../ui/primitives.jsx";
import { TEAL, NAVY } from "../../ui/tokens.js";
import { useConfirm } from "../../contexts.jsx";

/* ─── API helper ────────────────────────────────────────────────────── */
const API = import.meta.env.PROD ? "" : "http://localhost:8000";
const _tok  = () => localStorage.getItem("ns_token") || "";
const _hdrs = (json = false) => {
  const h = { Authorization: `Bearer ${_tok()}` };
  if (json) h["Content-Type"] = "application/json";
  return h;
};
async function aiGet(path) {
  const r = await fetch(`${API}${path}`, { headers: _hdrs() });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `HTTP ${r.status}`);
  return r.json();
}
async function aiPost(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST", headers: _hdrs(true), body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `HTTP ${r.status}`);
  return r.json();
}

/* ─── Helpers exportados ─────────────────────────────────────────────── */
export async function improveWithAI(text, task = "style") {
  const r = await aiPost("/api/v1/ai/improve", { text, task });
  return { improved: r.content || r.improved || "", provider: r.provider, raw: r };
}
export async function narrateWithAI(dominio, resultados, estilo = "parrafo") {
  const r = await aiPost("/api/v1/ai/narrate", { dominio, resultados, estilo });
  return { text: r.content || r.narrativa || "", provider: r.provider };
}

/* §ai-specialized (2026-05-18): invoca un prompt especializado de la
 * biblioteca clínica del backend. Los prompts viven en
 * app/domain/clinical_engine/ai_prompts.py y son curados clínicamente.
 *
 * Ejemplos:
 *   await specializedAI("mejorar_observacion_clinica", { texto: "..." })
 *   await specializedAI("sugerir_dx_dsm5", { edad, escolaridad, puntajes,
 *       observaciones, motivo })
 *   await specializedAI("narrativa_integradora", { edad, escolaridad,
 *       dominios, observaciones })
 *
 * Devuelve { content, provider, model, usage }. */
export async function specializedAI(promptId, variables) {
  const r = await aiPost("/api/v1/ai/specialized", {
    prompt_id: promptId,
    variables,
  });
  return {
    content: r.content || "",
    provider: r.provider,
    model: r.model,
    usage: r.usage,
  };
}

/* Catálogo de prompts disponibles (cargado dinámicamente desde el backend). */
export async function listSpecializedPrompts() {
  const token = localStorage.getItem("ns_token") || "";
  const r = await fetch(`${API}/api/v1/ai/prompts`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

/* ═══════════════════════════════════════════════════════════════════════
 * DATOS DE PROVEEDORES
 * ═══════════════════════════════════════════════════════════════════════ */
const PROVIDERS = [
  {
    id: "gemini",
    label: "Google Gemini",
    short: "Gemini",
    logoLetter: "G",
    color: "#4285F4",
    gradient: "linear-gradient(135deg,#4285F4,#34A853)",
    description: "Modelos de Google AI con contexto largo y cuota gratuita generosa.",
    badge: "Gratis",
    badgeColor: "#059669",
    keyPrefix: "AIza",
    keyHint: "Debe empezar con 'AIza'",
    keyUrl: "https://aistudio.google.com/apikey",
    keyUrlLabel: "Obtener clave en Google AI Studio →",
    keySteps: [
      "Entra a aistudio.google.com con tu cuenta de Google.",
      "Haz clic en «Get API Key» → «Create API key in new project».",
      "Copia la clave generada (empieza con AIza…).",
      "Pégala aquí y guarda.",
    ],
    models: [
      { id: "gemini-2.0-flash-exp", label: "Gemini 2.0 Flash Exp (recomendado)", recommended: true },
      { id: "gemini-1.5-flash",     label: "Gemini 1.5 Flash (rápido)" },
      { id: "gemini-1.5-pro",       label: "Gemini 1.5 Pro (máxima calidad)" },
    ],
  },
  {
    id: "claude",
    label: "Anthropic Claude",
    short: "Claude",
    logoLetter: "A",
    color: "#7C3AED",
    gradient: "linear-gradient(135deg,#7C3AED,#A78BFA)",
    description: "Claude de Anthropic — excelente para redacción clínica estructurada y narrativas.",
    badge: "De pago",
    badgeColor: "#6366f1",
    keyPrefix: "sk-ant-",
    keyHint: "Debe empezar con 'sk-ant-'",
    keyUrl: "https://console.anthropic.com/settings/keys",
    keyUrlLabel: "Obtener clave en Anthropic Console →",
    keySteps: [
      "Entra a console.anthropic.com (requiere cuenta y créditos).",
      "Ve a Settings → API Keys → «Create Key».",
      "Asigna un nombre (ej. 'NeuroSoft') y copia la clave.",
      "Pégala aquí y guarda.",
    ],
    models: [
      { id: "claude-3-5-haiku-20241022",  label: "Claude 3.5 Haiku (rápido, económico)", recommended: true },
      { id: "claude-3-5-sonnet-20241022", label: "Claude 3.5 Sonnet (más capaz)" },
      { id: "claude-3-opus-20240229",     label: "Claude 3 Opus (máxima calidad)" },
    ],
  },
  {
    id: "openai",
    label: "OpenAI GPT",
    short: "OpenAI",
    logoLetter: "⊕",
    color: "#059669",
    gradient: "linear-gradient(135deg,#059669,#34D399)",
    description: "GPT-4o y GPT-4o mini de OpenAI — ampliamente usados en entornos clínicos.",
    badge: "De pago",
    badgeColor: "#6366f1",
    keyPrefix: "sk-",
    keyHint: "Debe empezar con 'sk-'",
    keyUrl: "https://platform.openai.com/api-keys",
    keyUrlLabel: "Obtener clave en OpenAI Platform →",
    keySteps: [
      "Entra a platform.openai.com (requiere cuenta y créditos).",
      "Ve a API Keys → «Create new secret key».",
      "Copia la clave (solo se muestra una vez).",
      "Pégala aquí y guarda.",
    ],
    models: [
      { id: "gpt-4o-mini", label: "GPT-4o mini (rápido, económico)", recommended: true },
      { id: "gpt-4o",      label: "GPT-4o (más capaz)" },
      { id: "gpt-4-turbo", label: "GPT-4 Turbo" },
    ],
  },
  {
    id: "ollama",
    label: "Ollama (Local)",
    short: "Ollama",
    logoLetter: "⊡",
    color: "#2563EB",
    gradient: "linear-gradient(135deg,#2563EB,#60A5FA)",
    description: "Modelos de IA en tu propio equipo — sin internet, máxima privacidad de datos.",
    badge: "Gratis",
    badgeColor: "#059669",
    keyPrefix: null,
    keyHint: null,
    keyUrl: "https://ollama.com/download",
    keyUrlLabel: "Descargar Ollama para Windows →",
    keySteps: [
      "Descarga e instala Ollama desde ollama.com/download.",
      "Abre una terminal y ejecuta: ollama pull llama3.1:8b",
      "Ollama se ejecuta automáticamente en http://127.0.0.1:11434.",
      "O usa el botón «Setup automático» de abajo.",
    ],
    models: [], // se llenan con modelos locales detectados
  },
  {
    id: "auto",
    label: "Automático",
    short: "Auto",
    logoLetter: "✦",
    color: TEAL,
    gradient: `linear-gradient(135deg,${NAVY},${TEAL})`,
    description: "Selecciona automáticamente el mejor proveedor disponible con la configuración actual.",
    badge: null,
    keyPrefix: null,
    keyHint: null,
    keyUrl: null,
    models: [],
  },
];

/* ─── Validación de formato de API Key ───────────────────────────────── */
function validateKey(provider, key) {
  if (!provider?.keyPrefix || !key) return null; // sin restricción
  if (key.startsWith(provider.keyPrefix)) return "ok";
  return "error";
}

/* ─── Logo visual del proveedor ──────────────────────────────────────── */
function ProviderLogo({ prov, size = 44 }) {
  return (
    <div
      className="flex items-center justify-center shrink-0 rounded-2xl font-extrabold select-none"
      style={{
        width: size, height: size, fontSize: size * 0.4,
        background: prov.gradient, color: "white",
        boxShadow: `0 4px 14px -2px ${prov.color}50`,
      }}
    >
      {prov.logoLetter}
    </div>
  );
}

/* ─── Tarjeta de proveedor ───────────────────────────────────────────── */
function ProviderCard({ prov, selected, onSelect, connected }) {
  return (
    <button
      onClick={onSelect}
      className="w-full text-left p-4 rounded-2xl border-2 transition-all"
      style={{
        borderColor: selected ? prov.color : "var(--ns-card-b)",
        background: selected ? `${prov.color}10` : "var(--ns-card)",
        boxShadow: selected ? `0 0 0 3px ${prov.color}25` : "none",
      }}
    >
      <div className="flex items-start gap-3">
        <ProviderLogo prov={prov} size={40} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>{prov.label}</span>
            {prov.badge && (
              <span className="text-[9px] font-extrabold px-2 py-0.5 rounded-full text-white"
                style={{ background: prov.badgeColor }}>
                {prov.badge}
              </span>
            )}
            {connected && (
              <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-500 text-white flex items-center gap-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-white inline-block"/> Conectado
              </span>
            )}
          </div>
          <p className="text-[11px] mt-0.5 leading-snug" style={{ color: "var(--ns-muted)" }}>
            {prov.description}
          </p>
        </div>
      </div>
    </button>
  );
}

/* ─── Input de API Key con toggle y validación ───────────────────────── */
function ApiKeyInput({ prov, value, onChange }) {
  const [show, setShow] = useState(false);
  const [showSteps, setShowSteps] = useState(false);
  const validity = validateKey(prov, value);

  return (
    <div className="space-y-3">
      {/* Input row */}
      <div className="relative">
        <input
          type={show ? "text" : "password"}
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={prov.keyHint || "Clave API…"}
          autoComplete="off"
          spellCheck={false}
          className="w-full px-4 py-3 pr-24 rounded-xl text-sm font-mono transition-all"
          style={{
            background: "var(--ns-input)",
            color: "var(--ns-text)",
            border: `1.5px solid ${
              validity === "ok" ? "#10b981"
              : validity === "error" ? "#f43f5e"
              : "var(--ns-card-b)"
            }`,
            outline: "none",
          }}
        />
        {/* Toggle + Status */}
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {validity === "ok"    && <I name="check_circle" fill className="text-base text-emerald-500" />}
          {validity === "error" && <I name="error"        fill className="text-base text-rose-500" />}
          <button
            type="button"
            onClick={() => setShow(s => !s)}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-all"
            style={{ color: "var(--ns-muted)" }}
            title={show ? "Ocultar" : "Mostrar"}
          >
            <I name={show ? "visibility_off" : "visibility"} className="text-base" />
          </button>
        </div>
      </div>

      {/* Validation hint */}
      {validity === "error" && (
        <p className="text-[11px] text-rose-500 flex items-center gap-1">
          <I name="warning" className="text-xs" />
          {prov.keyHint} — verifica que copiaste la clave completa.
        </p>
      )}
      {validity === "ok" && (
        <p className="text-[11px] text-emerald-600 flex items-center gap-1">
          <I name="check_circle" className="text-xs" />
          Formato de clave correcto. Guarda y prueba la conexión.
        </p>
      )}

      {/* Link directo + tutorial */}
      {prov.keyUrl && (
        <div className="flex items-center justify-between flex-wrap gap-2">
          <a
            href={prov.keyUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-bold flex items-center gap-1 hover:underline"
            style={{ color: prov.color }}
          >
            <I name="open_in_new" className="text-xs" />
            {prov.keyUrlLabel}
          </a>
          <button
            type="button"
            onClick={() => setShowSteps(s => !s)}
            className="text-xs flex items-center gap-1 hover:underline"
            style={{ color: "var(--ns-muted)" }}
          >
            <I name={showSteps ? "expand_less" : "help_outline"} className="text-xs" />
            {showSteps ? "Ocultar pasos" : "¿Cómo obtengo la clave?"}
          </button>
        </div>
      )}

      {/* Paso a paso colapsable */}
      {showSteps && prov.keySteps && (
        <div className="rounded-xl p-4 space-y-2"
          style={{ background: `${prov.color}08`, border: `1px solid ${prov.color}25` }}>
          <p className="text-[10px] font-extrabold uppercase tracking-wider" style={{ color: prov.color }}>
            Pasos para obtener tu clave API
          </p>
          <ol className="space-y-1.5">
            {prov.keySteps.map((step, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[11px]" style={{ color: "var(--ns-text)" }}>
                <span className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-extrabold text-white shrink-0 mt-0.5"
                  style={{ background: prov.color }}>{i + 1}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

/* ─── Selector de modelo ─────────────────────────────────────────────── */
function ModelSelector({ prov, value, onChange, dynamicModels = [] }) {
  const models = prov.id === "ollama"
    ? dynamicModels.map(m => ({ id: m.name || m, label: m.name || m }))
    : prov.models;

  if (models.length === 0 && prov.id !== "ollama") return null;

  return (
    <div className="space-y-2">
      <label className="text-xs font-extrabold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
        Modelo
      </label>
      {models.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {models.map(m => (
            <button
              key={m.id}
              type="button"
              onClick={() => onChange(m.id)}
              className="flex items-center gap-2 p-2.5 rounded-xl border text-left transition-all"
              style={{
                borderColor: value === m.id ? prov.color : "var(--ns-card-b)",
                background: value === m.id ? `${prov.color}12` : "var(--ns-subtle)",
              }}
            >
              <I
                name={value === m.id ? "radio_button_checked" : "radio_button_unchecked"}
                className="text-base shrink-0"
                style={{ color: value === m.id ? prov.color : "var(--ns-muted)" }}
              />
              <div className="min-w-0">
                <p className="text-xs font-bold truncate" style={{ color: "var(--ns-text)" }}>{m.label}</p>
                {m.recommended && (
                  <span className="text-[9px] font-bold text-emerald-600">★ Recomendado</span>
                )}
              </div>
            </button>
          ))}
        </div>
      ) : (
        <p className="text-xs p-3 rounded-xl" style={{ color: "var(--ns-muted)", background: "var(--ns-subtle)" }}>
          {prov.id === "ollama"
            ? "Inicia Ollama y haz clic en «Re-detectar» para ver los modelos instalados."
            : "Sin modelos — escribe el identificador manualmente en el campo de abajo."}
        </p>
      )}
      {/* Campo manual como fallback */}
      <div>
        <input
          value={value || ""}
          onChange={e => onChange(e.target.value)}
          placeholder="O escribe el identificador exacto del modelo…"
          className="w-full px-3 py-2 rounded-lg text-xs"
          style={{
            background: "var(--ns-input)", color: "var(--ns-text)",
            border: "1.5px solid var(--ns-card-b)", outline: "none",
          }}
        />
      </div>
    </div>
  );
}

/* ─── Status chip ────────────────────────────────────────────────────── */
function StatusChip({ ok, label }) {
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-full ${
      ok === true  ? "bg-emerald-100 text-emerald-700"
    : ok === false ? "bg-rose-100 text-rose-700"
    :                "bg-gray-100 text-gray-500"
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        ok === true ? "bg-emerald-500" : ok === false ? "bg-rose-500" : "bg-gray-400"
      }`}/>
      {label}
    </span>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
 * AIConfigPage — Página principal de configuración
 * ═══════════════════════════════════════════════════════════════════════ */
export function AIConfigPage() {
  const confirm = useConfirm();
  const [cfg,        setCfg]        = useState(null);
  const [msg,        setMsg]        = useState({ text: "", type: "" });
  const [busy,       setBusy]       = useState(false);
  const [health,     setHealth]     = useState(null);
  const [ollama,     setOllama]     = useState(null);
  const [bundled,    setBundled]    = useState(null);
  const [installing, _setInstalling] = useState(false);
  const [pullBusy,   setPullBusy]   = useState(false);
  const [pullProgress, setPullProgress] = useState(null);

  const selProv = PROVIDERS.find(p => p.id === cfg?.provider) || PROVIDERS[0];

  const load = useCallback(async () => {
    try {
      const c = await aiGet("/api/v1/ai/config");
      setCfg(c);
    } catch (e) { setMsg({ text: "Error cargando config: " + e.message, type: "error" }); }
  }, []);

  const checkOllama = useCallback(async () => {
    try { setOllama(await aiGet("/api/v1/ai/ollama/status")); }
    catch { setOllama({ installed: false, running: false }); }
    try { setBundled(await aiGet("/api/v1/ai/ollama/bundled")); }
    catch { setBundled({ available: false }); }
  }, []);

  useEffect(() => { load(); checkOllama(); }, [load, checkOllama]);

  const save = async () => {
    setBusy(true); setMsg({ text: "", type: "" });
    try {
      await aiPost("/api/v1/ai/config", cfg);
      setMsg({ text: "Configuración guardada correctamente.", type: "ok" });
      await load();
    } catch (e) { setMsg({ text: "Error al guardar: " + e.message, type: "error" }); }
    setBusy(false);
  };

  const testConnection = async () => {
    setBusy(true); setMsg({ text: "", type: "" });
    try {
      const h = await aiGet("/api/v1/ai/health");
      setHealth(h);
      const ok = h.providers?.some?.(p => p.ok) || h.status === "ok" || h.ok;
      setMsg({ text: ok ? "Conexión exitosa ✓" : "Sin proveedores activos. Revisa la configuración.", type: ok ? "ok" : "warn" });
    } catch (e) { setMsg({ text: "Error al probar: " + e.message, type: "error" }); }
    setBusy(false);
  };

  const pullModel = useCallback(async (modelName) => {
    const name = modelName || "llama3.1:8b";
    if (!(await confirm({
      title: `Descargar modelo ${name}`,
      message: "El modelo pesa entre 4 y 6 GB y puede tardar varios minutos.\nDurante la descarga, NeuroSoft seguirá funcionando pero el chat con IA estará deshabilitado.",
      confirmText: "Descargar",
    }))) return;
    setPullBusy(true); setPullProgress({ status: "iniciando", pct: 0 });
    try {
      const token = localStorage.getItem("ns_token") || "";
      const r = await fetch(`${API}/api/v1/ai/ollama/pull_stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
        body: JSON.stringify({ name }),
      });
      if (!r.ok) { setMsg({ text: "Error HTTP " + r.status, type: "error" }); setPullBusy(false); return; }
      const reader = r.body.getReader(); const dec = new TextDecoder(); let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n"); buf = lines.pop();
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const j = JSON.parse(line);
            const pct = j.total ? Math.round((j.completed || 0) / j.total * 100) : 0;
            setPullProgress({ status: j.status || "descargando", pct });
          } catch {}
        }
      }
      setMsg({ text: `Modelo "${name}" descargado exitosamente.`, type: "ok" });
      setPullProgress(null);
      await checkOllama();
    } catch (e) { setMsg({ text: "Error: " + e.message, type: "error" }); }
    setPullBusy(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [checkOllama]);

  const autoSetup = async () => {
    if (!(await confirm({
      title: "Setup automático del asistente IA",
      message: "Se instalará Ollama si aún no está, y se descargará el modelo por defecto.\nProceso completo: ~5-10 minutos.",
      confirmText: "Iniciar setup",
    }))) return;
    setMsg({ text: "Setup automático iniciado…", type: "info" });
    try {
      const r = await aiPost("/api/v1/ai/ollama/autosetup", {});
      if (r.running) {
        setMsg({ text: "Ollama activo. Iniciando descarga del modelo…", type: "info" });
        await pullModel(r.suggested_model);
      } else {
        setMsg({ text: "Instalador lanzado. Cuando termine haz clic en «Re-detectar».", type: "info" });
      }
      await checkOllama();
    } catch (e) { setMsg({ text: "Error: " + e.message, type: "error" }); }
  };

  if (!cfg) return (
    <>
      <TopBar title="Asistente IA" />
      <main className="p-8 flex items-center justify-center h-96">
        <div className="animate-spin w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full" />
      </main>
    </>
  );

  const msgColors = {
    ok:    { bg: "rgba(16,185,129,0.1)", color: "#065f46", icon: "check_circle" },
    error: { bg: "rgba(239,68,68,0.1)",  color: "#991b1b", icon: "error" },
    warn:  { bg: "rgba(245,158,11,0.1)", color: "#92400e", icon: "warning" },
    info:  { bg: "rgba(99,102,241,0.1)", color: "#3730a3", icon: "info" },
  };

  return (
    <>
      <TopBar title="Asistente IA">
        <span className="text-xs" style={{ color: "var(--ns-muted)" }}>Configuración de proveedor</span>
      </TopBar>

      <main className="p-6 lg:p-8 max-w-4xl">
        {/* Hero explicativo */}
        <Card className="p-5 mb-6 flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0"
            style={{ background: `${TEAL}15` }}>
            <I name="smart_toy" fill className="text-2xl" style={{ color: TEAL }} />
          </div>
          <div>
            <h2 className="font-bold text-base" style={{ color: "var(--ns-text)" }}>
              ¿Cómo funciona el Asistente IA?
            </h2>
            <p className="text-xs mt-1 leading-relaxed" style={{ color: "var(--ns-muted)" }}>
              NeuroSoft usa modelos de IA para ayudarte a redactar informes, mejorar narrativas
              clínicas y responder dudas sobre puntajes. Puedes usar un proveedor en la nube
              (requiere clave API gratuita o de pago) o instalar Ollama para funcionar
              completamente sin internet. Los datos de identificación del paciente se sanitizan
              automáticamente antes de enviarse a cualquier proveedor externo.
            </p>
          </div>
        </Card>

        {/* §ollama-auto: banner destacado si Ollama está corriendo (auto-instalado) */}
        {ollama?.running && (
          <Card className="p-4 mb-5 flex items-start gap-3" style={{ background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.3)" }}>
            <div className="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0"
              style={{ background: "linear-gradient(135deg,#10b981,#059669)" }}>
              <I name="check_circle" fill className="text-xl text-white" />
            </div>
            <div className="flex-1">
              <p className="font-bold text-sm" style={{ color: "#065f46" }}>
                ✨ IA local lista — sin API keys, sin internet
              </p>
              <p className="text-xs mt-1 leading-relaxed" style={{ color: "#047857" }}>
                Ollama está instalado y corriendo en tu equipo. {ollama?.models?.length > 0
                  ? <>Tienes <strong>{ollama.models.length}</strong> modelo{ollama.models.length !== 1 ? "s" : ""} disponible{ollama.models.length !== 1 ? "s" : ""}.</>
                  : <>Aún no tienes ningún modelo descargado — usa el botón <strong>«Descargar llama3.1:8b»</strong> abajo para empezar (~4 GB, una sola vez).</>
                } Los datos NUNCA salen de tu computadora.
              </p>
            </div>
          </Card>
        )}
        {/* §ollama-auto: banner durante la instalación silenciosa al primer arranque */}
        {!ollama?.running && bundled?.available && (
          <Card className="p-4 mb-5 flex items-start gap-3" style={{ background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.3)" }}>
            <div className="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0"
              style={{ background: "linear-gradient(135deg,#6366f1,#8b5cf6)" }}>
              <I name="auto_awesome" fill className="text-xl text-white" />
            </div>
            <div className="flex-1">
              <p className="font-bold text-sm" style={{ color: "#3730a3" }}>
                🤖 Asistente IA local incluido — sin API keys
              </p>
              <p className="text-xs mt-1 leading-relaxed" style={{ color: "#4338ca" }}>
                Esta versión trae <strong>Ollama incluido</strong> ({bundled.size_mb} MB). Al arrancar la app por primera vez se instala
                automáticamente en segundo plano. Si no apareció solo, haz clic en <strong>«Setup automático»</strong> abajo.
              </p>
            </div>
            <button onClick={autoSetup} disabled={installing || pullBusy}
              className="text-xs px-3 py-2 rounded-xl font-bold text-white flex items-center gap-1 disabled:opacity-50 shrink-0 self-center"
              style={{ background: "linear-gradient(135deg,#6366f1,#8b5cf6)" }}>
              <I name="bolt" className="text-sm" />Setup automático
            </button>
          </Card>
        )}

        {/* Mensaje de estado */}
        {msg.text && (() => {
          const mc = msgColors[msg.type] || msgColors.info;
          return (
            <div className="mb-5 p-3 rounded-xl flex items-center gap-2 text-sm font-medium"
              style={{ background: mc.bg, color: mc.color }}>
              <I name={mc.icon} fill className="text-base shrink-0" />
              {msg.text}
            </div>
          );
        })()}

        {/* 1. Selección de proveedor */}
        <section className="mb-5">
          <h3 className="text-xs font-extrabold uppercase tracking-wider mb-3 flex items-center gap-2"
            style={{ color: "var(--ns-muted)" }}>
            <span className="w-5 h-5 rounded-full bg-teal-600 text-white text-[9px] font-extrabold flex items-center justify-center">1</span>
            Elige un proveedor de IA
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {PROVIDERS.map(p => (
              <ProviderCard
                key={p.id}
                prov={p}
                selected={cfg.provider === p.id}
                onSelect={() => setCfg({ ...cfg, provider: p.id })}
                connected={health?.providers?.find?.(hp => hp.id === p.id)?.ok}
              />
            ))}
          </div>
        </section>

        {/* 2. Configuración específica del proveedor */}
        {cfg.provider !== "auto" && (
          <section className="mb-5">
            <h3 className="text-xs font-extrabold uppercase tracking-wider mb-3 flex items-center gap-2"
              style={{ color: "var(--ns-muted)" }}>
              <span className="w-5 h-5 rounded-full bg-teal-600 text-white text-[9px] font-extrabold flex items-center justify-center">2</span>
              Configura {selProv.label}
            </h3>

            <Card className="p-5 space-y-5">
              <div className="flex items-center gap-3 pb-4 border-b" style={{ borderColor: "var(--ns-card-b)" }}>
                <ProviderLogo prov={selProv} size={36} />
                <div>
                  <p className="font-bold text-sm" style={{ color: "var(--ns-text)" }}>{selProv.label}</p>
                  <p className="text-[11px]" style={{ color: "var(--ns-muted)" }}>{selProv.description}</p>
                </div>
              </div>

              {/* API Key (solo para cloud providers) */}
              {selProv.keyPrefix !== null && (
                <div className="space-y-2">
                  <label className="text-xs font-extrabold uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                    Clave API
                    <span className="ml-2 text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: "rgba(16,185,129,0.1)", color: "#065f46" }}>
                      Se cifra y almacena localmente
                    </span>
                  </label>
                  <ApiKeyInput
                    prov={selProv}
                    value={cfg.api_key || ""}
                    onChange={val => setCfg({ ...cfg, api_key: val })}
                  />
                </div>
              )}

              {/* URL Ollama */}
              {cfg.provider === "ollama" && (
                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-extrabold uppercase tracking-wider block mb-1.5"
                      style={{ color: "var(--ns-muted)" }}>URL de Ollama</label>
                    <input
                      value={cfg.ollama_url || ""}
                      onChange={e => setCfg({ ...cfg, ollama_url: e.target.value })}
                      placeholder="http://127.0.0.1:11434"
                      className="w-full px-3 py-2.5 rounded-xl text-sm"
                      style={{ background: "var(--ns-input)", color: "var(--ns-text)", border: "1.5px solid var(--ns-card-b)", outline: "none" }}
                    />
                  </div>

                  {/* Estado de Ollama */}
                  <div className="flex items-center gap-3 flex-wrap p-4 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
                    <StatusChip
                      ok={ollama?.installed ? true : false}
                      label={ollama?.installed ? "Instalado" : "No instalado"}
                    />
                    <StatusChip
                      ok={ollama?.running ? true : false}
                      label={ollama?.running ? "Servicio activo" : "Servicio inactivo"}
                    />
                    {ollama?.models?.length > 0 && (
                      <span className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                        Modelos: <strong>{ollama.models.map(m => m.name || m).join(", ")}</strong>
                      </span>
                    )}
                    <button onClick={checkOllama}
                      className="ml-auto text-xs px-3 py-1.5 rounded-lg font-bold hover:bg-gray-100 flex items-center gap-1"
                      style={{ color: "var(--ns-muted)" }}>
                      <I name="refresh" className="text-sm" />Re-detectar
                    </button>
                  </div>

                  {/* Acciones Ollama */}
                  <div className="flex flex-wrap gap-2">
                    {!ollama?.installed && (
                      <a href="https://ollama.com/download" target="_blank" rel="noopener noreferrer"
                        className="text-xs px-3 py-2 rounded-xl font-bold text-white flex items-center gap-1"
                        style={{ background: selProv.color }}>
                        <I name="download" className="text-sm" />Descargar Ollama
                      </a>
                    )}
                    {bundled?.available && !ollama?.running && (
                      <button onClick={autoSetup} disabled={installing || pullBusy}
                        className="text-xs px-3 py-2 rounded-xl font-bold text-white flex items-center gap-1 disabled:opacity-50"
                        style={{ background: "#f59e0b" }}>
                        <I name="bolt" className="text-sm" />Setup automático
                      </button>
                    )}
                    {ollama?.running && (
                      <>
                        <button onClick={() => pullModel("llama3.1:8b")} disabled={pullBusy}
                          className="text-xs px-3 py-2 rounded-xl font-bold text-white flex items-center gap-1 disabled:opacity-50"
                          style={{ background: selProv.color }}>
                          <I name="cloud_download" className="text-sm" />
                          {pullBusy ? "Descargando…" : "Descargar llama3.1:8b"}
                        </button>
                        <button onClick={() => pullModel("qwen2.5:7b")} disabled={pullBusy}
                          className="text-xs px-3 py-2 rounded-xl font-bold flex items-center gap-1 disabled:opacity-50"
                          style={{ background: "var(--ns-subtle)", color: "var(--ns-text)" }}>
                          <I name="cloud_download" className="text-sm" />qwen2.5:7b
                        </button>
                      </>
                    )}
                  </div>

                  {/* Barra de progreso pull */}
                  {pullProgress && (
                    <div>
                      <div className="flex justify-between text-[10px] mb-1" style={{ color: "var(--ns-muted)" }}>
                        <span>{pullProgress.status}</span>
                        <span>{pullProgress.pct}%</span>
                      </div>
                      <div className="h-2 rounded-full overflow-hidden" style={{ background: "var(--ns-subtle)" }}>
                        <div className="h-full rounded-full transition-all" style={{ width: `${pullProgress.pct}%`, background: selProv.gradient }} />
                      </div>
                    </div>
                  )}

                  {/* Tutorial pasos */}
                  <details className="rounded-xl overflow-hidden" style={{ background: "rgba(37,99,235,0.06)" }}>
                    <summary className="px-4 py-3 text-xs font-bold cursor-pointer flex items-center gap-2"
                      style={{ color: selProv.color }}>
                      <I name="help_outline" className="text-sm" />¿Cómo instalar Ollama paso a paso?
                    </summary>
                    <ol className="px-4 pb-4 space-y-2">
                      {selProv.keySteps.map((step, i) => (
                        <li key={i} className="flex items-start gap-2.5 text-[11px]" style={{ color: "var(--ns-text)" }}>
                          <span className="w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-extrabold text-white shrink-0 mt-0.5"
                            style={{ background: selProv.color }}>{i + 1}</span>
                          {step}
                        </li>
                      ))}
                    </ol>
                  </details>
                </div>
              )}

              {/* Selector de modelo */}
              <ModelSelector
                prov={selProv}
                value={cfg.model || ""}
                onChange={val => setCfg({ ...cfg, model: val })}
                dynamicModels={ollama?.models || []}
              />
            </Card>
          </section>
        )}

        {/* 3. Parámetros avanzados (colapsable) */}
        <section className="mb-5">
          <details>
            <summary className="flex items-center gap-2 cursor-pointer text-xs font-extrabold uppercase tracking-wider mb-3"
              style={{ color: "var(--ns-muted)" }}>
              <I name="tune" className="text-sm" />Parámetros avanzados (Temperature, Tokens, Nube)
            </summary>
            <Card className="p-5 mt-3 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider block mb-1.5" style={{ color: "var(--ns-muted)" }}>
                    Temperature <span className="normal-case font-normal">(0–100)</span>
                  </label>
                  <input type="number" min="0" max="100"
                    value={cfg.temperature ?? 70}
                    onChange={e => setCfg({ ...cfg, temperature: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--ns-input)", color: "var(--ns-text)", border: "1.5px solid var(--ns-card-b)", outline: "none" }}
                  />
                  <p className="text-[9px] mt-1" style={{ color: "var(--ns-muted)" }}>70 = equilibrado. Más alto → más creativo.</p>
                </div>
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider block mb-1.5" style={{ color: "var(--ns-muted)" }}>
                    Tokens máximos
                  </label>
                  <input type="number" min="128" max="8192"
                    value={cfg.max_tokens ?? 1024}
                    onChange={e => setCfg({ ...cfg, max_tokens: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-lg text-sm"
                    style={{ background: "var(--ns-input)", color: "var(--ns-text)", border: "1.5px solid var(--ns-card-b)", outline: "none" }}
                  />
                </div>
              </div>
              <label className="flex items-start gap-3 cursor-pointer">
                <input type="checkbox"
                  checked={cfg.enable_cloud !== false}
                  onChange={e => setCfg({ ...cfg, enable_cloud: e.target.checked })}
                  className="mt-0.5 w-4 h-4 accent-teal-600"
                />
                <div>
                  <span className="text-sm font-medium" style={{ color: "var(--ns-text)" }}>
                    Permitir proveedores en la nube
                  </span>
                  <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                    Si se desactiva, el sistema SOLO usará Ollama local — completamente offline.
                  </p>
                </div>
              </label>
            </Card>
          </details>
        </section>

        {/* 3. Acciones principales */}
        <section className="flex items-center gap-3 mb-5 flex-wrap">
          <Btn onClick={save} disabled={busy} className="flex items-center gap-2">
            <I name="save" className="text-base" />
            {busy ? "Guardando…" : "Guardar configuración"}
          </Btn>
          <button onClick={testConnection} disabled={busy}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl border font-bold text-sm hover:bg-gray-50 transition-all disabled:opacity-50"
            style={{ borderColor: "var(--ns-card-b)", color: "var(--ns-text)" }}>
            <I name="wifi_tethering" className="text-base" />
            Probar conexión
          </button>
        </section>

        {/* Resultado del health check (visual) */}
        {health && (
          <Card className="p-5">
            <p className="text-xs font-extrabold uppercase tracking-wider mb-3 flex items-center gap-2"
              style={{ color: "var(--ns-muted)" }}>
              <I name="monitor_heart" className="text-sm" />Estado de proveedores
            </p>
            <div className="space-y-2">
              {Array.isArray(health.providers) ? health.providers.map((p, i) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-xl"
                  style={{ background: "var(--ns-subtle)" }}>
                  <StatusChip ok={p.ok} label={p.ok ? "Activo" : "Sin conexión"} />
                  <span className="text-sm font-bold" style={{ color: "var(--ns-text)" }}>{p.id || p.name || `Proveedor ${i+1}`}</span>
                  {p.model && <span className="text-xs" style={{ color: "var(--ns-muted)" }}>{p.model}</span>}
                  {p.error && <span className="text-xs text-rose-500 truncate max-w-xs">{p.error}</span>}
                </div>
              )) : (
                <div className="flex items-center gap-3 p-3 rounded-xl" style={{ background: "var(--ns-subtle)" }}>
                  <StatusChip ok={health.ok || health.status === "ok"} label={health.status || "desconocido"} />
                  <pre className="text-[10px] overflow-auto" style={{ color: "var(--ns-muted)" }}>
                    {JSON.stringify(health, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Footer aviso privacidad */}
        <div className="mt-6 p-4 rounded-2xl text-center text-[10px] leading-relaxed"
          style={{ background: "var(--ns-subtle)", color: "var(--ns-muted)" }}>
          <I name="shield" fill className="text-xs mr-1" style={{ color: TEAL }} />
          NeuroSoft sanitiza automáticamente nombres, documentos y fechas antes de
          enviar cualquier texto a proveedores externos. Los datos clínicos identificables
          nunca salen de tu equipo sin anonimización previa.
        </div>
      </main>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
 * AIFloatingChat — botón flotante + side-panel
 * ═══════════════════════════════════════════════════════════════════════ */
const SUGGESTION_CHIPS = [
  { label: "Interpretar Z = -1.5",       prompt: "¿Cómo interpreto clínicamente un puntaje Z de -1.5 en una prueba de memoria verbal?" },
  { label: "Redactar conclusión",         prompt: "Ayúdame a redactar una conclusión diagnóstica para un perfil neuropsicológico con afectación en memoria y función ejecutiva." },
  { label: "Recomendar intervención",     prompt: "¿Qué intervenciones cognitivas son más efectivas para pacientes con deterioro leve en memoria de trabajo?" },
  { label: "¿Qué es el RCI?",             prompt: "Explica brevemente qué es el Índice de Cambio Confiable (RCI) y cómo se interpreta en neuropsicología clínica." },
  { label: "Diferencia WISC vs WAIS",    prompt: "¿Cuál es la diferencia clínica principal entre aplicar el WISC-IV y el WAIS-III?" },
];

export function AIFloatingChat() {
  const [open,     setOpen]     = useState(false);
  const [msgs,     setMsgs]     = useState([{
    role: "assistant",
    content: "Hola 👋 Soy el asistente clínico de NeuroSoft. Puedo ayudarte con interpretación de puntajes, redacción de informes o dudas técnicas.\n\n¿En qué te ayudo hoy?",
  }]);
  const [input,    setInput]    = useState("");
  const [busy,     setBusy]     = useState(false);
  const [showChips, setShowChips] = useState(true);
  const scrollRef  = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [msgs, open]);

  const send = useCallback(async (text) => {
    const t = (text || input).trim();
    if (!t || busy) return;
    const userMsg = { role: "user", content: t };
    setMsgs(m => [...m, userMsg]);
    setInput("");
    setBusy(true);
    setShowChips(false);
    try {
      const r = await aiPost("/api/v1/ai/chat", {
        messages: [...msgs, userMsg].map(m => ({ role: m.role, content: m.content })),
      });
      setMsgs(m => [...m, {
        role: "assistant",
        content: r.content || r.reply || "(respuesta vacía)",
        provider: `${r.provider || "?"}${r.model ? " · " + r.model : ""}`,
      }]);
    } catch (e) {
      setMsgs(m => [...m, { role: "assistant", content: `⚠ Error: ${e.message}`, error: true }]);
    }
    setBusy(false);
  }, [input, busy, msgs]);

  const onKey = e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  const clearChat = () => {
    setMsgs([{ role: "assistant", content: "Hola 👋 Soy el asistente clínico de NeuroSoft. ¿En qué te ayudo?" }]);
    setShowChips(true);
    setInput("");
  };

  return (
    <>
      {/* FAB */}
      <button
        onClick={() => setOpen(v => !v)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center text-white transition-all hover:scale-105 active:scale-95"
        style={{ background: `linear-gradient(135deg,${NAVY},${TEAL})`, boxShadow: `0 8px 24px -4px ${TEAL}60` }}
        title="Asistente IA (Ctrl+Shift+A)"
      >
        <I name={open ? "close" : "smart_toy"} fill className="text-2xl" />
      </button>

      {/* Panel */}
      {open && (
        <div
          className="fixed bottom-24 right-6 z-40 w-[420px] max-w-[calc(100vw-3rem)] flex flex-col rounded-3xl shadow-2xl overflow-hidden"
          style={{
            height: "clamp(420px, 65vh, 620px)",
            background: "var(--ns-card)",
            border: "1px solid var(--ns-card-b)",
          }}
        >
          {/* Header */}
          <div className="p-4 flex items-center justify-between shrink-0"
            style={{ background: `linear-gradient(135deg,${NAVY},${TEAL})`, color: "white" }}>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-white/20 flex items-center justify-center">
                <I name="psychology" fill className="text-base" />
              </div>
              <div>
                <p className="font-bold text-sm leading-tight">Asistente Clínico</p>
                <p className="text-[10px] opacity-75">NeuroSoft AI · PHI sanitizado</p>
              </div>
            </div>
            <button onClick={clearChat}
              className="text-[10px] font-bold opacity-75 hover:opacity-100 flex items-center gap-1 px-2 py-1 rounded-lg bg-white/10 hover:bg-white/20 transition-all">
              <I name="delete_sweep" className="text-xs" />Limpiar
            </button>
          </div>

          {/* Mensajes */}
          <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-3"
            style={{ background: "var(--ns-subtle)" }}>

            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                {m.role === "assistant" && (
                  <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mr-2 mt-0.5"
                    style={{ background: `${TEAL}20` }}>
                    <I name="psychology" className="text-xs" style={{ color: TEAL }} />
                  </div>
                )}
                <div className={`max-w-[85%] p-3 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${
                  m.role === "user"
                    ? "rounded-br-sm text-white"
                    : m.error
                    ? "rounded-bl-sm border"
                    : "rounded-bl-sm border"
                }`}
                  style={m.role === "user"
                    ? { background: TEAL }
                    : m.error
                    ? { background: "rgba(239,68,68,0.08)", borderColor: "#fca5a5", color: "#991b1b" }
                    : { background: "var(--ns-card)", borderColor: "var(--ns-card-b)", color: "var(--ns-text)" }
                  }>
                  {m.content}
                  {m.provider && (
                    <span className="block text-[9px] mt-1.5 opacity-50">via {m.provider}</span>
                  )}
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {busy && (
              <div className="flex justify-start items-center gap-2">
                <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0"
                  style={{ background: `${TEAL}20` }}>
                  <I name="psychology" className="text-xs" style={{ color: TEAL }} />
                </div>
                <div className="p-3 rounded-2xl rounded-bl-sm border flex items-center gap-1.5"
                  style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
                  {[0, 150, 300].map(delay => (
                    <div key={delay}
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ background: TEAL, animationDelay: `${delay}ms` }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Chips de sugerencias (solo al inicio) */}
            {showChips && msgs.length <= 1 && (
              <div className="pt-2">
                <p className="text-[10px] font-bold mb-2 uppercase tracking-wider" style={{ color: "var(--ns-muted)" }}>
                  Preguntas frecuentes
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {SUGGESTION_CHIPS.map((c, i) => (
                    <button
                      key={i}
                      onClick={() => send(c.prompt)}
                      className="text-[11px] font-medium px-3 py-1.5 rounded-full border transition-all hover:shadow-sm"
                      style={{
                        background: "var(--ns-card)",
                        borderColor: "var(--ns-card-b)",
                        color: "var(--ns-text)",
                      }}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-3 shrink-0 space-y-2 border-t" style={{ background: "var(--ns-card)", borderColor: "var(--ns-card-b)" }}>
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={onKey}
                rows={2}
                placeholder="Escribe tu pregunta… (Enter para enviar)"
                className="flex-1 px-3 py-2 rounded-xl resize-none text-sm"
                style={{
                  background: "var(--ns-input)",
                  color: "var(--ns-text)",
                  border: "1.5px solid var(--ns-card-b)",
                  outline: "none",
                }}
              />
              <button
                onClick={() => send()}
                disabled={busy || !input.trim()}
                className="p-3 rounded-xl text-white font-bold disabled:opacity-40 transition-all hover:scale-105 active:scale-95"
                style={{ background: busy ? "var(--ns-muted)" : TEAL }}
              >
                <I name="send" fill className="text-base" />
              </button>
            </div>
            <p className="text-[9px] text-center" style={{ color: "var(--ns-muted)" }}>
              Los datos del paciente se sanitizan antes de enviar · Shift+Enter = nueva línea
            </p>
          </div>
        </div>
      )}
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════════
 * ImproveButton — botón inline para mejorar texto de cualquier textarea
 * ═══════════════════════════════════════════════════════════════════════ */
export function ImproveButton({ getText, setText, mode = "style", label = "Mejorar con IA" }) {
  const [busy, setBusy] = useState(false);
  const [err,  setErr]  = useState("");
  const run = async () => {
    const t = getText ? getText() : "";
    if (!t || t.length < 10) { setErr("Texto muy corto"); return; }
    setBusy(true); setErr("");
    try {
      const r = await improveWithAI(t, mode);
      if (r.improved && setText) setText(r.improved);
    } catch (e) { setErr(e.message); }
    setBusy(false);
  };
  return (
    <div className="inline-flex items-center gap-2">
      <button
        onClick={run} disabled={busy}
        className="text-xs px-3 py-1.5 rounded-lg border flex items-center gap-1 font-bold transition-all hover:shadow-sm disabled:opacity-40"
        style={{ background: `${TEAL}10`, color: TEAL, borderColor: `${TEAL}30` }}
      >
        <I name="auto_fix_high" className="text-sm" />
        {busy ? "Procesando…" : label}
      </button>
      {err && <span className="text-[10px] text-rose-600">{err}</span>}
    </div>
  );
}

export default AIConfigPage;
