"""
NeuroSoft License Admin — Panel de licencias (solo titular)
Ejecutar: python admin_license_app.py
EXE:     python build_license_admin.py
"""
from __future__ import annotations

import csv
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.license_core import (  # noqa: E402
    DEFAULT_EMAIL_TEMPLATE,
    TYPE_META,
    append_history,
    backup_inventory,
    check_quota,
    decode_key,
    email_template,
    export_inventory_csv,
    generate_key,
    import_csv_inventory,
    inventory_batches,
    inventory_filter,
    inventory_mark,
    inventory_register,
    inventory_revoke,
    inventory_stats,
    load_history,
    load_settings,
    save_history_entries,
    save_settings,
)

C = {
    "bg": "#0b1220",
    "card": "#151f32",
    "border": "#2a3a52",
    "teal": "#14b8a6",
    "teal_dim": "#0d9488",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
    "accent": "#38bdf8",
    "warn": "#fbbf24",
    "ok": "#34d399",
    "danger": "#f87171",
}


def _style_ttk(root: tk.Tk) -> None:
    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass
    s.configure("TNotebook", background=C["bg"], borderwidth=0)
    s.configure("TNotebook.Tab", background=C["card"], foreground=C["muted"], padding=[12, 7], font=("Segoe UI", 10))
    s.map("TNotebook.Tab", background=[("selected", C["teal_dim"])], foreground=[("selected", "white")])
    s.configure("Treeview", background=C["bg"], foreground=C["text"], fieldbackground=C["bg"], rowheight=24)
    s.configure("Treeview.Heading", background=C["border"], foreground=C["text"], font=("Segoe UI", 9, "bold"))


class LicenseAdminApp:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.root = tk.Tk()
        self.root.title("NeuroSoft License Admin")
        self.root.geometry("1020x780")
        self.root.minsize(920, 680)
        self.root.configure(bg=C["bg"])
        _style_ttk(self.root)

        self._header()
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._tab_dashboard(nb)
        self._tab_single(nb)
        self._tab_batch(nb)
        self._tab_inventory(nb)
        self._tab_validate(nb)
        self._tab_customize(nb)
        self._tab_history(nb)
        self._tab_email(nb)
        self._tab_help(nb)
        self._refresh_stats()
        self._update_preview()
        self.root.mainloop()

    # ── Layout helpers ───────────────────────────────────────────

    def _header(self) -> None:
        h = tk.Frame(self.root, bg=C["bg"], pady=10)
        h.pack(fill="x", padx=16)
        tk.Label(h, text="⬡ NeuroSoft", font=("Segoe UI", 22, "bold"), fg=C["teal"], bg=C["bg"]).pack(side="left")
        tk.Label(h, text="License Admin", font=("Segoe UI", 11), fg=C["muted"], bg=C["bg"]).pack(side="left", padx=(10, 0))

        self.stats_frame = tk.Frame(h, bg=C["bg"])
        self.stats_frame.pack(side="right")

    def _stat_chip(self, parent, label: str, var: tk.StringVar, color: str) -> None:
        f = tk.Frame(parent, bg=C["card"], highlightbackground=C["border"], highlightthickness=1, padx=10, pady=4)
        f.pack(side="left", padx=4)
        tk.Label(f, text=label, font=("Segoe UI", 8), fg=C["muted"], bg=C["card"]).pack()
        tk.Label(f, textvariable=var, font=("Segoe UI", 14, "bold"), fg=color, bg=C["card"]).pack()

    def _refresh_stats(self) -> None:
        for w in self.stats_frame.winfo_children():
            w.destroy()
        st = inventory_stats()
        self._stat_total = tk.StringVar(value=str(st["total"]))
        self._stat_avail = tk.StringVar(value=str(st["available"]))
        self._stat_assigned = tk.StringVar(value=str(st["assigned"]))
        self._stat_revoked = tk.StringVar(value=str(st["revoked"]))
        self._stat_batches = tk.StringVar(value=str(st["batches"]))
        self._stat_chip(self.stats_frame, "Total", self._stat_total, C["accent"])
        self._stat_chip(self.stats_frame, "Disponibles", self._stat_avail, C["ok"])
        self._stat_chip(self.stats_frame, "Asignadas", self._stat_assigned, C["warn"])
        self._stat_chip(self.stats_frame, "Revocadas", self._stat_revoked, C["danger"])
        self._stat_chip(self.stats_frame, "Lotes", self._stat_batches, C["muted"])

    def _card(self, parent: tk.Widget) -> tk.Frame:
        f = tk.Frame(parent, bg=C["card"], highlightbackground=C["border"], highlightthickness=1, padx=18, pady=14)
        f.pack(fill="both", expand=True, padx=5, pady=5)
        return f

    def _field(self, parent: tk.Frame, label: str, default: str = "") -> tk.Entry:
        row = tk.Frame(parent, bg=C["card"])
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, width=18, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        e = tk.Entry(row, bg=C["bg"], fg=C["text"], insertbackground=C["text"], relief="flat", font=("Segoe UI", 10))
        e.pack(side="left", fill="x", expand=True, ipady=5, padx=(4, 0))
        if default:
            e.insert(0, default)
        return e

    def _btn(self, parent, text, cmd, primary=False) -> tk.Button:
        bg = C["teal"] if primary else C["border"]
        b = tk.Button(
            parent, text=text, command=cmd, bg=bg, fg="white" if primary else C["text"],
            activebackground=C["teal_dim"], font=("Segoe UI", 10, "bold" if primary else "normal"),
            relief="flat", padx=12, pady=7, cursor="hand2",
        )
        b.pack(side="left", padx=(0, 6))
        return b

    def _type_combo(self, parent, default: str = "beta") -> ttk.Combobox:
        cb = ttk.Combobox(parent, values=list(TYPE_META.keys()), state="readonly", width=34, font=("Segoe UI", 10))
        cb.set(default)
        return cb

    # ── Tabs ─────────────────────────────────────────────────────

    def _tab_dashboard(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Panel  ")
        card = self._card(tab)
        self.dash_lbl = tk.Label(card, text="", font=("Segoe UI", 10), fg=C["text"], bg=C["card"], justify="left")
        self.dash_lbl.pack(anchor="w", fill="x")
        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", pady=12)
        self._btn(bf, "Actualizar contadores", self._refresh_dashboard, primary=True)
        self._btn(bf, "Backup inventario", self._backup_inv)
        self._btn(bf, "Exportar inventario CSV", self._export_all_inv)
        self._btn(bf, "Importar CSV existente", self._import_csv)

    def _refresh_dashboard(self) -> None:
        self._refresh_stats()
        st = inventory_stats()
        lines = [
            f"Resumen del inventario ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "─" * 48,
            f"  Total generadas:     {st['total']}",
            f"  Disponibles:         {st['available']}",
            f"  Asignadas:           {st['assigned']}",
            f"  Revocadas:           {st['revoked']}",
            f"  Lotes distintos:     {st['batches']}",
            "",
            "Por tipo (disponibles / total):",
        ]
        for t, n in sorted(st.get("by_type", {}).items()):
            meta = TYPE_META.get(t, {})
            det = st.get("by_type_detail", {}).get(t, {})
            avail = det.get("available", 0)
            lines.append(f"  • {meta.get('label', t):16s}  {avail:4d} disp / {n:4d} total")
        batches = inventory_batches()
        if batches:
            lines += ["", "Lotes:", *[f"  • {b}" for b in batches[:12]]]
        self.dash_lbl.config(text="\n".join(lines))
        if hasattr(self, "inv_tree"):
            self._refresh_inventory_tree()

    def _tab_single(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Licencia  ")
        outer = tk.Frame(tab, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        left = self._card(outer)
        left.pack(side="left", fill="both", expand=True)
        right = self._card(outer)
        right.pack(side="right", fill="y")

        self.s_type = self._type_combo(left, "beta")
        self.s_type.bind("<<ComboboxSelected>>", lambda _: (self._toggle_days(), self._update_preview()))
        row = tk.Frame(left, bg=C["card"])
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Tipo", width=18, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.s_type.pack(in_=row, side="left", fill="x", expand=True)

        self.s_type_desc = tk.Label(left, text="", font=("Segoe UI", 9), fg=C["accent"], bg=C["card"], wraplength=440, justify="left")
        self.s_type_desc.pack(anchor="w", pady=(0, 6))

        self.s_days_frame = tk.Frame(left, bg=C["card"])
        self.s_days = tk.Spinbox(self.s_days_frame, from_=1, to=730, width=8, font=("Segoe UI", 10))
        self.s_days.delete(0, "end")
        self.s_days.insert(0, str(TYPE_META["trial"]["days_default"]))
        row_d = tk.Frame(self.s_days_frame, bg=C["card"])
        row_d.pack(fill="x")
        tk.Label(row_d, text="Días (trial)", width=18, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.s_days.pack(in_=row_d, side="left")

        self.s_name = self._field(left, "Profesional")
        self.s_email = self._field(left, "Email")
        self.s_doc = self._field(left, "Documento")
        self.s_inst = self._field(left, "Institución", self.settings.get("default_institution", ""))
        self.s_notes = self._field(left, "Notas internas")

        self.s_auto_assign = tk.BooleanVar(value=True)
        tk.Checkbutton(
            left, text="Marcar como asignada al generar", variable=self.s_auto_assign,
            bg=C["card"], fg=C["text"], selectcolor=C["bg"], activebackground=C["card"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=4)

        self.s_key = tk.StringVar(value="—")
        tk.Label(left, text="Clave NSFT", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(anchor="w", pady=(8, 2))
        tk.Entry(left, textvariable=self.s_key, font=("Consolas", 12, "bold"), justify="center",
                 bg=C["bg"], fg=C["teal"], relief="flat", state="readonly").pack(fill="x", ipady=8)

        bf = tk.Frame(left, bg=C["card"])
        bf.pack(fill="x", pady=10)
        self._btn(bf, "Generar clave", self._gen_single, primary=True)
        self._btn(bf, "Copiar", lambda: self._copy(self.s_key.get()))
        self._btn(bf, "Limpiar", self._clear_single)

        tk.Label(right, text="Vista previa", font=("Segoe UI", 11, "bold"), fg=C["text"], bg=C["card"]).pack(anchor="w")
        self.preview = tk.Label(right, text="", font=("Segoe UI", 9), fg=C["muted"], bg=C["card"], justify="left", wraplength=280)
        self.preview.pack(anchor="w", pady=8)
        self._toggle_days()

    def _tab_batch(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Lote CSV  ")
        card = self._card(tab)

        self.b_count = tk.Spinbox(card, from_=1, to=10000, width=10, font=("Segoe UI", 10))
        self.b_count.delete(0, "end")
        self.b_count.insert(0, str(self.settings.get("default_batch_size", 50)))
        row = tk.Frame(card, bg=C["card"])
        row.pack(fill="x", pady=4)
        tk.Label(row, text="Cantidad", width=18, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.b_count.pack(in_=row, side="left")

        self.b_type = self._type_combo(card, "beta")
        row2 = tk.Frame(card, bg=C["card"])
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="Tipo", width=18, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.b_type.pack(in_=row2, side="left", fill="x", expand=True)

        self.b_days = tk.Spinbox(card, from_=1, to=365, width=8, font=("Segoe UI", 10))
        self.b_days.delete(0, "end")
        self.b_days.insert(0, "90")
        self.b_prefix = self._field(card, "Prefijo lote", self.settings.get("default_prefix", "BETA2026"))
        self.b_inst = self._field(card, "Institución", self.settings.get("default_institution", ""))

        self.b_result = tk.Label(card, text="", font=("Segoe UI", 10), fg=C["ok"], bg=C["card"], justify="left")
        self.b_result.pack(anchor="w", pady=8)

        tk.Button(card, text="Generar archivo CSV + inventario", command=self._gen_batch, bg=C["teal"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", pady=10, cursor="hand2").pack(fill="x", pady=8)

    def _tab_inventory(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Inventario  ")
        card = self._card(tab)

        sf = tk.Frame(card, bg=C["card"])
        sf.pack(fill="x", pady=(0, 6))
        self.inv_search = tk.Entry(sf, bg=C["bg"], fg=C["text"], relief="flat", font=("Segoe UI", 10))
        self.inv_search.pack(side="left", fill="x", expand=True, ipady=4)
        self.inv_search.bind("<KeyRelease>", lambda _: self._refresh_inventory_tree())

        self.inv_status = ttk.Combobox(sf, values=["todas", "available", "assigned", "revoked"], state="readonly", width=12)
        self.inv_status.set("todas")
        self.inv_status.pack(side="left", padx=6)
        self.inv_status.bind("<<ComboboxSelected>>", lambda _: self._refresh_inventory_tree())

        self.inv_batch = ttk.Combobox(sf, values=["todos"], state="readonly", width=16)
        self.inv_batch.set("todos")
        self.inv_batch.pack(side="left", padx=4)
        self.inv_batch.bind("<<ComboboxSelected>>", lambda _: self._refresh_inventory_tree())

        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", pady=4)
        self._btn(bf, "Marcar asignada", self._inv_mark_assigned)
        self._btn(bf, "Marcar disponible", self._inv_mark_available)
        self._btn(bf, "Revocar", self._inv_revoke)
        self._btn(bf, "Exportar filtro CSV", self._export_filtered_inv)
        self._btn(bf, "Importar CSV", self._import_csv)

        cols = ("status", "type", "name", "email", "batch", "key")
        self.inv_tree = ttk.Treeview(card, columns=cols, show="headings", height=16)
        for c, w in zip(cols, (90, 70, 140, 160, 100, 280)):
            self.inv_tree.heading(c, text=c.capitalize())
            self.inv_tree.column(c, width=w, minwidth=60)
        self.inv_tree.pack(fill="both", expand=True)
        self._refresh_inventory_tree()

    def _tab_validate(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Validar  ")
        card = self._card(tab)
        tk.Label(card, text="Pega una clave NSFT para inspeccionar su payload (offline).",
                 font=("Segoe UI", 10), fg=C["muted"], bg=C["card"]).pack(anchor="w", pady=(0, 6))
        self.v_key = tk.Entry(card, bg=C["bg"], fg=C["text"], font=("Consolas", 11), relief="flat")
        self.v_key.pack(fill="x", ipady=6)
        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", pady=8)
        self._btn(bf, "Decodificar", self._decode_key_ui, primary=True)
        self._btn(bf, "Desde selección inventario", self._decode_from_selection)
        self.v_result = tk.Label(card, text="", font=("Segoe UI", 10), fg=C["text"], bg=C["card"], justify="left")
        self.v_result.pack(anchor="w", fill="x")

    def _tab_customize(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Personalizar  ")
        card = self._card(tab)

        self.c_inst = self._field(card, "Institución default", self.settings.get("default_institution", ""))
        self.c_prefix = self._field(card, "Prefijo lote default", self.settings.get("default_prefix", "BETA2026"))
        self.c_sender = self._field(card, "Firma email", self.settings.get("default_sender", "Equipo NeuroSoft"))
        self.c_batch_sz = self._field(card, "Tamaño lote default", str(self.settings.get("default_batch_size", 50)))

        qf = tk.LabelFrame(card, text="Cuotas (máx. disponibles por tipo · 0 = sin límite)",
                           font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"])
        qf.pack(fill="x", pady=(8, 4))
        quotas = self.settings.get("quotas") or {}
        self.c_quota = {}
        for t in TYPE_META:
            row = tk.Frame(qf, bg=C["card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=TYPE_META[t]["label"], width=14, anchor="w",
                     font=("Segoe UI", 9), fg=C["muted"], bg=C["card"]).pack(side="left")
            e = tk.Entry(row, width=8, bg=C["bg"], fg=C["text"], relief="flat", font=("Segoe UI", 10))
            e.insert(0, str(quotas.get(t, 0)))
            e.pack(side="left", padx=4)
            self.c_quota[t] = e

        tk.Label(card, text="Plantilla email (placeholders: {name} {email} {key} {type_label} {institution} {days_line} {notes_line} {sender})",
                 font=("Segoe UI", 9), fg=C["muted"], bg=C["card"], wraplength=700, justify="left").pack(anchor="w", pady=(10, 4))
        self.c_template = scrolledtext.ScrolledText(card, height=14, bg=C["bg"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        self.c_template.pack(fill="both", expand=True)
        self.c_template.insert("1.0", self.settings.get("email_template") or DEFAULT_EMAIL_TEMPLATE)

        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", pady=8)
        self._btn(bf, "Guardar preferencias", self._save_customize, primary=True)
        self._btn(bf, "Restaurar plantilla", self._reset_template)

    def _tab_history(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Historial  ")
        card = self._card(tab)
        sf = tk.Frame(card, bg=C["card"])
        sf.pack(fill="x", pady=(0, 6))
        self.h_search = tk.Entry(sf, bg=C["bg"], fg=C["text"], relief="flat", font=("Segoe UI", 10))
        self.h_search.pack(side="left", fill="x", expand=True, ipady=4)
        self.h_search.bind("<KeyRelease>", lambda _: self._refresh_hist())
        self._btn(sf, "Exportar JSON", self._export_hist)
        self.hist = scrolledtext.ScrolledText(card, height=18, bg=C["bg"], fg=C["muted"], font=("Consolas", 9), relief="flat")
        self.hist.pack(fill="both", expand=True)
        self._refresh_hist()

    def _tab_email(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Email  ")
        card = self._card(tab)
        tk.Label(card, text="Plantilla del último registro seleccionado o generado", font=("Segoe UI", 10),
                 fg=C["muted"], bg=C["card"]).pack(anchor="w", pady=(0, 6))
        self.email_txt = scrolledtext.ScrolledText(card, height=16, bg=C["bg"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        self.email_txt.pack(fill="both", expand=True)
        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", pady=6)
        self._btn(bf, "Cargar última clave", self._load_last_email)
        self._btn(bf, "Desde selección inventario", self._email_from_selection)
        self._btn(bf, "Copiar", lambda: self._copy(self.email_txt.get("1.0", "end")))

    def _tab_help(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Ayuda  ")
        card = self._card(tab)
        txt = scrolledtext.ScrolledText(card, wrap="word", bg=C["bg"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", """FLUJO RECOMENDADO
─────────────────
1. Pestaña Lote CSV → genera N claves (quedan en Inventario como "available").
2. Panel superior muestra cuántas quedan disponibles.
3. Al entregar una clave al tester: selecciónala en Inventario → "Marcar asignada".
4. Email → copia plantilla personalizada y envía por WhatsApp/correo.

TIPOS DE LICENCIA
─────────────────
• perpetual — Cliente pagador, sin marca de agua.
• trial     — Demo N días, expira en la clave.
• beta      — Testers, marca de agua en PDF.
• master    — Tu PC de desarrollo. NO distribuir.

REBUILD / ACTUALIZACIONES
──────────────────────────
Recompilar NeuroSoft.exe NO invalida licencias ya activadas.
La licencia vive en %APPDATA%\\NeuroSoft\\license.dat (por equipo).

DATOS LOCALES (no subir a GitHub)
─────────────────────────────────
%%APPDATA%%\\NeuroSoft\\LicenseAdmin\\
  license_inventory.json
  license_history.json
  license_settings.json
""")
        txt.configure(state="disabled")

    # ── Actions ──────────────────────────────────────────────────

    def _toggle_days(self) -> None:
        if self.s_type.get() == "trial":
            self.s_days_frame.pack(fill="x", pady=4, after=self.s_type_desc)
        else:
            self.s_days_frame.pack_forget()
        self._update_preview()

    def _update_preview(self) -> None:
        t = self.s_type.get()
        meta = TYPE_META.get(t, TYPE_META["beta"])
        self.s_type_desc.config(text=meta["desc"])
        days = self.s_days.get() if t == "trial" else "—"
        st = inventory_stats()
        self.preview.config(text=(
            f"Tipo: {meta['label']}\n"
            f"Marca de agua PDF: {'Sí' if meta['watermark'] else 'No'}\n"
            f"Días trial: {days}\n\n"
            f"Inventario: {st['available']} disponibles / {st['total']} total\n\n"
            "Activación offline · sin internet."
        ))

    def _gen_single(self) -> None:
        name = self.s_name.get().strip()
        email = self.s_email.get().strip()
        if not name or not email:
            messagebox.showwarning("Datos incompletos", "Nombre y email son obligatorios.")
            return
        ltype = self.s_type.get()
        ok, msg = check_quota(ltype, count=1, settings=self.settings)
        if not ok:
            messagebox.showwarning("Cuota alcanzada", msg)
            return
        days = int(self.s_days.get()) if ltype == "trial" else 0
        inst = self.s_inst.get().strip() or self.settings.get("default_institution", "")
        key = generate_key(ltype, name, email, self.s_doc.get().strip(), days, inst)
        self.s_key.set(key)
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": ltype, "name": name, "email": email, "institution": inst,
            "days": days or None, "notes": self.s_notes.get().strip(), "key": key,
        }
        append_history(entry)
        status = "assigned" if self.s_auto_assign.get() else "available"
        inventory_register(entry, status=status)
        self._refresh_stats()
        self._refresh_dashboard()
        self._refresh_inventory_tree()
        self.email_txt.delete("1.0", "end")
        self.email_txt.insert("1.0", email_template(entry, self.settings))
        messagebox.showinfo("Listo", f"Clave generada · estado: {status}\nDisponibles: {inventory_stats()['available']}")

    def _clear_single(self) -> None:
        for w in (self.s_name, self.s_email, self.s_doc, self.s_inst, self.s_notes):
            w.delete(0, "end")
        self.s_key.set("—")

    def _gen_batch(self) -> None:
        n = int(self.b_count.get())
        ltype = self.b_type.get()
        ok, msg = check_quota(ltype, count=n, settings=self.settings)
        if not ok:
            messagebox.showwarning("Cuota alcanzada", msg)
            return
        days = int(self.b_days.get()) if ltype == "trial" else 0
        prefix = self.b_prefix.get().strip() or self.settings.get("default_prefix", "LOTE")
        inst = self.b_inst.get().strip() or self.settings.get("default_institution", "")
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile=f"{prefix}_licencias.csv",
        )
        if not path:
            return
        rows = []
        for i in range(1, n + 1):
            name = f"{prefix}-{i:04d}"
            email = f"{prefix.lower()}-{i:04d}@beta.neurosoft.local"
            key = generate_key(ltype, name, email, "", days, inst)
            rows.append({"idx": i, "status": "available", "type": ltype, "name": name, "email": email, "institution": inst, "batch": prefix, "key": key})
            entry = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": ltype, "name": name,
                     "email": email, "institution": inst, "days": days or None, "key": key, "batch": prefix}
            append_history({**entry, "batch": prefix})
            inventory_register(entry, status="available")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["idx", "status", "type", "name", "email", "institution", "batch", "key"])
            w.writeheader()
            w.writerows(rows)
        st = inventory_stats()
        self.b_result.config(text=f"✓ {n} claves → {path}\nDisponibles en inventario: {st['available']} / {st['total']}")
        self._refresh_stats()
        self._refresh_dashboard()
        self._refresh_inventory_tree()
        messagebox.showinfo("Lote generado", f"{n} claves registradas.\nDisponibles: {st['available']}")

    def _refresh_inventory_tree(self) -> None:
        if not hasattr(self, "inv_tree"):
            return
        batches = ["todos", *inventory_batches()]
        self.inv_batch["values"] = batches

        q = self.inv_search.get() if hasattr(self, "inv_search") else ""
        st_f = self.inv_status.get()
        status = None if st_f == "todas" else st_f
        batch = None if self.inv_batch.get() == "todos" else self.inv_batch.get()
        rows = inventory_filter(status=status, batch=batch, query=q)

        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for r in rows[:500]:
            self.inv_tree.insert("", "end", values=(
                r.get("status", ""), r.get("type", ""), r.get("name", ""),
                r.get("email", ""), r.get("batch", ""), r.get("key", ""),
            ))

    def _inv_selected_key(self) -> str | None:
        sel = self.inv_tree.selection()
        if not sel:
            return None
        vals = self.inv_tree.item(sel[0], "values")
        return vals[5] if len(vals) > 5 else None

    def _inv_mark_assigned(self) -> None:
        key = self._inv_selected_key()
        if not key:
            messagebox.showinfo("Selección", "Selecciona una fila del inventario.")
            return
        inventory_mark(key, "assigned")
        self._refresh_stats()
        self._refresh_inventory_tree()
        self._refresh_dashboard()

    def _inv_mark_available(self) -> None:
        key = self._inv_selected_key()
        if not key:
            messagebox.showinfo("Selección", "Selecciona una fila del inventario.")
            return
        inventory_mark(key, "available")
        self._refresh_stats()
        self._refresh_inventory_tree()

    def _inv_revoke(self) -> None:
        key = self._inv_selected_key()
        if not key:
            messagebox.showinfo("Selección", "Selecciona una fila del inventario.")
            return
        if not messagebox.askyesno("Revocar", f"¿Marcar como revocada?\n{key[:40]}…"):
            return
        inventory_revoke(key)
        self._refresh_stats()
        self._refresh_inventory_tree()
        self._refresh_dashboard()

    def _backup_inv(self) -> None:
        path = backup_inventory()
        messagebox.showinfo("Backup", f"Inventario respaldado en:\n{path}")

    def _decode_key_ui(self) -> None:
        key = self.v_key.get().strip()
        if not key:
            messagebox.showinfo("Clave", "Pega una clave NSFT.")
            return
        try:
            info = decode_key(key)
            self.v_result.config(text=(
                f"Tipo: {info['type_label']} ({info['type']})\n"
                f"Emitida: {info['issued_at']}\n"
                f"Marca de agua PDF: {'Sí' if info['watermark'] else 'No'}\n"
                f"Días trial: {info['trial_days'] or '—'}\n"
                f"Expira: {info['expires_at'] or 'Sin vencimiento en clave'}\n"
                f"Firma RSA: {'Sí' if info['signed'] else 'No (dev)'}"
            ), fg=C["text"])
        except ValueError as exc:
            self.v_result.config(text=f"Error: {exc}", fg=C["danger"])

    def _decode_from_selection(self) -> None:
        key = self._inv_selected_key()
        if not key:
            messagebox.showinfo("Selección", "Selecciona una fila del inventario.")
            return
        self.v_key.delete(0, "end")
        self.v_key.insert(0, key)
        self._decode_key_ui()

    def _import_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        new_n, total = import_csv_inventory(path)
        self._refresh_stats()
        self._refresh_dashboard()
        self._refresh_inventory_tree()
        messagebox.showinfo("Importado", f"{new_n} claves nuevas importadas ({total} filas en CSV).")

    def _export_all_inv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="inventario_licencias.csv")
        if path:
            n = export_inventory_csv(path)
            messagebox.showinfo("Exportado", f"{n} filas → {path}")

    def _export_filtered_inv(self) -> None:
        st_f = self.inv_status.get()
        status = None if st_f == "todas" else st_f
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"licencias_{st_f}.csv")
        if path:
            n = export_inventory_csv(path, status=status)
            messagebox.showinfo("Exportado", f"{n} filas → {path}")

    def _save_customize(self) -> None:
        self.settings = {
            "default_institution": self.c_inst.get().strip(),
            "default_prefix": self.c_prefix.get().strip(),
            "default_sender": self.c_sender.get().strip(),
            "default_batch_size": int(self.c_batch_sz.get() or 50),
            "email_template": self.c_template.get("1.0", "end").strip(),
            "quotas": {t: int(self.c_quota[t].get() or 0) for t in self.c_quota},
        }
        save_settings(self.settings)
        messagebox.showinfo("Guardado", "Preferencias guardadas.")

    def _reset_template(self) -> None:
        self.c_template.delete("1.0", "end")
        self.c_template.insert("1.0", DEFAULT_EMAIL_TEMPLATE)

    def _refresh_hist(self) -> None:
        q = (self.h_search.get() or "").lower()
        self.hist.delete("1.0", "end")
        for e in reversed(load_history()):
            line = f"{e.get('date','')} | {e.get('type',''):8s} | {e.get('name','')[:28]:28s} | {e.get('key','')}\n"
            if q and q not in line.lower():
                continue
            self.hist.insert("end", line)

    def _export_hist(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            import json
            with open(path, "w", encoding="utf-8") as f:
                json.dump(load_history(), f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exportado", path)

    def _load_last_email(self) -> None:
        hist = load_history()
        if not hist:
            messagebox.showinfo("Historial vacío", "Genera una clave primero.")
            return
        self.email_txt.delete("1.0", "end")
        self.email_txt.insert("1.0", email_template(hist[-1], self.settings))

    def _email_from_selection(self) -> None:
        key = self._inv_selected_key()
        if not key:
            messagebox.showinfo("Selección", "Selecciona una fila del inventario.")
            return
        row = next((k for k in inventory_filter() if k.get("key") == key), None)
        if not row:
            return
        self.email_txt.delete("1.0", "end")
        self.email_txt.insert("1.0", email_template(row, self.settings))

    def _copy(self, text: str) -> None:
        t = (text or "").strip()
        if t and t != "—":
            self.root.clipboard_clear()
            self.root.clipboard_append(t)
            messagebox.showinfo("Copiado", "Texto en portapapeles.")


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        sys.path.insert(0, sys._MEIPASS)  # type: ignore[attr-defined]
    LicenseAdminApp()
