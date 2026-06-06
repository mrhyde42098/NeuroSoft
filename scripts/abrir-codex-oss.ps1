# Abre el formulario Codex OSS y la página del Organization ID de OpenAI.
Start-Process "https://openai.com/es-419/form/codex-for-oss/"
Start-Sleep -Seconds 1
Start-Process "https://platform.openai.com/settings/organization/general"
Write-Host ""
Write-Host "Formulario Codex OSS y ajustes de OpenAI abiertos en el navegador."
Write-Host "En OpenAI: copia el Organization ID (empieza con org-...) y pegalo en el formulario."
Write-Host "Guia completa: docs/infra/CODEX_OSS_FORMULARIO.md"
