---
name: checkpoint
description: Crea un snapshot rápido del estado actual del proyecto (commit local con timestamp + tag) sin push remoto. Útil ANTES de cambios grandes para poder revertir. Usar cuando se vaya a hacer una refactorización grande, modificar muchos archivos, o experimentar con algo arriesgado.
---

# Checkpoint — snapshot de seguridad

Crea un commit local de recuperación antes de cambios arriesgados.

## Cuándo activarte

Usuario escribió `/checkpoint` con opcional descripción:
- `/checkpoint` → snapshot genérico
- `/checkpoint antes de refactor RCI` → snapshot con descripción
- `/checkpoint pre-audit baremos` → snapshot etiquetado

## Protocolo

### Paso 1: Verificar estado actual

```bash
cd D:\NeuroSoftApp
git status
git rev-parse --abbrev-ref HEAD
```

Si hay cambios sin commitear o sin staging, los staging y commiteamos. Si no hay cambios, abortamos con mensaje "No hay cambios para snapshot".

### Paso 2: Staging selectivo

```bash
git add -A
```

Pero NUNCA stagear:
- `data/BD_NEURO_MAESTRA.json` (debería estar igual; si cambió, ALERTA)
- Archivos en `vendor/`, `dist/`, `build/`, `__pycache__/`, `node_modules/`
- `*.db`, `*.sqlite`, `.env`

(El `.gitignore` ya cubre lo último; verificar que no haya nada raro en `git status` antes de hacer add).

### Paso 3: Verificar que BD_NEURO_MAESTRA.json NO está modificado

```bash
git diff --cached --name-only | grep -i "BD_NEURO_MAESTRA"
```

Si aparece, **ABORTAR** y reportar al usuario. Es la regla crítica del proyecto.

### Paso 4: Commit con mensaje estructurado

```bash
git commit -m "checkpoint: <descripción o timestamp ISO>

Snapshot automático antes de cambios. Para revertir:
  git reset --hard <hash de este commit>

Estado al momento del checkpoint:
  - Frontend: <\$(ls neurosoft-frontend/dist 2>/dev/null && echo \"compilado\" || echo \"sin compilar\")>
  - Backend: <python -m py_compile neurosoft-backend/app/main.py 2>&1 && echo \"compila\" || echo \"warning: no compila\">

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

### Paso 5: Reportar al usuario

```
✅ Checkpoint creado · <hash corto>

📝 Mensaje: "<descripción>"
📊 Archivos: N
🌿 Rama: <rama>

Para revertir más tarde:
  git reset --hard <hash>
  git stash pop  # si estabas en medio de cambios
```

## Reglas

1. **NUNCA hacer `git push`** desde checkpoint. Es local-only.
2. **NUNCA usar `git reset --hard`** durante el checkpoint — solo crear el commit.
3. **NUNCA stagear** `BD_NEURO_MAESTRA.json` — si está modificado por accidente, abortar y avisar.
4. **Verificar `.gitignore`** está activo: `vendor/`, `dist/`, `__pycache__/` no deben aparecer en el staging.

## Modo "antes de operación riesgosa"

Si el usuario llama `/checkpoint antes de XXX`, después del commit ofrece:
- "Snapshot listo. ¿Procedo con <XXX>? Si algo sale mal, puedo revertir con `git reset --hard <hash>`."

## Limpieza

NO crear muchos checkpoints en serie. Si el usuario hace `/checkpoint` repetidas veces en una sesión, sugerir consolidar (git rebase interactivo) al final.
