/* ═══════════════════════════════════════════════════════════════════════
 * src/app/dashboard/NotificationsWidget.jsx — Widget de notificaciones
 * ───────────────────────────────────────────────────────────────────────
 * Sprint 10. Muestra las sesiones tarea-casa recientes que los
 * pacientes completaron desde su link público de rehab.
 *
 * Estado "leída" se persiste en localStorage:
 *   ns_notif_last_seen = timestamp ISO del último check
 *
 * Endpoints usados:
 *   GET /api/v1/notifications      → listado
 *   GET /api/v1/notifications/count?since=...  → badge
 * ═══════════════════════════════════════════════════════════════════════ */

import React, { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../../api/client.js";
import { Card, I } from "../../ui/primitives.jsx";
import { TEAL } from "../../ui/tokens.js";
import { safeLS } from "../../utils/safeLS.js";

const LAST_SEEN_KEY = "ns_notif_last_seen";

/* Inyectar CSS de animación una sola vez */
(function ensureStyle() {
  if (typeof document === "undefined" || document.getElementById("ns-notif-style")) return;
  const s = document.createElement("style");
  s.id = "ns-notif-style";
  s.textContent = `
@keyframes ns-badge-pop {
  0%   { transform: scale(0.6); opacity: 0; }
  70%  { transform: scale(1.25); }
  100% { transform: scale(1); opacity: 1; }
}
@keyframes ns-badge-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
  50%       { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
}
.ns-badge-pop  { animation: ns-badge-pop  0.3s cubic-bezier(0.34,1.56,0.64,1) forwards; }
.ns-badge-pulse { animation: ns-badge-pulse 2s ease-in-out infinite; }
  `;
  document.head.appendChild(s);
})();

function timeAgo(iso) {
  if (!iso) return "—";
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return iso;
  const sec = Math.floor((Date.now() - t) / 1000);
  if (sec < 60) return "ahora";
  if (sec < 3600) return `hace ${Math.floor(sec / 60)} min`;
  if (sec < 86400) return `hace ${Math.floor(sec / 3600)} h`;
  return `hace ${Math.floor(sec / 86400)} d`;
}

export default function NotificationsWidget() {
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const [lastSeen, setLastSeen] = useState(() => safeLS.get(LAST_SEEN_KEY) || "");
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const _prevUnread = useRef(0);

  const refresh = useCallback(() => {
    api.get("/api/v1/notifications?dias=14&limit=20")
      .then((rows) => {
        setItems(rows || []);
        const since = safeLS.get(LAST_SEEN_KEY) || "";
        const sinceMs = since ? new Date(since).getTime() : 0;
        const newCount = (rows || []).filter((r) => {
          const t = r.created_at ? new Date(r.created_at).getTime() : 0;
          return t > sinceMs;
        }).length;
        setUnread(newCount);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
    /* Polling cada 60 segundos */
    const t = setInterval(refresh, 60_000);
    return () => clearInterval(t);
  }, [refresh]);

  const markAllSeen = useCallback(() => {
    const now = new Date().toISOString();
    localStorage.setItem(LAST_SEEN_KEY, now);
    setLastSeen(now);
    setUnread(0);
  }, []);

  return (
    <Card className="p-5">
      <button
        onClick={() => { setOpen((o) => !o); if (!open && unread > 0) markAllSeen(); }}
        className="w-full flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="relative">
            <I name="notifications" fill={unread > 0} className="text-2xl" style={{ color: unread > 0 ? TEAL : "var(--ns-muted)" }} />
            {unread > 0 && (
              <span
                key={unread}
                className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center ns-badge-pop ns-badge-pulse"
              >
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </div>
          <div className="text-left">
            <p className="text-sm font-bold">Notificaciones</p>
            <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
              {loading ? "Cargando…"
                : items.length === 0 ? "Sin actividad reciente"
                : `${items.length} sesiones tarea-casa (14 días)`}
            </p>
          </div>
        </div>
        <I name={open ? "expand_less" : "expand_more"} className="text-base text-gray-400" />
      </button>

      {open && (
        <div className="mt-4 space-y-2 max-h-72 overflow-y-auto pr-1">
          {items.length === 0 ? (
            <div className="text-center py-4 text-xs" style={{ color: "var(--ns-muted)" }}>
              <I name="inbox" className="text-2xl opacity-30 mb-2" />
              <p>Sin actividad reciente.</p>
              <p className="text-[10px] mt-1">Las sesiones de tarea-casa aparecerán aquí.</p>
            </div>
          ) : items.map((it) => {
            const isNew = !lastSeen || (it.created_at && new Date(it.created_at) > new Date(lastSeen));
            return (
              <div key={it.id}
                className="flex items-center gap-3 p-2 rounded-xl"
                style={{ background: isNew ? `${TEAL}10` : "var(--ns-subtle)", borderLeft: isNew ? `3px solid ${TEAL}` : "3px solid transparent" }}>
                <I name={it.icon || "fitness_center"} className="text-base" style={{ color: it.color || TEAL }} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold truncate">{it.paciente_nombre}</p>
                  <p className="text-[10px]" style={{ color: "var(--ns-muted)" }}>
                    {it.activity_slug || "actividad"}{it.score != null ? ` · score ${Math.round(it.score)}` : ""}
                  </p>
                </div>
                <span className="text-[10px] shrink-0" style={{ color: "var(--ns-muted)" }}>
                  {timeAgo(it.created_at)}
                </span>
              </div>
            );
          })}
          {items.length > 0 && (
            <button
              onClick={markAllSeen}
              className="w-full text-[10px] font-bold py-2 rounded-lg hover:bg-gray-50"
              style={{ color: TEAL }}
            >
              Marcar todas como leídas
            </button>
          )}
        </div>
      )}
    </Card>
  );
}
