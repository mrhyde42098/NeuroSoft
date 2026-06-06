# Abre en el navegador TODO lo necesario para la solicitud Codex OSS.
# Uso: powershell -ExecutionPolicy Bypass -File scripts/abrir-todo-codex-oss.ps1

$repo = "https://github.com/mrhyde42098/NeuroSoft"

function Open-Url([string]$url) {
  Start-Process $url
  Start-Sleep -Milliseconds 800
}

Write-Host ""
Write-Host "=== NeuroSoft - asistente Codex OSS ===" -ForegroundColor Cyan
Write-Host ""

Open-Url $repo
Write-Host "[1] Repo abierto - engranaje About a la derecha, pega Description/Topics y Save."

$issue1Title = "[roadmap]: E2E Playwright paciente -> evaluacion -> informe Pro"
$issue1Body = "Flujo critico de regresion antes de releases beta.`n`n- [ ] Crear paciente sintetico`n- [ ] Aplicar subtest WISC`n- [ ] Generar informe Pro`n`nRef: docs/ESTADO_VIVO.md"

$issue2Title = "[roadmap]: Etiquetas/tags en panel de pacientes"
$issue2Body = "Quick win roadmap 2026. Filtrar pacientes por etiquetas clinicas.`n`nPrioridad: P1"

$issue3Title = "[feature]: Placeholders visuales de estimulos WISC/WAIS"
$issue3Body = "Mostrar estimulos desde stimuli_manifest.json sin material con copyright.`n`nRef: docs/stimuli/STIMULI_INVENTORY.md"

function New-IssueUrl($title, $body, $label) {
  $t = [uri]::EscapeDataString($title)
  $b = [uri]::EscapeDataString($body)
  $l = [uri]::EscapeDataString($label)
  return ($repo + "/issues/new?title=" + $t + "&body=" + $b + "&labels=" + $l)
}

$issueUrls = @(
  (New-IssueUrl $issue1Title $issue1Body "roadmap")
  (New-IssueUrl $issue2Title $issue2Body "roadmap")
  (New-IssueUrl $issue3Title $issue3Body "enhancement")
)

$n = 2
foreach ($url in $issueUrls) {
  Open-Url $url
  Write-Host "[$n] Issue pre-rellenado - clic Submit new issue."
  $n++
}

Open-Url "https://openai.com/es-419/form/codex-for-oss/"
Open-Url "https://platform.openai.com/settings/organization/general"
Write-Host "[$n] Formulario Codex + Organization ID abiertos."
Write-Host ""
Write-Host "=== PEGAR EN ABOUT ===" -ForegroundColor Yellow
Write-Host "OSS neuropsychology platform for Colombia/LATAM - clinical scoring engine, Colombian norms, PDF reports, RIPS. FastAPI + React. 1000+ tests."
Write-Host "Topics: neuropsychology healthcare fastapi react python colombia open-source clinical-software sqlite mental-health"
Write-Host ""
