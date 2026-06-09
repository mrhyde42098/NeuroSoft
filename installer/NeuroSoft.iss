; ═══════════════════════════════════════════════════════════════════════
; NeuroSoftOptimized.iss — Instalador Inno Setup 6 optimizado
; ───────────────────────────────────────────────────────────────────────
; Compilar:
;   ISCC.exe installer\NeuroSoftOptimized.iss
;
; Salida: dist\NeuroSoft-Setup.exe
;
; Mejoras vs NeuroSoft.iss:
;   • Rutas relativas al repo (sin hardcode D:\NeuroSoftApp)
;   • Ollama como componente OPCIONAL (~1.3 GB) — instalador base ~50 MB
;   • Compresión lzma2/max + solid
;   • Soporta PyInstaller onedir (dist\NeuroSoft\*) o onefile legacy
;   • Datos de usuario en %APPDATA%\NeuroSoft (PrivilegesRequired=lowest)
; ═══════════════════════════════════════════════════════════════════════

#define SourceRoot     ".."
#define MyAppName      "NeuroSoft App"
#define MyAppShortName "NeuroSoft"
#define MyAppPublisher "NeuroSoft"
#define MyAppURL       "https://neurosoft.local"
#define MyAppExeName   "NeuroSoft.exe"
#define MyAppVersion   "2.0.0"
#define MyAppId        "{{A3F1C8B2-9D4E-4C5A-B7E1-NEUROSOFT2026}}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppContact=support@neurosoft.local
AppCopyright=Copyright (C) 2026 NeuroSoft

; Instalación en Program Files (usuario puede cambiar ruta)
DefaultDirName={autopf}\{#MyAppShortName}
DefaultGroupName={#MyAppShortName}
DisableProgramGroupPage=no
AllowNoIcons=yes

; BD SQLite y backups viven en %APPDATA%\NeuroSoft — NO requiere admin
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

SetupIconFile={#SourceRoot}\neurosoft.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
WizardSizePercent=120
ShowLanguageDialog=no

OutputDir={#SourceRoot}\dist
OutputBaseFilename=NeuroSoft-Setup
; Máxima compresión (trade-off: compile más lento, setup más pequeño)
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4
LZMABlockSize=65536

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Types]
Name: "compact"; Description: "Instalación compacta (sin Ollama, ~50 MB)"
Name: "full"; Description: "Instalación completa (con IA local Ollama, ~1.4 GB)"
Name: "custom"; Description: "Personalizada"; Flags: iscustom

[Components]
Name: "core"; Description: "NeuroSoft App (obligatorio)"; Types: full compact custom; Flags: fixed
Name: "ollama"; Description: "Motor de IA local Ollama (~1.3 GB)"; Types: full; Flags: disablenouninstallwarning
Name: "docs"; Description: "Manual del beta tester (PDF)"; Types: full compact custom

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el &Escritorio"; GroupDescription: "Iconos:"; Flags: checkedonce
Name: "openmanual"; Description: "Abrir manual al finalizar"; GroupDescription: "Documentación:"; Components: docs; Flags: checkedonce

[Files]
; ── PyInstaller onedir (config_optimizada.spec) ─────────────
#ifexist "..\dist\NeuroSoft\NeuroSoft.exe"
Source: "{#SourceRoot}\dist\NeuroSoft\*"; \
  DestDir: "{app}"; \
  Components: core; \
  Flags: ignoreversion recursesubdirs createallsubdirs
#else
; ── Fallback: onefile legacy (neurosoft.spec) ───────────────
Source: "{#SourceRoot}\dist\{#MyAppExeName}"; \
  DestDir: "{app}"; \
  Components: core; \
  Flags: ignoreversion
#endif

; Ollama — solo se embebe en el setup si ISCC se invoca con /DINCLUDE_OLLAMA=1
; (evita que el .exe del instalador pese 1.4 GB cuando el componente es opcional)
#ifdef INCLUDE_OLLAMA
Source: "{#SourceRoot}\vendor\ollama\OllamaSetup.exe"; \
  DestDir: "{app}\vendor\ollama"; \
  Components: ollama; \
  Flags: ignoreversion
#endif

Source: "{#SourceRoot}\dist\MANUAL_BETA_TESTER.pdf"; \
  DestDir: "{app}"; \
  DestName: "Manual del Beta Tester.pdf"; \
  Components: docs; \
  Flags: ignoreversion skipifsourcedoesntexist

Source: "{#SourceRoot}\neurosoft.ico"; \
  DestDir: "{app}"; \
  Components: core; \
  Flags: ignoreversion

; Manifest de actualizaciones (opcional, para auto-update offline/USB)
Source: "{#SourceRoot}\dist\update.json"; \
  DestDir: "{app}"; \
  Components: core; \
  Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; Carpeta de datos del usuario (la app escribe en %APPDATA%, esto es solo hint)
Name: "{userappdata}\NeuroSoft"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\neurosoft.ico"; \
  Comment: "Evaluación neuropsicológica"

Name: "{group}\Manual del Beta Tester"; \
  Filename: "{app}\Manual del Beta Tester.pdf"; \
  Components: docs; \
  Comment: "Guía beta tester"

Name: "{group}\Desinstalar {#MyAppName}"; \
  Filename: "{uninstallexe}"

Name: "{autodesktop}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\neurosoft.ico"; \
  Tasks: desktopicon

[Run]
Filename: "{app}\Manual del Beta Tester.pdf"; \
  Description: "Abrir manual"; \
  Flags: postinstall shellexec skipifsilent; \
  Tasks: openmanual; \
  Components: docs

Filename: "{app}\{#MyAppExeName}"; \
  Description: "Iniciar {#MyAppName}"; \
  Flags: postinstall nowait skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\NeuroSoft\cache"

[Messages]
spanish.WelcomeLabel2=Este instalador coloca NeuroSoft en tu equipo.%n%nLa base de datos clínica se guarda en %APPDATA%\NeuroSoft — no requiere permisos de administrador.%n%nOllama (IA local) es opcional y ocupa ~1.3 GB adicionales.

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Font.Size := 10;
end;

function InitializeSetup: Boolean;
begin
  Result := True;
end;
