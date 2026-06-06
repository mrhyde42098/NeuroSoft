# Configura About + topics en GitHub (paso manual asistido).
# Requiere un Personal Access Token con scope "repo".
# Crear token: https://github.com/settings/tokens/new  (classic → marcar "repo")

param(
  [Parameter(Mandatory = $true)]
  [string]$GitHubToken
)

$owner = "mrhyde42098"
$repo = "NeuroSoft"
$headers = @{
  Authorization = "Bearer $GitHubToken"
  Accept        = "application/vnd.github+json"
  "X-GitHub-Api-Version" = "2022-11-28"
  "User-Agent"  = "NeuroSoft-OSS-Setup"
}

$description = "OSS neuropsychology platform for Colombia/LATAM — clinical scoring engine, Colombian norms, PDF reports, RIPS. FastAPI + React. 1000+ tests."
$topics = @(
  "neuropsychology", "healthcare", "fastapi", "react", "python",
  "colombia", "open-source", "clinical-software", "sqlite", "mental-health"
)

Write-Host "Actualizando descripcion del repo..."
$body = @{ description = $description } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "https://api.github.com/repos/$owner/$repo" -Headers $headers -Body $body -ContentType "application/json"

Write-Host "Actualizando topics..."
$topicBody = @{ names = $topics } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "https://api.github.com/repos/$owner/$repo/topics" -Headers $headers -Body $topicBody -ContentType "application/json"

Write-Host ""
Write-Host "Listo. About actualizado en: https://github.com/$owner/$repo"
Write-Host "Issues: ejecuta el workflow Bootstrap Codex OSS en Actions (o ya corrio solo)."
