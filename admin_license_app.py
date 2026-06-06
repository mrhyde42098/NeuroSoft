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

from tools.license_core import (
    TYPE_META,
    append_history,
    email_template,
    generate_key,
    load_history,
    save_history_entries,
)

# ── Tema visual ───────────────────────────────────────────────
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
}


def _style_ttk(root: tk.Tk) -> None:
    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except tk.TclError:
        pass
    s.configure("TNotebook", background=C["bg"], borderwidth=0)
    s.configure("TNotebook.Tab", background=C["card"], foreground=C["muted"], padding=[14, 8], font=("Segoe UI", 10))
    s.map("TNotebook.Tab", background=[("selected", C["teal_dim"])], foreground=[("selected", "white")])
    s.configure("TCombobox", fieldbackground=C["bg"], background=C["card"], foreground=C["text"])


class LicenseAdminApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("NeuroSoft License Admin")
        self.root.geometry("900x720")
        self.root.minsize(820, 640)
        self.root.configure(bg=C["bg"])
        _style_ttk(self.root)

        self._header()
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self._tab_single(nb)
        self._tab_batch(nb)
        self._tab_history(nb)
        self._tab_email(nb)
        self._tab_help(nb)
        self._update_preview()
        self.root.mainloop()

    def _header(self) -> None:
        h = tk.Frame(self.root, bg=C["bg"], pady=14)
        h.pack(fill="x", padx=20)
        tk.Label(h, text="⬡ NeuroSoft", font=("Segoe UI", 24, "bold"), fg=C["teal"], bg=C["bg"]).pack(side="left")
        tk.Label(h, text="License Admin", font=("Segoe UI", 12), fg=C["muted"], bg=C["bg"]).pack(side="left", padx=(12, 0))
        tk.Label(h, text="Uso exclusivo del titular · offline", font=("Segoe UI", 9), fg=C["muted"], bg=C["bg"]).pack(side="right")

    def _card(self, parent: tk.Widget) -> tk.Frame:
        f = tk.Frame(parent, bg=C["card"], highlightbackground=C["border"], highlightthickness=1, padx=22, pady=18)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        return f

    def _field(self, parent: tk.Frame, label: str, default: str = "") -> tk.Entry:
        row = tk.Frame(parent, bg=C["card"])
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label, width=20, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        e = tk.Entry(row, bg=C["bg"], fg=C["text"], insertbackground=C["text"], relief="flat", font=("Segoe UI", 10))
        e.pack(side="left", fill="x", expand=True, ipady=6, padx=(4, 0))
        if default:
            e.insert(0, default)
        return e

    def _btn(self, parent, text, cmd, primary=False) -> tk.Button:
        bg = C["teal"] if primary else C["border"]
        fg = "white" if primary else C["text"]
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=C["teal_dim"],
                      font=("Segoe UI", 10, "bold" if primary else "normal"), relief="flat", padx=14, pady=8, cursor="hand2")
        b.pack(side="left", padx=(0, 8))
        return b

    def _tab_single(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Licencia  ")
        outer = tk.Frame(tab, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        left = self._card(outer)
        left.pack(side="left", fill="both", expand=True)
        right = self._card(outer)
        right.pack(side="right", fill="y", padx=(0, 6))

        self.s_type = ttk.Combobox(left, values=list(TYPE_META.keys()), state="readonly", width=36, font=("Segoe UI", 10))
        self.s_type.set("beta")
        self.s_type.bind("<<ComboboxSelected>>", lambda _: (self._toggle_days(), self._update_preview()))
        row = tk.Frame(left, bg=C["card"])
        row.pack(fill="x", pady=5)
        tk.Label(row, text="Tipo", width=20, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.s_type.pack(in_=row, side="left", fill="x", expand=True)

        self.s_type_desc = tk.Label(left, text="", font=("Segoe UI", 9), fg=C["accent"], bg=C["card"], wraplength=420, justify="left")
        self.s_type_desc.pack(anchor="w", pady=(0, 8))

        self.s_days_frame = tk.Frame(left, bg=C["card"])
        self.s_days = tk.Spinbox(self.s_days_frame, from_=1, to=730, width=8, font=("Segoe UI", 10))
        self.s_days.delete(0, "end")
        self.s_days.insert(0, "14")
        row_d = tk.Frame(self.s_days_frame, bg=C["card"])
        row_d.pack(fill="x")
        tk.Label(row_d, text="Días (trial)", width=20, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.s_days.pack(in_=row_d, side="left")

        self.s_name = self._field(left, "Profesional")
        self.s_email = self._field(left, "Email")
        self.s_doc = self._field(left, "Documento")
        self.s_inst = self._field(left, "Institución / clínica")
        self.s_notes = self._field(left, "Notas internas")

        self.s_key = tk.StringVar(value="—")
        tk.Label(left, text="Clave NSFT", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(anchor="w", pady=(10, 4))
        tk.Entry(left, textvariable=self.s_key, font=("Consolas", 13, "bold"), justify="center",
                 bg=C["bg"], fg=C["teal"], relief="flat", state="readonly").pack(fill="x", ipady=10)

        bf = tk.Frame(left, bg=C["card"])
        bf.pack(fill="x", pady=12)
        self._btn(bf, "Generar clave", self._gen_single, primary=True)
        self._btn(bf, "Copiar", lambda: self._copy(self.s_key.get()))
        self._btn(bf, "Limpiar", self._clear_single)

        tk.Label(right, text="Vista previa", font=("Segoe UI", 11, "bold"), fg=C["text"], bg=C["card"]).pack(anchor="w")
        self.preview = tk.Label(right, text="", font=("Segoe UI", 9), fg=C["muted"], bg=C["card"],
                                justify="left", wraplength=260, width=32)
        self.preview.pack(anchor="w", pady=8)
        self._toggle_days()

    def _tab_batch(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Lote CSV  ")
        card = self._card(tab)
        self.b_count = tk.Spinbox(card, from_=1, to=10000, width=10, font=("Segoe UI", 10))
        self.b_count.delete(0, "end")
        self.b_count.insert(0, "50")
        row = tk.Frame(card, bg=C["card"])
        row.pack(fill="x", pady=5)
        tk.Label(row, text="Cantidad", width=20, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.b_count.pack(in_=row, side="left")

        self.b_type = ttk.Combobox(card, values=list(TYPE_META.keys()), state="readonly", width=36)
        self.b_type.set("beta")
        row2 = tk.Frame(card, bg=C["card"])
        row2.pack(fill="x", pady=5)
        tk.Label(row2, text="Tipo", width=20, anchor="w", font=("Segoe UI", 9, "bold"), fg=C["muted"], bg=C["card"]).pack(side="left")
        self.b_type.pack(in_=row2, side="left", fill="x", expand=True)

        self.b_days = tk.Spinbox(card, from_=1, to=365, width=8, font=("Segoe UI", 10))
        self.b_days.delete(0, "end")
        self.b_days.insert(0, "90")
        self.b_prefix = self._field(card, "Prefijo lote", "BETA2026")
        self.b_inst = self._field(card, "Institución (opcional)")

        tk.Button(card, text="Generar archivo CSV…", command=self._gen_batch, bg=C["teal"], fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", pady=12, cursor="hand2").pack(fill="x", pady=16)

    def _tab_history(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Historial  ")
        card = self._card(tab)
        sf = tk.Frame(card, bg=C["card"])
        sf.pack(fill="x", pady=(0, 8))
        self.h_search = tk.Entry(sf, bg=C["bg"], fg=C["text"], relief="flat", font=("Segoe UI", 10))
        self.h_search.pack(side="left", fill="x", expand=True, ipady=5)
        self.h_search.bind("<KeyRelease>", lambda _: self._refresh_hist())
        self._btn(sf, "Exportar JSON", self._export_hist)
        self.hist = scrolledtext.ScrolledText(card, height=20, bg=C["bg"], fg=C["muted"], font=("Consolas", 9), relief="flat")
        self.hist.pack(fill="both", expand=True)
        self._refresh_hist()

    def _tab_email(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Email  ")
        card = self._card(tab)
        tk.Label(card, text="Plantilla para enviar al beta tester (última clave generada)", font=("Segoe UI", 10),
                 fg=C["muted"], bg=C["card"]).pack(anchor="w", pady=(0, 8))
        self.email_txt = scrolledtext.ScrolledText(card, height=18, bg=C["bg"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        self.email_txt.pack(fill="both", expand=True)
        bf = tk.Frame(card, bg=C["card"])
        bf.pack(fill="x", pady=8)
        self._btn(bf, "Cargar última clave", self._load_last_email)
        self._btn(bf, "Copiar texto", lambda: self._copy(self.email_txt.get("1.0", "end")))

    def _tab_help(self, nb: ttk.Notebook) -> None:
        tab = tk.Frame(nb, bg=C["bg"])
        nb.add(tab, text="  Ayuda  ")
        card = self._card(tab)
        txt = scrolledtext.ScrolledText(card, wrap="word", bg=C["bg"], fg=C["text"], font=("Segoe UI", 10), relief="flat")
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", """FLUJO RECOMENDADO
─────────────────
1. Genera clave (individual o lote CSV).
2. Envía NeuroSoft-Setup.exe por Drive/USB y la clave por WhatsApp/correo aparte.
3. El tester activa la clave una vez; queda ligada al equipo.

TIPOS DE LICENCIA
─────────────────
• perpetual — Cliente pagador, sin marca de agua.
• trial     — Demo N días, expira en la clave.
• beta      — Testers, marca de agua en PDF.
• master    — Tu PC de desarrollo. NO distribuir.

PERSONALIZACIÓN
────────────────
El nombre de institución queda en historial y plantilla de email.
La clínica configura logo y nombre en Configuración → Institución dentro de la app.

SEGURIDAD
─────────
Historial en %%APPDATA%%\\NeuroSoft\\LicenseAdmin\\
No subir license_history.json a git.

BUILD PROTEGIDO (opcional)
──────────────────────────
python neurosoft-backend/build_protected.py
""")
        txt.configure(state="disabled")

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
        wm = "Sí" if meta["watermark"] else "No"
        days = self.s_days.get() if t == "trial" else "—"
        self.preview.config(text=(
            f"Tipo: {meta['label']}\n"
            f"Marca de agua PDF: {wm}\n"
            f"Días trial: {days}\n\n"
            f"La clave se activa offline.\n"
            f"No requiere internet."
        ))

    def _gen_single(self) -> None:
        name = self.s_name.get().strip()
        email = self.s_email.get().strip()
        if not name or not email:
            messagebox.showwarning("Datos incompletos", "Nombre y email son obligatorios.")
            return
        ltype = self.s_type.get()
        days = int(self.s_days.get()) if ltype == "trial" else 0
        inst = self.s_inst.get().strip()
        key = generate_key(ltype, name, email, self.s_doc.get().strip(), days, inst)
        self.s_key.set(key)
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": ltype, "name": name, "email": email, "institution": inst,
            "days": days or None, "notes": self.s_notes.get().strip(), "key": key,
        }
        append_history(entry)
        self._refresh_hist()
        self.email_txt.delete("1.0", "end")
        self.email_txt.insert("1.0", email_template(entry))
        messagebox.showinfo("Listo", "Clave generada y guardada en historial.")

    def _clear_single(self) -> None:
        for w in (self.s_name, self.s_email, self.s_doc, self.s_inst, self.s_notes):
            w.delete(0, "end")
        self.s_key.set("—")

    def _gen_batch(self) -> None:
        n = int(self.b_count.get())
        ltype = self.b_type.get()
        days = int(self.b_days.get()) if ltype == "trial" else 0
        prefix = self.b_prefix.get().strip() or "LOTE"
        inst = self.b_inst.get().strip()
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                            initialfile=f"{prefix}_licencias.csv")
        if not path:
            return
        rows = []
        for i in range(1, n + 1):
            name = f"{prefix}-{i:04d}"
            email = f"{prefix.lower()}-{i:04d}@beta.neurosoft.local"
            key = generate_key(ltype, name, email, "", days, inst)
            rows.append({"idx": i, "type": ltype, "name": name, "email": email, "institution": inst, "key": key})
            append_history({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": ltype, "name": name,
                            "email": email, "institution": inst, "days": days or None, "key": key, "batch": prefix})
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["idx", "type", "name", "email", "institution", "key"])
            w.writeheader()
            w.writerows(rows)
        messagebox.showinfo("Lote generado", f"{n} claves →\n{path}")
        self._refresh_hist()

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
        self.email_txt.insert("1.0", email_template(hist[-1]))

    def _copy(self, text: str) -> None:
        t = (text or "").strip()
        if t and t != "—":
            self.root.clipboard_clear()
            self.root.clipboard_append(t)
            messagebox.showinfo("Copiado", "Texto en portapapeles.")


if __name__ == "__main__":
    # PyInstaller onefile: asegurar import path
    if getattr(sys, "frozen", False):
        sys.path.insert(0, sys._MEIPASS)  # type: ignore[attr-defined]
    LicenseAdminApp()
