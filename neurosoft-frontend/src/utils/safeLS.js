/* ═══════════════════════════════════════════════════════════════════════
 * src/utils/safeLS.js — Wrapper defensivo de localStorage
 * ───────────────────────────────────────────────────────────────────────
 * §M5-fix: localStorage puede lanzar excepciones en escenarios reales:
 *   - Modo privado de Safari (cuota = 0)
 *   - Almacenamiento deshabilitado por política corporativa
 *   - QuotaExceededError cuando se llena el espacio del dominio
 *   - SecurityError en algunos entornos sandboxed (iframes cross-origin)
 *
 * Antes había 49 llamadas a localStorage y solo 4 estaban en try/catch.
 * Un fallo de localStorage rompía el flow del clínico sin necesidad.
 *
 * Uso recomendado:
 *   import { safeLS } from "../../utils/safeLS.js";
 *   const token = safeLS.get("ns_token");
 *   safeLS.set("ns_dark", "1");
 *
 * Compatibilidad: API mínima compatible con localStorage para reemplazo
 * mecánico (get, set, remove). NO uses para datos críticos que requieran
 * confirmar el guardado — usa el backend.
 * ═══════════════════════════════════════════════════════════════════════ */

/** Devuelve el valor o null si falla. */
function get(key) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

/** Guarda. Devuelve true si tuvo éxito, false si falló (sin lanzar). */
function set(key, value) {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch (e) {
    // Cuota llena, modo privado, política. No spameamos consola — solo debug.
    try { console.debug("[safeLS] set falló para", key, "—", e?.name || e); } catch {}
    return false;
  }
}

/** Elimina. No lanza. */
function remove(key) {
  try {
    localStorage.removeItem(key);
    return true;
  } catch {
    return false;
  }
}

/** Devuelve un objeto parseado o `fallback` si falla parsing o storage. */
function getJSON(key, fallback = null) {
  const raw = get(key);
  if (raw == null) return fallback;
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

/** Guarda un objeto JSON (stringify + set). True si tuvo éxito. */
function setJSON(key, value) {
  try {
    return set(key, JSON.stringify(value));
  } catch {
    return false;
  }
}

/** Verifica si localStorage está disponible en este entorno. */
function isAvailable() {
  try {
    const t = "__ns_test__";
    localStorage.setItem(t, "1");
    localStorage.removeItem(t);
    return true;
  } catch {
    return false;
  }
}

export const safeLS = {
  get, set, remove, getJSON, setJSON, isAvailable,
};

export default safeLS;
