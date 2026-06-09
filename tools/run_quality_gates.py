#!/usr/bin/env python3
"""Runner unificado de quality gates para Inspector General y CI."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITS_DIR = ROOT / "docs" / "audits"


def run_step(name: str, cmd: list[str], cwd: Path | None = None) -> dict:
    result = {
        "name": name,
        "command": " ".join(cmd),
        "cwd": str(cwd or ROOT),
        "ok": False,
        "returncode": None,
        "stdout_tail": "",
        "stderr_tail": "",
    }
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        result["returncode"] = proc.returncode
        result["ok"] = proc.returncode == 0
        result["stdout_tail"] = proc.stdout[-4000:] if proc.stdout else ""
        result["stderr_tail"] = proc.stderr[-4000:] if proc.stderr else ""
    except Exception as exc:  # noqa: BLE001 — report gate runner failures
        result["stderr_tail"] = str(exc)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="NeuroSoft quality gates runner")
    parser.add_argument(
        "--output",
        type=Path,
        help="JSON output path (default: docs/audits/gates_<fecha>.json)",
    )
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--skip-lint", action="store_true")
    parser.add_argument("--skip-build", action="store_true", default=True)
    parser.add_argument("--with-build", dest="skip_build", action="store_false")
    parser.add_argument(
        "--strict-api",
        action="store_true",
        help="api_manifest_check fails on baseline issues too",
    )
    args = parser.parse_args()

    today = date.today().isoformat()
    out_path = args.output or (AUDITS_DIR / f"gates_{today}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    steps: list[dict] = []

    if not args.skip_pytest:
        steps.append(
            run_step(
                "pytest",
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-q",
                    "--tb=no",
                ],
                cwd=ROOT / "neurosoft-backend",
            )
        )

    if not args.skip_lint:
        npm = "npm.cmd" if sys.platform == "win32" else "npm"
        steps.append(
            run_step(
                "eslint",
                [npm, "run", "lint"],
                cwd=ROOT / "neurosoft-frontend",
            )
        )

    steps.append(
        run_step(
            "v2_guards",
            [sys.executable, "tools/check_v2_guards.py"],
        )
    )

    api_cmd = [sys.executable, "tools/api_manifest_check.py", "--no-fail-new"]
    if args.strict_api:
        api_cmd = [sys.executable, "tools/api_manifest_check.py", "--strict"]
    api_json = AUDITS_DIR / f"api_manifest_{today}.json"
    api_cmd.extend(["--json", str(api_json)])
    steps.append(run_step("api_manifest", api_cmd))

    if not args.skip_build:
        npm = "npm.cmd" if sys.platform == "win32" else "npm"
        steps.append(
            run_step(
                "frontend_build",
                [npm, "run", "build"],
                cwd=ROOT / "neurosoft-frontend",
            )
        )

    report = {
        "date": today,
        "root": str(ROOT),
        "all_ok": all(s["ok"] for s in steps),
        "steps": steps,
        "api_manifest_json": str(api_json) if api_json.exists() else None,
    }

    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Quality gates report: {out_path}")
    for step in steps:
        status = "OK" if step["ok"] else "FAIL"
        print(f"  [{status}] {step['name']}")
        if not step["ok"]:
            tail = step["stderr_tail"] or step["stdout_tail"]
            if tail:
                for line in tail.strip().splitlines()[-5:]:
                    print(f"        {line}")

    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
