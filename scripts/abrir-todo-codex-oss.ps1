# Abre en el navegador TODO lo necesario para la solicitud Codex OSS.
# Uso: clic derecho -> Ejecutar con PowerShell
#   o desde la raiz: powershell -ExecutionPolicy Bypass -File scripts/abrir-todo-codex-oss.ps1

$repo = "https://github.com/mrhyde42098/NeuroSoft"

function Open-Url([string]$url) {
  Start-Process $url
  Start-Sleep -Milliseconds 800
}

Write-Host ""
Write-Host "=== NeuroSoft — asistente Codex OSS ===" -ForegroundColor Cyan
Write-Host "Se abriran varias pestanas. Sigue el orden en pantalla."
Write-Host ""

# 1) Repo (About)
Open-Url $repo
Write-Host "[1] Repo abierto."
Write-Host "    -> A la DERECHA busca la caja 'About' y el icono de engranaje."
Write-Host "    -> Pega la Description y Topics que salen abajo, luego Save."
Write-Host ""

# 2) Tres issues pre-rellenados (solo dar Submit en cada uno)
$issues = @(
  @{
    title = "[roadmap]: E2E Playwright paciente -> evaluacion -> informe Pro"
    body  = "Flujo critico de regresion antes de releases beta.`n`n- [ ] Crear paciente sintetico`n- [ ] Aplicar subtest WISC con baremo conocido`n- [ ] Generar informe Pro y validar CI esperado`n`nRef: docs/ESTADO_VIVO.md"
    labels = "roadmap"
  },
  @{
    title = "[roadmap]: Etiquetas/tags en panel de pacientes"
    body  = "Quick win pendiente del roadmap 2026. Permitir filtrar pacientes por etiquetas clinicas (TDAH, adulto mayor, remision EPS, etc.).`n`nPrioridad: P1"
    labels = "roadmap"
  },
  @{
    title = "[feature]: Placeholders visuales de estimulos WISC/WAIS en evaluacion"
    body  = "Mejorar fidelidad del flujo mostrando estimulos desde stimuli_manifest.json. Sin copiar material con copyright en el repo.`n`nRef: docs/stimuli/STIMULI_INVENTORY.md"
    labels = "enhancement"
  }
)

$i = 2
foreach ($issue in $issues) {
  $q = @{
    title  = $issue.title
    body   = $issue.body
    labels = $issue.labels
  }
  $query = ($q.GetEnumerator() | ForEach-Object {
    "{0}={1}" -f [uri]::EscapeDataString($_.Key), [uri]::EscapeDataString($_.Value)
  }) -join "&"
  Open-Url "$repo/issues/new?$query"
  Write-Host "[$i] Issue pre-rellenado abierto — revisa y clic en 'Submit new issue'."
  $i++
}

# 3) Formulario OpenAI + Organization ID
Open-Url "https://openai.com/es-419/form/codex-for-oss/"
Open-Url "https://platform.openai.com/settings/organization/general"
Write-Host "[$i] Formulario Codex OSS + pagina del Organization ID (org-...) abiertos."
Write-Host ""

Write-Host "=== PEGAR EN ABOUT (paso 1) ===" -ForegroundColor Yellow
Write-Host "Description:"
Write-Host "OSS neuropsychology platform for Colombia/LATAM — clinical scoring engine, Colombian norms, PDF reports, RIPS. FastAPI + React. 1000+ tests."
Write-Host ""
Write-Host "Topics (uno por uno o separados por espacio):"
Write-Host "neuropsychology healthcare fastapi react python colombia open-source clinical-software sqlite mental-health"
Write-Host ""
Write-Host "Guia completa del formulario: docs/infra/CODEX_OSS_FORMULARIO.md"
Write-Host ""
