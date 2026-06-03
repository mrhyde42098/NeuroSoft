/* ═══════════════════════════════════════════════════════════════════════
 * src/app/layout/Sidebar.jsx — Navegación principal
 * ───────────────────────────────────────────────────────────────────────
 * Sidebar fijo a la izquierda con:
 *   • Logo + branding
 *   • Avatar del usuario con dropdown (Configuración / Logout)
 *   • Navegación agrupada en 4 secciones temáticas
 *   • Botón CTA "Nueva Evaluación"
 *   • Toggle modo oscuro + acceso a atajos de teclado
 *
 * Las secciones reflejan el flujo clínico:
 *   Recibir → Evaluar → Rehabilitar → Herramientas
 *
 * Props:
 *   • page          string   — id de la página activa
 *   • setPage       fn       — cambia la página activa
 *   • shortcuts     array    — para el modal de atajos (Alt+H)
 *   • TEAL/NAVY     strings  — tokens de marca (paleta inyectada)
 *   • BrainLogo,I   componentes — primitivos visuales
 *   • useAuth/useDark — hooks del contexto inyectados como props para
 *     no acoplar este archivo a la implementación de los providers.
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useEffect, useState } from "react";

const GROUPS = [
  {
    title: "Clínica",
    items: [
      { id: "dashboard", ic: "home",             lb: "Inicio" },
      { id: "patients",  ic: "group",            lb: "Pacientes" },
      { id: "agenda",    ic: "calendar_today",   lb: "Agenda" },
    ],
  },
  {
    title: "Evaluación",
    items: [
      { id: "evaluation", ic: "psychology",       lb: "Aplicar evaluación" },
      { id: "screening",  ic: "checklist",        lb: "Screening" },
      { id: "history",    ic: "history",          lb: "Historial" },
      { id: "compare",    ic: "compare_arrows",   lb: "Pre–Post" },
      { id: "reports",    ic: "description",      lb: "Informes" },
    ],
  },
  {
    title: "Psicoterapia",
    items: [
      { id: "therapy", ic: "psychology_alt", lb: "Sesiones clínicas" },
    ],
  },
  {
    title: "Rehabilitación",
    items: [
      { id: "rehab", ic: "fitness_center", lb: "Plan & Actividades" },
    ],
  },
  {
    title: "Aprender",
    items: [
      { id: "aprender",             ic: "school",         lb: "Centro de aprendizaje" },
      { id: "biblioteca",           ic: "auto_stories",   lb: "Biblioteca clínica" },
      { id: "aprender_glosario",    ic: "translate",      lb: "Glosario neuropsi" },
      { id: "aprender_estudiar",    ic: "psychology",     lb: "Tarjetas estudio" },
      { id: "aprender_quiz",        ic: "quiz",           lb: "Quizzes" },
      { id: "aprender_articulos",   ic: "article",        lb: "Artículos clínicos" },
      { id: "aprender_simulador",   ic: "psychology_alt", lb: "Simulador de casos" },
      { id: "pruebas",              ic: "rule",           lb: "Pruebas disponibles" },
    ],
  },
  {
    title: "Herramientas",
    items: [
      { id: "ai",     ic: "smart_toy", lb: "Asistente IA" },
      { id: "shares",       ic: "share",       lb: "Telemedicina" },
      { id: "help",         ic: "help",        lb: "Ayuda" },
      { id: "help_changelog", ic: "new_releases", lb: "Registro de cambios" },
    ],
  },
];

export default function Sidebar({
  page,
  setPage,
  user,
  logout,
  dark,
  toggle,
  shortcuts = [],
  BrainLogo,
  I,
  TEAL = "#0D9488",
  NAVY = "#1E293B",
}) {
  const [showShortcuts,   setShowShortcuts]   = useState(false);
  const [showUserMenu,    setShowUserMenu]    = useState(false);
  const [projection,      setProjection]      = useState(false);

  /* Modo proyección: aplica clase css que escala toda la UI */
  useEffect(() => {
    if (projection) {
      document.documentElement.classList.add("ns-projection");
    } else {
      document.documentElement.classList.remove("ns-projection");
    }
    return () => document.documentElement.classList.remove("ns-projection");
  }, [projection]);

  return (
    <>
      <aside
        className="fixed left-0 top-0 h-full flex flex-col p-5 w-72 z-50"
        style={{
          background: "var(--ns-sidebar)",
          backdropFilter: "blur(40px)",
          borderRight: "1px solid var(--ns-card-b)",
        }}
      >
        {/* §editorial: brand con tipografía mixta (sans + serif) — look más editorial */}
        <div className="mb-6 px-2 flex items-center gap-3">
          <BrainLogo size={38} />
          <div className="leading-none">
            <h1 className="leading-none" style={{ color: "var(--ns-text)" }}>
              <span className="text-[22px] font-bold tracking-tight">Neuro</span>
              <span className="ns-serif-italic text-[24px]" style={{ color: TEAL }}>Soft</span>
            </h1>
            <p className="ns-eyebrow mt-1.5">Gestión clínica</p>
          </div>
        </div>

        {/* User chip + dropdown */}
        <div className="relative mb-4">
          <button
            onClick={() => setShowUserMenu((s) => !s)}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-2xl hover:bg-gray-100 transition-all text-left"
            style={{ background: showUserMenu ? "var(--ns-subtle)" : "transparent" }}
          >
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs shrink-0"
              style={{ background: `${TEAL}20`, color: TEAL }}
            >
              {(user?.nombre_completo || "U")[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold truncate" style={{ color: "var(--ns-text)" }}>
                {user?.nombre_completo || "Usuario"}
              </p>
              <p
                className="text-[10px] font-bold uppercase tracking-wider"
                style={{ color: "var(--ns-muted)" }}
              >
                {user?.role}
              </p>
            </div>
            <I
              name={showUserMenu ? "expand_less" : "expand_more"}
              className="text-base opacity-60"
            />
          </button>
          {showUserMenu && (
            <div
              className="absolute top-full left-0 right-0 mt-1 rounded-2xl shadow-2xl overflow-hidden z-50"
              style={{ background: "var(--ns-card)", border: "1px solid var(--ns-card-b)" }}
            >
              <button
                onClick={() => {
                  setPage("config");
                  setShowUserMenu(false);
                }}
                className="w-full px-4 py-2.5 text-left text-sm font-medium hover:bg-gray-100 flex items-center gap-2"
                style={{ color: "var(--ns-text)" }}
              >
                <I name="settings" className="text-base opacity-60" />
                Configuración
              </button>
              <button
                onClick={() => {
                  logout();
                  setShowUserMenu(false);
                }}
                className="w-full px-4 py-2.5 text-left text-sm font-medium hover:bg-red-50 hover:text-red-600 flex items-center gap-2"
                style={{ color: "var(--ns-text)" }}
              >
                <I name="logout" className="text-base opacity-60" />
                Cerrar sesión
              </button>
            </div>
          )}
        </div>

        {/* Navegación agrupada */}
        <nav className="flex flex-col gap-3 flex-grow overflow-y-auto">
          {GROUPS.map((g, gi) => (
            <div key={gi} className="flex flex-col gap-1">
              <p
                className="text-[9px] font-extrabold uppercase tracking-[0.2em] px-3 mb-0.5"
                style={{ color: "var(--ns-muted)", opacity: 0.7 }}
              >
                {g.title}
              </p>
              {g.items.map((l) => {
                const active = page === l.id;
                return (
                  /* §editorial: botones más sobrios — rounded-md (6px) en lugar
                   * de rounded-2xl (16px), barra indicadora vertical en activo,
                   * sin sombra dramática. Look "menú editorial", no "app móvil". */
                  <button
                    key={l.id}
                    onClick={() => setPage(l.id)}
                    aria-current={active ? "page" : undefined}
                    aria-label={active ? `${l.lb} (página actual)` : l.lb}
                    className={`relative flex items-center gap-3 pl-4 pr-3 py-2 rounded-md transition-all text-left w-full focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 ${
                      active ? "" : "hover:bg-gray-100"
                    }`}
                    style={
                      active
                        ? { background: `${TEAL}10`, color: TEAL }
                        : { color: "var(--ns-muted)" }
                    }
                  >
                    {active && (
                      <span
                        className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r"
                        style={{ background: TEAL }}
                      />
                    )}
                    <I
                      name={l.ic}
                      fill={active}
                      className={active ? "text-[18px]" : "text-[18px] opacity-55"}
                    />
                    <span className={`text-[13px] ${active ? "font-bold" : "font-medium"}`}>
                      {l.lb}
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* §editorial: footer CTA sobrio — sin gradient, navy sólido,
          * sombra contenida. Botón cuadrado-redondeado en lugar de píldora. */}
        <div className="mt-auto flex flex-col gap-3 pt-3">
          <button
            onClick={() => setPage("evaluation")}
            className="w-full py-3 text-white rounded-md font-bold flex items-center justify-center gap-2 transition-all text-[13px] tracking-tight hover:opacity-90"
            style={{
              background: NAVY,
              boxShadow: "0 4px 12px -3px rgba(30,41,59,0.25)",
            }}
          >
            <I name="add" className="text-base" />
            Nueva evaluación
          </button>
          <div className="flex items-center justify-between px-2 gap-1">
            <button
              onClick={toggle}
              className="flex-1 py-2 rounded-xl text-[11px] font-bold flex items-center justify-center gap-1.5 hover:bg-gray-100 transition-all"
              style={{ color: "var(--ns-muted)" }}
              title="Modo oscuro (D)"
            >
              <I name={dark ? "light_mode" : "dark_mode"} className="text-base" />
              {dark ? "Claro" : "Oscuro"}
            </button>
            <button
              onClick={() => setProjection(p => !p)}
              className={`py-2 px-3 rounded-xl transition-all ${projection ? "text-white" : "hover:bg-gray-100"}`}
              style={projection ? { background: TEAL } : { color: "var(--ns-muted)" }}
              title="Modo proyección (pantalla grande)"
            >
              <I name={projection ? "zoom_in_map" : "zoom_out_map"} className="text-base" />
            </button>
            <button
              onClick={() => setShowShortcuts(true)}
              className="py-2 px-3 rounded-xl hover:bg-gray-100"
              style={{ color: "var(--ns-muted)" }}
              title="Atajos (?)"
            >
              <I name="keyboard" className="text-base" />
            </button>
          </div>
        </div>
      </aside>

      {/* Modal de atajos */}
      {showShortcuts && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center"
          style={{ background: "rgba(0,0,0,0.5)" }}
          onClick={() => setShowShortcuts(false)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl"
            style={{ background: "var(--ns-card)" }}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <I name="keyboard" style={{ color: TEAL }} />
                Atajos de Teclado
              </h3>
              <button
                onClick={() => setShowShortcuts(false)}
                className="p-2 rounded-lg hover:bg-gray-100"
              >
                <I name="close" />
              </button>
            </div>
            <div className="space-y-2">
              {shortcuts.map((s) => (
                <div
                  key={s.key}
                  className="flex items-center justify-between py-2 border-b"
                  style={{ borderColor: "var(--ns-card-b)" }}
                >
                  <span className="text-sm" style={{ color: "var(--ns-muted)" }}>
                    {s.desc}
                  </span>
                  <kbd
                    className="px-3 py-1 rounded-lg text-xs font-bold"
                    style={{ background: "var(--ns-subtle)", color: "var(--ns-text)" }}
                  >
                    Alt+{s.key.toUpperCase()}
                  </kbd>
                </div>
              ))}
            </div>
            <p
              className="text-[10px] text-center mt-4"
              style={{ color: "var(--ns-muted)" }}
            >
              Mantenga presionado Alt + la tecla
            </p>
          </div>
        </div>
      )}
    </>
  );
}
