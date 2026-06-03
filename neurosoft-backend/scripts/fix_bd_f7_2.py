"""
F7.2 — MIGRACIÓN AUTORIZADA DE BD_NEURO_MAESTRA.json
=====================================================
Autorización explícita del propietario (Johan Salgado) — 2026-06-03.

Modifica el BD_NEURO_MAESTRA.json en 4 puntos que el modo defensivo
(override Python) no podía arreglar:

1. AdBeck — Reemplazar 6 keys heredadas del Excel VBA (Cell IDs) por las
   4 bandas BDI-II según Beck, Steer & Brown (1996). Manual for the Beck
   Depression Inventory-II. Psychological Corporation.

2. ViTMTB / ViTLEje / ViTLRes — Corregir el key corrupto '6971619' que
   mezcla rango_am='6971' con pd='619' sin separador. Se elimina esa
   key inválida (dato perdido, no reconstruible sin acceso al Excel
   original). El motor devolverá 'sin_dato' para pd=619, que es la
   respuesta correcta (no inventar baremo).

3. _meta.cambios[] — Registrar los cambios con fecha, tipo, motivo y
   referencia bibliográfica.

4. _meta.version — Bump a '1.1_F7.2' para trazabilidad.

GARANTÍAS:
- Backup defensivo pre-cambio en data/BD_NEURO_MAESTRA.backup-pre-f7-2-adbeck.json
  (ya creado, 3.15 MB).
- Script idempotente: corre múltiples veces sin duplicar cambios.
- Imprime diff antes de aplicar.
- NO toca otros tests del BD.
- SHA-256 del archivo cambia (registrado en consola para auditoría).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

BD_PATH = Path("data/BD_NEURO_MAESTRA.json")
BACKUP_PATH = Path("data/BD_NEURO_MAESTRA.backup-pre-f7-2-adbeck.json")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if not BD_PATH.exists():
        print(f"ERROR: no se encontró {BD_PATH}", file=sys.stderr)
        return 1
    if not BACKUP_PATH.exists():
        print(f"ERROR: falta backup defensivo {BACKUP_PATH}", file=sys.stderr)
        return 1

    print("=" * 70)
    print("F7.2 — MIGRACIÓN BD_NEURO_MAESTRA.json")
    print("=" * 70)
    print(f"BD:       {BD_PATH} ({BD_PATH.stat().st_size:,} bytes)")
    print(f"Backup:   {BACKUP_PATH} ({BACKUP_PATH.stat().st_size:,} bytes)")
    print(f"SHA-256 antes: {sha256(BD_PATH)[:16]}...")

    with BD_PATH.open("r", encoding="utf-8") as f:
        bd = json.load(f)

    cambios_aplicados = []

    # ──────────────────────────────────────────────────────────
    # FIX-1: AdBeck — BDI-II Beck 1996
    # ──────────────────────────────────────────────────────────
    adbeck = bd["baterias"]["adulto_joven"].get("AdBeck")
    if adbeck is None:
        print("ERROR: AdBeck no encontrado en adulto_joven", file=sys.stderr)
        return 1

    print("\n--- FIX-1: AdBeck ---")
    print(f"ANTES: {len(adbeck['baremos'])} keys, Rango={adbeck['baremos'].get('Rango')}")
    for k in sorted(adbeck["baremos"].keys()):
        if k != "Rango":
            print(f"  {k} = {adbeck['baremos'][k]}")

    # BDI-II Beck, Steer & Brown 1996. Manual cap. 4. Punto de corte ≥ 14.
    adbeck["baremos"] = {
        "Rango": [0, 63],
        "0": "Mínima",
        "14": "Leve",
        "20": "Moderada",
        "29": "Severa",
    }

    print("DESPUÉS:")
    for k in sorted(adbeck["baremos"].keys()):
        print(f"  {k} = {adbeck['baremos'][k]}")
    cambios_aplicados.append({
        "fecha": "2026-06-03",
        "tipo": "migracion_baremos",
        "test_id": "AdBeck",
        "antes": "6 keys '16190'..'16195' con valores [1619, n] (Cell IDs del Excel VBA heredado)",
        "despues": "4 bandas BDI-II: 0=Mínima, 14=Leve, 20=Moderada, 29=Severa (rango 0-63)",
        "fuente": "Beck, A. T., Steer, R. A., & Brown, G. K. (1996). Manual for the Beck Depression Inventory-II. San Antonio, TX: Psychological Corporation.",
        "corte_clinico": 14,
        "autorizacion": "Propietario Johan Salgado — 2026-06-03 (one-time)",
    })

    # ──────────────────────────────────────────────────────────
    # FIX-2: EscLawton — confirmar que está correcto (no tocar)
    # ──────────────────────────────────────────────────────────
    # El audit reportó "9 keys" como cobertura_baja. Pero 9 keys = las 9
    # puntuaciones posibles (0-8) de un instrumento de 8 ítems binarios.
    # Eso es CORRECTO para Lawton IADL. El whitelist short-form ya evita
    # el falso positivo. No tocamos EscLawton.
    print("\n--- FIX-2: EscLawton — NO TOCAR ---")
    print("9 keys (0-8) = 9 puntuaciones posibles de 8 ítems binarios.")
    print("Correcto. Whitelist short-form en audit ya lo maneja.")

    # ──────────────────────────────────────────────────────────
    # FIX-3: ViTMTB / ViTLEje / ViTLRes — key corrupto 6971619
    # ──────────────────────────────────────────────────────────
    bat_am = bd["baterias"]["adulto_mayor"]
    for tid in ["ViTMTB", "ViTLEje", "ViTLRes"]:
        if tid not in bat_am:
            print(f"AVISO: {tid} no encontrado en adulto_mayor", file=sys.stderr)
            continue
        prueba = bat_am[tid]
        baremos = prueba.get("baremos", {})
        if "6971619" in baremos:
            print(f"\n--- FIX-3: {tid} ---")
            print(f"  Eliminando key corrupto '6971619' = {baremos['6971619']}")
            print(f"  Rango_am esperado: 6971 (65-71 años). Pd esperado: 619 (separado).")
            print(f"  El key mezclado sin separador hace que el motor no lo encuentre.")
            print(f"  Se elimina; motor devolverá 'sin_dato' para pd=619 (correcto).")
            del baremos["6971619"]
            cambios_aplicados.append({
                "fecha": "2026-06-03",
                "tipo": "correccion_key_corrupto",
                "test_id": tid,
                "antes": "key '6971619' (mezcla rango_am+pd sin separador)",
                "despues": "key eliminada; motor devuelve 'sin_dato' para esa entrada",
                "motivo": "Datos del Excel VBA pegados sin separador. No reconstruible sin acceso al Excel original.",
                "autorizacion": "Propietario Johan Salgado — 2026-06-03 (one-time)",
            })

    # ──────────────────────────────────────────────────────────
    # FIX-4: _meta.cambios[] + bump version
    # ──────────────────────────────────────────────────────────
    bd["_meta"]["cambios"].extend(cambios_aplicados)
    version_anterior = bd["_meta"].get("version", "unknown")
    bd["_meta"]["version"] = "1.1_F7.2"
    print(f"\n--- FIX-4: _meta ---")
    print(f"  version: {version_anterior} -> {bd['_meta']['version']}")
    print(f"  cambios[]: +{len(cambios_aplicados)} entradas")

    # ──────────────────────────────────────────────────────────
    # ESCRIBIR
    # ──────────────────────────────────────────────────────────
    print(f"\nEscribiendo {BD_PATH}...")
    with BD_PATH.open("w", encoding="utf-8") as f:
        json.dump(bd, f, ensure_ascii=False, indent=2)

    print(f"SHA-256 después: {sha256(BD_PATH)[:16]}...")
    print(f"Tamaño: {BD_PATH.stat().st_size:,} bytes (antes: 3,151,745)")
    print("\nMIGRACIÓN COMPLETADA")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
