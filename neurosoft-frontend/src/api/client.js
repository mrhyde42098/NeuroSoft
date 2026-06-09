/* ═══════════════════════════════════════════════════════════════════════
 * src/api/client.js — Cliente HTTP centralizado
 * ───────────────────────────────────────────────────────────────────────
 * Encapsula:
 *   • Inyección de Bearer token desde localStorage
 *   • Detección de 401 → flush de sesión + reload
 *   • Parseo amigable de errores Pydantic en español
 *   • Endpoints REST + descarga de blobs
 *
 * En producción (bundle empaquetado) usa origen relativo.
 * En desarrollo apunta a http://localhost:8000 (proxy Vite o directo).
 * ═══════════════════════════════════════════════════════════════════════ */

import { safeLS } from "../utils/safeLS.js";

export const API = import.meta.env.PROD ? "" : "http://localhost:8000";

/* §C7-fix: solo borramos claves de SESIÓN. Antes hacíamos
 * localStorage.clear() y esto eliminaba preferencias (ns_dark, ns_a11y_*)
 * y, peor, los timestamps ns_codif_t_* que sostienen la validez del
 * intervalo de recobro diferido durante una evaluación en curso.
 * §M5-fix: usamos safeLS para no romper en modo privado / cuota llena. */
const _SESSION_KEYS = ["ns_token", "ns_user"];
const _chk401 = (r) => {
  if (r.status === 401 && safeLS.get("ns_token")) {
    _SESSION_KEYS.forEach((k) => safeLS.remove(k));
    window.location.reload();
    return true;
  }
  return false;
};

const _hdrs = (json) => {
  const t = safeLS.get("ns_token");
  const h = { ...(t ? { Authorization: `Bearer ${t}` } : {}) };
  if (json) h["Content-Type"] = "application/json";
  return h;
};

const _fetch = async (url, opts, timeoutMs = 15000) => {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch(url, { ...opts, signal: ctrl.signal });
    clearTimeout(timer);
    return r;
  } catch (e) {
    clearTimeout(timer);
    const isTimeout = e.name === "AbortError";
    throw {
      status: 0,
      detail: isTimeout
        ? "La solicitud tardó demasiado. Verifique que el backend esté respondiendo."
        : "No se puede conectar al servidor. Verifique que el backend esté ejecutándose en puerto 8000.",
    };
  }
};

/* Mapeo de campos técnicos a nombres legibles en español */
export const _fieldNames = {
  primer_nombre: "Primer nombre", segundo_nombre: "Segundo nombre",
  primer_apellido: "Primer apellido", segundo_apellido: "Segundo apellido",
  numero_documento: "Número de documento", tipo_documento: "Tipo de documento",
  fecha_nacimiento: "Fecha de nacimiento", fecha_atencion: "Fecha de atención",
  sexo: "Sexo", escolaridad: "Escolaridad", lateralidad: "Lateralidad",
  estado_civil: "Estado civil", lugar_nacimiento: "Lugar de nacimiento",
  telefono: "Teléfono", correo: "Correo electrónico", direccion: "Dirección",
  ciudad: "Ciudad", localidad: "Localidad", estrato: "Estrato",
  ocupacion: "Ocupación", acompanante: "Acompañante", grupo_etnico: "Grupo étnico",
  profesional_id: "Profesional", motivo_consulta: "Motivo de consulta",
  remite: "Remite", eps: "EPS", orden_medica_no: "Orden médica",
  discapacidad: "Discapacidad", codigo_rips: "Código RIPS", cups: "CUPS",
  finalidad_consulta: "Finalidad consulta", numero_sesiones: "Número de sesiones",
  nombre_completo: "Nombre completo", registro_profesional: "Registro profesional",
  titulo: "Título", especialidad: "Especialidad", email: "Email",
  patient_id: "Paciente", fecha: "Fecha", hora_inicio: "Hora inicio",
  hora_fin: "Hora fin", tipo_cita: "Tipo de cita", motivo: "Motivo",
  nombre: "Nombre", nit: "NIT",
  via_atencion: "Vía de atención",
};

const _msgMap = {
  "String should have at least": "debe tener al menos",
  "characters": "caracteres",
  "field required": "es obligatorio",
  "value is not a valid": "valor no válido",
  "Input should be a valid date": "debe ser una fecha válida",
  "input is too short": "el valor es muy corto",
  "ensure this value has at": "debe tener al menos",
  "Input should be": "debe ser",
  "Extra inputs are not permitted": "campo no permitido",
  "Value error": "Error de valor",
};

/** Códigos NeuroSoft → mensaje amigable (sincronizado con app/core/error_codes.py). */
export const ERROR_MESSAGES_ES = {
  PATIENT_ALREADY_EXISTS: "Ya existe un paciente con ese documento en la fecha indicada.",
  PATIENT_NOT_FOUND: "Paciente no encontrado.",
  EVALUATION_NOT_FOUND: "Evaluación no encontrada.",
  EVALUATION_ALREADY_SIGNED: "La evaluación ya está firmada y no puede modificarse.",
  EVALUATION_NOT_SIGNED: "La evaluación aún no ha sido firmada.",
  CONCURRENCY_CONFLICT: "Otro usuario modificó este registro. Recargue e intente de nuevo.",
  BAREMO_NOT_FOUND: "No hay baremo disponible para esta prueba.",
  INVALID_SCORE: "Puntaje inválido para esta prueba.",
  AGE_OUT_OF_RANGE: "La edad del paciente está fuera del rango normativo.",
  BAREMO_DB_NOT_LOADED: "Base de baremos no cargada. Reinicie el servidor.",
  DATABASE_ERROR: "Error de base de datos. Intente de nuevo.",
  REPORT_GENERATION_ERROR: "No se pudo generar el informe.",
};

const _normalizeApiErrorBody = (e) => {
  if (!e || typeof e !== "object") return e;
  const d = e.detail;
  if (d && typeof d === "object" && !Array.isArray(d)) {
    const code = d.error || d.code;
    if (code && ERROR_MESSAGES_ES[code]) {
      return { ...d, message: d.message || ERROR_MESSAGES_ES[code] };
    }
    return d;
  }
  return e;
};

export const _parseError = (e) => {
  if (!e) return "Error desconocido";
  if (typeof e === "string") return e;
  const norm = _normalizeApiErrorBody(e);
  if (norm?.message && typeof norm.message === "string") return norm.message;
  if (typeof e.detail === "string") return e.detail;
  if (norm?.error && ERROR_MESSAGES_ES[norm.error]) return ERROR_MESSAGES_ES[norm.error];
  if (Array.isArray(e.detail)) {
    return e.detail
      .map((err) => {
        const field = (err.loc || []).filter((l) => l !== "body").pop() || "Campo";
        const fname = _fieldNames[field] || field.replace(/_/g, " ");
        let msg = err.msg || "error de validación";
        Object.entries(_msgMap).forEach(([en, es]) => {
          msg = msg.replace(en, es);
        });
        return `${fname}: ${msg}`;
      })
      .join(". ");
  }
  if (e.detail) return JSON.stringify(e.detail);
  if (e.message) return e.message;
  return "Error inesperado";
};

export const api = {
  async post(u, b) {
    const r = await _fetch(`${API}${u}`, {
      method: "POST", headers: _hdrs(true), body: JSON.stringify(b),
    });
    if (_chk401(r)) return;
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      throw { status: r.status, detail: d.detail || `Error ${r.status}: ${r.statusText}` };
    }
    return r.json();
  },
  async get(u) {
    const r = await _fetch(`${API}${u}`, { headers: _hdrs() });
    if (_chk401(r)) return;
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      throw { status: r.status, detail: d.detail || `Error ${r.status}` };
    }
    return r.json();
  },
  async patch(u, b) {
    const r = await _fetch(`${API}${u}`, {
      method: "PATCH", headers: _hdrs(true), body: JSON.stringify(b),
    });
    if (_chk401(r)) return;
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      throw { status: r.status, detail: d.detail || `Error ${r.status}: ${r.statusText}` };
    }
    return r.json();
  },
  async put(u, b) {
    const r = await _fetch(`${API}${u}`, {
      method: "PUT", headers: _hdrs(true), body: JSON.stringify(b),
    });
    if (_chk401(r)) return;
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      throw { status: r.status, detail: d.detail || `Error ${r.status}: ${r.statusText}` };
    }
    return r.json();
  },
  async del(u) {
    const r = await _fetch(`${API}${u}`, { method: "DELETE", headers: _hdrs() });
    if (_chk401(r)) return;
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      throw { status: r.status, detail: d.detail || `Error ${r.status}` };
    }
    return r.status === 204 ? null : r.json();
  },
  async blob(u, method = "POST") {
    const r = await _fetch(`${API}${u}`, { method, headers: _hdrs() });
    if (_chk401(r)) return;
    if (!r.ok) {
      const err = await r.text().catch(() => "Error");
      throw { status: r.status, detail: err };
    }
    return r.blob();
  },
  async upload(u, file, fieldName = "file") {
    const fd = new FormData();
    fd.append(fieldName, file);
    const r = await _fetch(`${API}${u}`, { method: "POST", headers: _hdrs(false), body: fd });
    if (_chk401(r)) return;
    if (!r.ok) {
      const d = await r.json().catch(() => ({}));
      throw { status: r.status, detail: d.detail || `Error ${r.status}` };
    }
    return r.json();
  },
};

export const exportCSV = (rows, filename) => {
  if (!rows || !rows.length) return;
  const headers = Object.keys(rows[0]);
  const csv = [
    headers.join(","),
    ...rows.map((r) =>
      headers.map((h) => `"${String(r[h] ?? "").replace(/"/g, '""')}"`).join(",")
    ),
  ].join("\n");
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
};
