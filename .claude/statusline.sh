#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# .claude/statusline.sh — Status line contextual para NeuroSoft
# ───────────────────────────────────────────────────────────────────────
# Muestra: rama git · #modificados · último build · tamaño exe
# Para activar, agregar a ~/.claude/settings.json:
#   "statusLine": {
#     "type": "command",
#     "command": "D:/NeuroSoftApp/.claude/statusline.sh"
#   }
# ═══════════════════════════════════════════════════════════════════════

# Leer el JSON de contexto desde stdin (no usado por ahora, pero disponible)
INPUT=$(cat 2>/dev/null || echo "{}")
CWD=$(echo "$INPUT" | node -e "try{const d=JSON.parse(require('fs').readFileSync(0,'utf8'));console.log(d.workspace?.current_dir||d.cwd||'')}catch{}" 2>/dev/null)

# Si no estamos en el proyecto NeuroSoft, mostrar solo info genérica
if [[ "$CWD" != *"NeuroSoftApp"* ]]; then
  echo "⌁ Claude Code"
  exit 0
fi

cd /d/NeuroSoftApp 2>/dev/null || exit 0

# Rama git
BRANCH=$(git branch --show-current 2>/dev/null || echo "?")

# Archivos modificados
MOD=$(git status --short 2>/dev/null | wc -l | tr -d ' ')

# Último build del .exe
EXE="/d/NeuroSoftApp/dist/NeuroSoft.exe"
if [[ -f "$EXE" ]]; then
  EXE_SIZE=$(du -m "$EXE" 2>/dev/null | cut -f1)
  EXE_INFO="📦 ${EXE_SIZE}MB"
else
  EXE_INFO="📦 no build"
fi

# Setup final
SETUP="/d/NeuroSoftApp/dist/NeuroSoft-Setup.exe"
if [[ -f "$SETUP" ]]; then
  SETUP_AGE=$(stat -c %Y "$SETUP" 2>/dev/null)
  NOW=$(date +%s)
  AGE_HOURS=$(( (NOW - SETUP_AGE) / 3600 ))
  if (( AGE_HOURS < 24 )); then
    SETUP_INFO="🚀 Setup ${AGE_HOURS}h"
  else
    SETUP_INFO="🚀 Setup ${AGE_HOURS}h ⚠"
  fi
else
  SETUP_INFO=""
fi

# Output formateado con colores ANSI
printf "🧠 \033[36mNeuroSoft\033[0m  \033[33m⎇ %s\033[0m" "$BRANCH"
if [[ "$MOD" != "0" ]]; then
  printf "  \033[35m●%s\033[0m" "$MOD"
fi
printf "  %s" "$EXE_INFO"
[[ -n "$SETUP_INFO" ]] && printf "  %s" "$SETUP_INFO"
echo
