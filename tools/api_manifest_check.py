#!/usr/bin/env python3
"""Verifica alineación frontend↔backend: métodos HTTP y rutas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE_SRC = ROOT / "neurosoft-frontend" / "src"
BE_API = ROOT / "neurosoft-backend" / "app" / "presentation" / "api" / "v1"
BASELINE_PATH = Path(__file__).resolve().parent / "api_manifest_baseline.json"
API_PREFIX = "/api/v1"

ROUTER_PREFIX_RE = re.compile(
    r"(\w+)\s*=\s*APIRouter\(\s*prefix\s*=\s*[\"']([^\"']+)[\"']"
)
ROUTE_DECORATOR_RE = re.compile(
    r"@(\w+)\.(get|post|put|patch|delete)\(\s*[\"']([^\"']*)[\"']",
    re.IGNORECASE,
)
FE_API_CALL_RE = re.compile(
    r"api\.(get|post|patch|put|del|blob)\(\s*[`'\"](/api/v1[^`'\"]+)[`'\"]"
    r"(?:\s*,\s*[`'\"](GET|POST|PUT|PATCH|DELETE)[`'\"])?",
    re.IGNORECASE,
)
FE_API_TEMPLATE_RE = re.compile(
    r"api\.(get|post|patch|put|del|blob)\(\s*`(/api/v1[^`]+)`(?:\s*,\s*[\"'](GET|POST|PUT|PATCH|DELETE)[\"'])?",
    re.IGNORECASE,
)
FE_API_CONCAT_RE = re.compile(
    r"api\.(get|post|patch|put|del)\(\s*[\"'](/api/v1/[^\"']+)[\"']\s*\+",
    re.IGNORECASE,
)
FE_ABRIR_PDF_RE = re.compile(
    r"abrirPdf\(\s*`(/api/v1[^`]+)`",
    re.IGNORECASE,
)
FE_FETCH_RE = re.compile(
    r"fetch\(\s*[`'\"]([^`'\"]*?/api/v1[^`'\"]+)[`'\"][^)]*method:\s*[`'\"](\w+)[`'\"]",
    re.IGNORECASE,
)
FE_FETCH_API_TEMPLATE_RE = re.compile(
    r"fetch\(\s*`\$\{API\}(/api/v1[^`]+)`[^)]*method:\s*[`'\"](\w+)[`'\"]",
    re.IGNORECASE,
)
FE_TEMPLATE_SEGMENT_RE = re.compile(r"\$\{[^}]+\}")


@dataclass
class BackendRoute:
    method: str
    path: str
    file: str


@dataclass
class FrontendCall:
    method: str
    path: str
    file: str
    line: int


@dataclass
class Issue:
    kind: str
    path: str
    frontend_method: str | None
    backend_method: str | None
    file: str
    line: int | None = None
    in_baseline: bool = False


def normalize_path(path: str) -> str:
    p = path.split("?")[0].strip()
    p = re.sub(r"\$\{API\}", "", p)
    if not p.startswith("/"):
        p = "/" + p
    p = FE_TEMPLATE_SEGMENT_RE.sub("{param}", p)
    p = re.sub(r"/\d+", "/{param}", p)
    p = re.sub(r"\{[a-zA-Z_][^}]*\}", "{param}", p)
    if len(p) > 1 and p.endswith("/"):
        p = p.rstrip("/")
    return p


def extract_backend_routes() -> list[BackendRoute]:
    routes: list[BackendRoute] = []
    for py_file in sorted(BE_API.glob("*.py")):
        text = py_file.read_text(encoding="utf-8", errors="replace")
        prefixes: dict[str, str] = {}
        for m in ROUTER_PREFIX_RE.finditer(text):
            prefixes[m.group(1)] = m.group(2)
        for m in ROUTE_DECORATOR_RE.finditer(text):
            router_var = m.group(1)
            method = m.group(2).upper()
            subpath = m.group(3)
            prefix = prefixes.get(router_var, "")
            full = f"{API_PREFIX}{prefix}{subpath}"
            routes.append(
                BackendRoute(method=method, path=normalize_path(full), file=py_file.name)
            )
    return routes


def extract_frontend_calls() -> list[FrontendCall]:
    calls: list[FrontendCall] = []
    for src_file in sorted(FE_SRC.rglob("*")):
        if src_file.suffix not in {".js", ".jsx"}:
            continue
        text = src_file.read_text(encoding="utf-8", errors="replace")
        rel = str(src_file.relative_to(ROOT)).replace("\\", "/")
        for i, line in enumerate(text.splitlines(), start=1):
            for m in FE_ABRIR_PDF_RE.finditer(line):
                calls.append(
                    FrontendCall(
                        method="GET",
                        path=normalize_path(m.group(1)),
                        file=rel,
                        line=i,
                    )
                )
            for m in FE_API_CONCAT_RE.finditer(line):
                fn = m.group(1).lower()
                method = "DELETE" if fn == "del" else fn.upper()
                calls.append(
                    FrontendCall(
                        method=method,
                        path=normalize_path(m.group(2)),
                        file=rel,
                        line=i,
                    )
                )
            for m in FE_API_TEMPLATE_RE.finditer(line):
                tmpl = m.group(2)
                if "${" in tmpl and "}" not in tmpl:
                    continue
                if re.search(r"\?[^?`]*`", tmpl):
                    continue
                fn = m.group(1).lower()
                explicit = m.group(3)
                if fn == "blob":
                    method = (explicit or "POST").upper()
                elif fn == "del":
                    method = "DELETE"
                else:
                    method = fn.upper()
                calls.append(
                    FrontendCall(
                        method=method,
                        path=normalize_path(tmpl),
                        file=rel,
                        line=i,
                    )
                )
            for m in FE_API_CALL_RE.finditer(line):
                fn = m.group(1).lower()
                url = m.group(2)
                if "${" in url:
                    continue
                explicit = m.group(3)
                if fn == "del":
                    method = "DELETE"
                elif fn == "blob":
                    method = (explicit or "POST").upper()
                else:
                    method = fn.upper()
                calls.append(
                    FrontendCall(
                        method=method,
                        path=normalize_path(url),
                        file=rel,
                        line=i,
                    )
                )
            for m in FE_FETCH_RE.finditer(line):
                calls.append(
                    FrontendCall(
                        method=m.group(2).upper(),
                        path=normalize_path(m.group(1)),
                        file=rel,
                        line=i,
                    )
                )
            for m in FE_FETCH_API_TEMPLATE_RE.finditer(line):
                calls.append(
                    FrontendCall(
                        method=m.group(2).upper(),
                        path=normalize_path(m.group(1)),
                        file=rel,
                        line=i,
                    )
                )
    seen: set[tuple] = set()
    unique: list[FrontendCall] = []
    for call in calls:
        key = (call.method, call.path, call.file, call.line)
        if key not in seen:
            seen.add(key)
            unique.append(call)
    return unique


def load_baseline() -> tuple[set[tuple], set[tuple]]:
    if not BASELINE_PATH.exists():
        return set(), set()
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    mm = {
        (
            normalize_path(item["path"]),
            item["frontend_method"].upper(),
            item["backend_method"].upper(),
        )
        for item in data.get("method_mismatch", [])
    }
    mf = {
        (normalize_path(item["path"]), item["backend_method"].upper())
        for item in data.get("missing_frontend", [])
    }
    return mm, mf


def path_matches(call_path: str, route_path: str) -> bool:
    if call_path == route_path:
        return True
    cp = call_path.strip("/").split("/")
    rp = route_path.strip("/").split("/")
    if len(cp) > len(rp):
        return False
    if len(cp) < len(rp):
        if not all(seg == "{param}" for seg in rp[len(cp) :]):
            return False
    for a, b in zip(cp, rp[: len(cp)], strict=True):
        if a == b:
            continue
        if b == "{param}" or a == "{param}":
            continue
        return False
    return True


def find_backend_match(
    call_path: str, method: str, routes: list[BackendRoute]
) -> BackendRoute | None:
    matches = [r for r in routes if path_matches(call_path, r.path)]
    if not matches:
        return None
    for r in matches:
        if r.method == method:
            return r
    return matches[0]


def analyze(
    routes: list[BackendRoute], calls: list[FrontendCall]
) -> list[Issue]:
    baseline_mm, baseline_mf = load_baseline()
    issues: list[Issue] = []

    consumed_backend: set[tuple[str, str]] = set()

    for call in calls:
        match = find_backend_match(call.path, call.method, routes)
        if match is None:
            issues.append(
                Issue(
                    kind="MISSING_BACKEND",
                    path=call.path,
                    frontend_method=call.method,
                    backend_method=None,
                    file=call.file,
                    line=call.line,
                )
            )
            continue
        consumed_backend.add((match.path, match.method))
        if match.method != call.method:
            key = (call.path, call.method, match.method)
            issues.append(
                Issue(
                    kind="METHOD_MISMATCH",
                    path=call.path,
                    frontend_method=call.method,
                    backend_method=match.method,
                    file=call.file,
                    line=call.line,
                    in_baseline=key in baseline_mm,
                )
            )

    baseline_mf_paths: list[tuple[str, str]] = []
    if BASELINE_PATH.exists():
        for item in json.loads(BASELINE_PATH.read_text(encoding="utf-8")).get(
            "missing_frontend", []
        ):
            baseline_mf_paths.append(
                (normalize_path(item["path"]), item["backend_method"].upper())
            )

    for route in routes:
        if (route.path, route.method) in consumed_backend:
            continue
        if not route.path.startswith(API_PREFIX):
            continue
        in_baseline = any(
            path_matches(route.path, bp) and route.method == bm
            for bp, bm in baseline_mf_paths
        )
        issues.append(
            Issue(
                kind="ORPHAN_BACKEND",
                path=route.path,
                frontend_method=None,
                backend_method=route.method,
                file=f"neurosoft-backend/app/presentation/api/v1/{route.file}",
                in_baseline=in_baseline,
            )
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="API manifest alignment check")
    parser.add_argument("--json", type=Path, help="Write JSON report to path")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on any METHOD_MISMATCH/MISSING_BACKEND even if in baseline",
    )
    parser.add_argument(
        "--fail-new",
        action="store_true",
        default=True,
        help="Exit 1 on issues not in baseline (default: true)",
    )
    parser.add_argument(
        "--no-fail-new",
        dest="fail_new",
        action="store_false",
        help="Report only, always exit 0",
    )
    args = parser.parse_args()

    routes = extract_backend_routes()
    calls = extract_frontend_calls()
    issues = analyze(routes, calls)

    critical_kinds = {"METHOD_MISMATCH", "MISSING_BACKEND"}
    critical = [i for i in issues if i.kind in critical_kinds]
    new_critical = [i for i in critical if not i.in_baseline]
    orphans = [i for i in issues if i.kind == "ORPHAN_BACKEND" and not i.in_baseline]

    report = {
        "backend_routes": len(routes),
        "frontend_calls": len(calls),
        "method_mismatch": [asdict(i) for i in issues if i.kind == "METHOD_MISMATCH"],
        "missing_backend": [asdict(i) for i in issues if i.kind == "MISSING_BACKEND"],
        "orphan_backend_count": len(orphans),
        "orphan_backend_sample": [asdict(i) for i in orphans[:20]],
        "baseline_items": sum(1 for i in issues if i.in_baseline),
        "new_critical_count": len(new_critical),
    }

    print(f"Backend routes: {len(routes)}")
    print(f"Frontend API calls: {len(calls)}")
    print(f"METHOD_MISMATCH: {len([i for i in issues if i.kind == 'METHOD_MISMATCH'])}")
    print(f"MISSING_BACKEND: {len([i for i in issues if i.kind == 'MISSING_BACKEND'])}")
    print(f"ORPHAN_BACKEND (sample max 20): {len(orphans)}")
    print(f"In baseline (known P0): {report['baseline_items']}")
    print(f"New critical issues: {len(new_critical)}")

    for issue in critical:
        flag = " [BASELINE]" if issue.in_baseline else " [NEW]"
        loc = f"{issue.file}:{issue.line}" if issue.line else issue.file
        print(
            f"  {issue.kind}{flag}: {issue.path} "
            f"FE={issue.frontend_method} BE={issue.backend_method} @ {loc}"
        )

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON report: {args.json}")

    if args.strict and critical:
        return 1
    if args.fail_new and new_critical:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
