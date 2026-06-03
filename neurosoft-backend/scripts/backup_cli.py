"""
S4.3: Script CLI para gestión de backups cifrados.

Uso:
    python -m scripts.backup_cli crear [--notas "..."]
    python -m scripts.backup_cli listar
    python -m scripts.backup_cli restaurar <ruta> [--target PATH]
    python -m scripts.backup_cli rotar [--diarios N] [--semanales M]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permitir ejecutar como `python scripts/backup_cli.py ...`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gestión de backups cifrados (S4.3)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_crear = sub.add_parser("crear", help="Crear un nuevo backup cifrado")
    p_crear.add_argument("--notas", default="", help="Notas opcionales")

    p_listar = sub.add_parser("listar", help="Listar backups disponibles")

    p_rest = sub.add_parser("restaurar", help="Restaurar un backup")
    p_rest.add_argument("ruta", help="Ruta al archivo .enc.gz")
    p_rest.add_argument("--target", help="Ruta destino (default: BD activa)")

    p_rotar = sub.add_parser("rotar", help="Eliminar backups viejos")
    p_rotar.add_argument("--diarios", type=int, default=7)
    p_rotar.add_argument("--semanales", type=int, default=4)

    args = parser.parse_args()

    from app.infrastructure.backup import (
        crear_backup,
        eliminar_backups_viejos,
        listar_backups,
        restaurar_backup,
    )

    if args.cmd == "crear":
        ruta = crear_backup(notas=args.notas or None)
        print(f"OK: backup creado en {ruta}")
        return 0

    if args.cmd == "listar":
        backups = listar_backups()
        if not backups:
            print("(sin backups)")
            return 0
        for b in backups:
            notas = f" — {b.notas}" if b.notas else ""
            ts = b.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            tam = b.tamano_bytes / 1024
            print(f"{ts}  {tam:8.1f} KB  {b.ruta.name}{notas}")
        return 0

    if args.cmd == "restaurar":
        target = restaurar_backup(args.ruta, target_path=args.target)
        print(f"OK: backup restaurado en {target}")
        return 0

    if args.cmd == "rotar":
        n = eliminar_backups_viejos(
            mantener_diarios=args.diarios,
            mantener_semanales=args.semanales,
        )
        print(f"OK: {n} backups eliminados")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
