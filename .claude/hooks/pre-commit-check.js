/**
 * .claude/hooks/pre-commit-check.js
 * PreToolUse hook: bloquea git commit si ESLint o py_compile fallan.
 * Lee stdin con el tool_input de Claude Code y actúa solo en git commit.
 */

const { execSync } = require("child_process");

let input;
try {
  input = JSON.parse(require("fs").readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const cmd = (input.tool_input && input.tool_input.command) || "";

// Solo aplica a commits de git
if (!/^git\s+commit/.test(cmd)) process.exit(0);

const ROOT = "D:/NeuroSoftApp";
const errors = [];

// ── 1. ESLint frontend ────────────────────────────────────────────────────
try {
  execSync("npm run lint", {
    cwd: `${ROOT}/neurosoft-frontend`,
    stdio: "pipe",
    timeout: 30_000,
  });
} catch (e) {
  errors.push(
    "❌ ESLint falló (frontend):\n" +
      (e.stdout?.toString().trim() || "") +
      (e.stderr?.toString().trim() || "")
  );
}

// ── 2. py_compile en .py staged (solo backend, excluye tests) ────────────
try {
  const staged = execSync("git diff --cached --name-only", {
    cwd: ROOT,
    stdio: "pipe",
  })
    .toString()
    .trim()
    .split("\n")
    .filter(
      (f) =>
        f.endsWith(".py") &&
        !f.includes("/tests/") &&
        !f.includes("\\tests\\")
    );

  for (const f of staged) {
    if (!f) continue;
    try {
      execSync(`python -m py_compile "${ROOT}/${f}"`, { stdio: "pipe" });
    } catch (e) {
      errors.push(
        `❌ Syntax error en ${f}:\n${e.stderr?.toString().trim() || ""}`
      );
    }
  }
} catch {
  // git diff falló (sin repo o sin staged) — no bloquear
}

if (errors.length > 0) {
  console.error(
    "⛔ Pre-commit check bloqueó el commit:\n\n" + errors.join("\n\n")
  );
  process.exit(2);
}

process.exit(0);
