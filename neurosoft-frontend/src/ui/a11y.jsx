// S3.3: Helpers de accesibilidad (A11y) para NeuroSoft.
//
// Provee componentes y hooks que cumplen WCAG 2.1 AA:
//   - <SkipToMain>: link de salto para lectores de pantalla
//   - <LiveRegion>: región ARIA live para anuncios
//   - useFocusTrap: hook para focus trap en modales
//   - useEscape: hook para cerrar con tecla Escape
//   - useAnnounce: hook para anunciar mensajes a lectores de pantalla
//   - usePrefersReducedMotion: respeta prefers-reduced-motion

import { useCallback, useEffect, useRef, useState } from "react";


/* ═══════════════════════════════════════════════════════════════
 * Skip to main content — primer foco del teclado
 * ═══════════════════════════════════════════════════════════════ */

export function SkipToMain({ targetId = "ns-main-content" }) {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[10000] focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg focus:outline-2 focus:outline-teal-500"
      style={{
        background: "var(--ns-teal, #0D9488)",
        color: "#fff",
        fontWeight: 700,
        fontSize: 14,
        textDecoration: "none",
      }}
    >
      Saltar al contenido principal
    </a>
  );
}


/* ═══════════════════════════════════════════════════════════════
 * Live Region — anuncios a lectores de pantalla
 * ═══════════════════════════════════════════════════════════════ */

export function LiveRegion({ message, politeness = "polite" }) {
  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      style={{
        position: "absolute",
        width: 1,
        height: 1,
        margin: -1,
        padding: 0,
        overflow: "hidden",
        clip: "rect(0,0,0,0)",
        whiteSpace: "nowrap",
        border: 0,
      }}
    >
      {message}
    </div>
  );
}


export function useAnnounce() {
  const [msg, setMsg] = useState("");
  const [politeness, setPoliteness] = useState("polite");
  const announce = useCallback((text, level = "polite") => {
    setPoliteness(level);
    setMsg(""); // reset para forzar re-anuncio
    requestAnimationFrame(() => setMsg(String(text || "")));
  }, []);
  const LiveAnnouncer = useCallback(
    () => <LiveRegion message={msg} politeness={politeness} />,
    [msg, politeness]
  );
  return { announce, LiveAnnouncer };
}


/* ═══════════════════════════════════════════════════════════════
 * Focus trap — para modales y diálogos
 * ═══════════════════════════════════════════════════════════════ */

const FOCUSABLE = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

export function useFocusTrap(active = true) {
  const ref = useRef(null);

  useEffect(() => {
    if (!active || !ref.current) return;
    const root = ref.current;
    const previouslyFocused = document.activeElement;

    const focusables = () => Array.from(root.querySelectorAll(FOCUSABLE));

    const onKey = (e) => {
      if (e.key !== "Tab") return;
      const list = focusables();
      if (list.length === 0) {
        e.preventDefault();
        return;
      }
      const first = list[0];
      const last = list[list.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    root.addEventListener("keydown", onKey);
    // Foco inicial: primer focusable
    const first = focusables()[0];
    if (first) first.focus();
    else root.focus();

    return () => {
      root.removeEventListener("keydown", onKey);
      if (previouslyFocused && previouslyFocused.focus) {
        previouslyFocused.focus();
      }
    };
  }, [active]);

  return ref;
}


/* ═══════════════════════════════════════════════════════════════
 * Escape — cerrar con tecla Escape
 * ═══════════════════════════════════════════════════════════════ */

export function useEscape(active = true, onEscape) {
  useEffect(() => {
    if (!active || !onEscape) return;
    const onKey = (e) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onEscape(e);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [active, onEscape]);
}


/* ═══════════════════════════════════════════════════════════════
 * Prefers reduced motion
 * ═══════════════════════════════════════════════════════════════ */

export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
  });
  useEffect(() => {
    const mq = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!mq) return;
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener?.("change", onChange);
    return () => mq.removeEventListener?.("change", onChange);
  }, []);
  return reduced;
}


/* ═══════════════════════════════════════════════════════════════
 * useId — id único para aria-controls/aria-labelledby
 * ═══════════════════════════════════════════════════════════════ */

let _nsA11yIdCounter = 0;
export function useId(prefix = "ns") {
  const ref = useRef(null);
  if (ref.current === null) {
    _nsA11yIdCounter += 1;
    ref.current = `${prefix}-${_nsA11yIdCounter}`;
  }
  return ref.current;
}
