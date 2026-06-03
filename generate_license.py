"""
generate_license.py
===================
§BLINDAJE-N1 — GUI para generar licencias de NeuroSoft.

Solo la usa Johan. Sin dependencias externas (solo tkinter, built-in).
Genera claves NSFT-XXXX-XXXX-XXXX-XXXX válidas.

Tipos de licencia soportados:
  - Perpetua: pago único, sin expiración
  - Trial: N días, expira automáticamente
  - Beta tester: sin expiración, con marca de agua
  - Master Admin: solo Johan, acceso total

Ejecutar: python generate_license.py
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import messagebox, ttk

# ═══════════════════════════════════════════════════════════════
# LÓGICA DE GENERACIÓN DE CLAVES
# ═══════════════════════════════════════════════════════════════

_PRODUCT_ID = "NSFT"


def _generate_key(license_type: str, licensee: str, email: str, doc: str, days: int = 0) -> str:
    """
    Genera una clave de licencia en formato NSFT-XXXX-XXXX-XXXX-XXXX.

    Cada bloque XXXX es hexadecimal. La clave contiene:
    - Versión del formato (1 byte)
    - Tipo de licencia (1 byte: 0=perpetual, 1=trial, 2=beta, 3=master)
    - Timestamp de emisión (4 bytes)
    - Días de duración (2 bytes, 0 = perpetua)
    - Hash de identidad (8 bytes)
    - Relleno aleatorio hasta 32 bytes
    """
    type_map = {"perpetual": 0, "trial": 1, "beta": 2, "master": 3}
    version = 1
    ltype = type_map.get(license_type, 0)
    now = int(datetime.now(timezone.utc).timestamp())

    # Construir payload binario (32 bytes)
    identity = f"{licensee}|{email}|{doc}".encode("utf-8")
    id_hash = hashlib.sha256(identity).digest()[:8]

    payload = bytearray(32)
    payload[0] = version
    payload[1] = ltype
    payload[2:6] = now.to_bytes(4, "big")
    payload[6:8] = days.to_bytes(2, "big")
    payload[8:16] = id_hash
    payload[16:] = secrets.token_bytes(16)

    # Formatear como NSFT-XXXX-XXXX-XXXX-XXXX
    hex_str = payload.hex().upper()
    blocks = [hex_str[i:i+4] for i in range(0, 32, 4)]
    return f"{_PRODUCT_ID}-{'-'.join(blocks[:8])}"


# ═══════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════

class LicenseGeneratorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeuroSoft — Generador de Licencias")
        self.root.geometry("550x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a1929")

        # ── Header ──
        header = tk.Frame(self.root, bg="#0a1929", height=80)
        header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(header, text="NeuroSoft", font=("Segoe UI", 20, "bold"),
                 fg="#0D9488", bg="#0a1929").pack(side="left")
        tk.Label(header, text="Generador de Licencias",
                 font=("Segoe UI", 12), fg="#94a3b8", bg="#0a1929").pack(side="left", padx=10)

        # ── Card principal ──
        card = tk.Frame(self.root, bg="#112240", highlightbackground="#1e3a5f",
                        highlightthickness=1, padx=24, pady=24)
        card.pack(fill="x", padx=20, pady=10)

        # Tipo de licencia
        tk.Label(card, text="Tipo de licencia", font=("Segoe UI", 10, "bold"),
                 fg="#94a3b8", bg="#112240").pack(anchor="w")
        self.license_type = ttk.Combobox(card, values=[
            "Perpetua (pago único, sin expiración)",
            "Trial (prueba por N días)",
            "Beta tester",
            "Master Admin (solo Johan)",
        ], state="readonly", font=("Segoe UI", 10))
        self.license_type.pack(fill="x", pady=(4, 12))
        self.license_type.current(0)

        # Días (solo trial)
        self.trial_frame = tk.Frame(card, bg="#112240")
        self.trial_frame.pack(fill="x")
        tk.Label(self.trial_frame, text="Días de prueba",
                 font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#112240").pack(anchor="w")
        self.trial_days = ttk.Spinbox(self.trial_frame, from_=1, to=365, font=("Segoe UI", 10))
        self.trial_days.pack(fill="x", pady=(4, 12))
        self.trial_days.set(14)
        self.trial_frame.pack_forget()  # Oculto por defecto

        # Datos del licenciatario
        tk.Label(card, text="Nombre del profesional", font=("Segoe UI", 10, "bold"),
                 fg="#94a3b8", bg="#112240").pack(anchor="w")
        self.name_entry = tk.Entry(card, font=("Segoe UI", 10),
                                   bg="#1a2b4a", fg="#e2e8f0", insertbackground="#e2e8f0",
                                   relief="flat")
        self.name_entry.pack(fill="x", pady=(4, 12))

        tk.Label(card, text="Email", font=("Segoe UI", 10, "bold"),
                 fg="#94a3b8", bg="#112240").pack(anchor="w")
        self.email_entry = tk.Entry(card, font=("Segoe UI", 10),
                                    bg="#1a2b4a", fg="#e2e8f0", insertbackground="#e2e8f0",
                                    relief="flat")
        self.email_entry.pack(fill="x", pady=(4, 12))

        tk.Label(card, text="Documento (opcional)", font=("Segoe UI", 10, "bold"),
                 fg="#94a3b8", bg="#112240").pack(anchor="w")
        self.doc_entry = tk.Entry(card, font=("Segoe UI", 10),
                                  bg="#1a2b4a", fg="#e2e8f0", insertbackground="#e2e8f0",
                                  relief="flat")
        self.doc_entry.pack(fill="x", pady=(4, 12))

        # Botón generar
        self.gen_btn = tk.Button(card, text="GENERAR LICENCIA", font=("Segoe UI", 12, "bold"),
                                 bg="#0D9488", fg="white", activebackground="#0f766e",
                                 relief="flat", cursor="hand2",
                                 command=self.generate)
        self.gen_btn.pack(fill="x", pady=(8, 0))

        # ── Resultado ──
        result_card = tk.Frame(self.root, bg="#112240", highlightbackground="#1e3a5f",
                               highlightthickness=1, padx=24, pady=24)
        result_card.pack(fill="x", padx=20, pady=10)

        tk.Label(result_card, text="Clave generada", font=("Segoe UI", 10, "bold"),
                 fg="#94a3b8", bg="#112240").pack(anchor="w")
        self.key_var = tk.StringVar(value="NSFT-XXXX-XXXX-XXXX-XXXX")
        self.key_label = tk.Entry(result_card, textvariable=self.key_var,
                                  font=("Consolas", 16, "bold"), justify="center",
                                  bg="#1a2b4a", fg="#0D9488", relief="flat",
                                  readonlybackground="#1a2b4a", state="readonly")
        self.key_label.pack(fill="x", pady=(4, 8))

        btn_frame = tk.Frame(result_card, bg="#112240")
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="📋 Copiar", font=("Segoe UI", 9),
                  bg="#1e3a5f", fg="#e2e8f0", relief="flat", cursor="hand2",
                  command=self.copy_key).pack(side="left", padx=(0, 5))

        # ── Historial ──
        hist_card = tk.Frame(self.root, bg="#112240", highlightbackground="#1e3a5f",
                             highlightthickness=1, padx=24, pady=24)
        hist_card.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(hist_card, text="Historial de licencias generadas",
                 font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#112240").pack(anchor="w")

        self.history_text = tk.Text(hist_card, font=("Consolas", 9), height=10,
                                    bg="#1a2b4a", fg="#94a3b8", relief="flat",
                                    state="disabled")
        self.history_text.pack(fill="both", expand=True, pady=(4, 0))

        # ── Bindings ──
        self.license_type.bind("<<ComboboxSelected>>", self._on_type_change)

        # Cargar historial
        self.history = []
        self._load_history()

        self.root.mainloop()

    def _on_type_change(self, event=None):
        sel = self.license_type.get()
        if "Trial" in sel:
            self.trial_frame.pack(fill="x", after=self.license_type)
        else:
            self.trial_frame.pack_forget()

    def generate(self):
        sel = self.license_type.get()
        if "Perpetua" in sel:
            ltype = "perpetual"
            days = 0
        elif "Trial" in sel:
            ltype = "trial"
            days = int(self.trial_days.get())
        elif "Beta" in sel:
            ltype = "beta"
            days = 0
        else:
            ltype = "master"
            days = 0

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        doc = self.doc_entry.get().strip()

        if not name:
            messagebox.showwarning("Falta información", "Ingrese el nombre del profesional.")
            return
        if not email:
            messagebox.showwarning("Falta información", "Ingrese el email del profesional.")
            return

        key = _generate_key(ltype, name, email, doc, days)
        self.key_var.set(key)

        # Registrar en historial
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": ltype,
            "name": name,
            "email": email,
            "days": days if ltype == "trial" else None,
            "key": key,
        }
        self.history.append(entry)
        self._save_history()
        self._refresh_history()

    def copy_key(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.key_var.get())
        messagebox.showinfo("Copiado", "Clave copiada al portapapeles.")

    def _save_history(self):
        path = os.path.join(os.path.dirname(__file__), "license_history.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.history[-50:], f, indent=2, ensure_ascii=False)

    def _load_history(self):
        path = os.path.join(os.path.dirname(__file__), "license_history.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            self._refresh_history()

    def _refresh_history(self):
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", tk.END)
        for entry in reversed(self.history[-20:]):
            tipo = {"perpetual": "PERP", "trial": "TRIAL", "beta": "BETA", "master": "MASTER"}.get(entry["type"], entry["type"])
            days_info = f" {entry['days']}d" if entry.get("days") else ""
            line = f"[{entry['date']}] {tipo:6s} | {entry['name'][:25]:25s} | {entry['key'][:20]}...{days_info}\n"
            self.history_text.insert(tk.END, line)
        self.history_text.configure(state="disabled")


if __name__ == "__main__":
    LicenseGeneratorApp()
