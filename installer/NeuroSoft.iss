; ═══════════════════════════════════════════════════════════════════════
; NeuroSoft.iss — Script de instalador Inno Setup para NeuroSoft App
; ───────────────────────────────────────────────────────────────────────
; Compila con:
;   "C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe" NeuroSoft.iss
;
; Salida:  D:\NeuroSoftApp\dist\NeuroSoft-Setup.exe
; ═══════════════════════════════════════════════════════════════════════

#define MyAppName        "NeuroSoft App"
#define MyAppShortName   "NeuroSoft"
#define MyAppPublisher   "NeuroSoft"
#define MyAppURL         "https://neurosoft.local"
#define MyAppExeName     "NeuroSoft.exe"
#define MyAppId          "{{A3F1C8B2-9D4E-4C5A-B7E1-NEUROSOFT2026}}"

[Setup]
; ─── Identificación de la aplicación ────────────────────────────────
AppId={#MyAppId}
AppName={#MyAppName}
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppContact=support@neurosoft.local
AppCopyright=Copyright (C) 2026 NeuroSoft

; ─── Carpeta de instalación por defecto ────────────────────────────
; El usuario podrá cambiar esta ruta durante la instalación.
DefaultDirName={autopf}\NeuroSoft
DefaultGroupName=NeuroSoft
DisableProgramGroupPage=no
DisableDirPage=no
AllowNoIcons=yes

; ─── Privilegios ───────────────────────────────────────────────────
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ─── Apariencia ────────────────────────────────────────────────────
SetupIconFile=D:\NeuroSoftApp\neurosoft.ico
UninstallDisplayIcon={app}\NeuroSoft.exe
WizardStyle=modern
WizardSizePercent=120
ShowLanguageDialog=no

; ─── Salida del instalador ─────────────────────────────────────────
OutputDir=D:\NeuroSoftApp\dist
OutputBaseFilename=NeuroSoft-Setup
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; ─── Comportamiento ────────────────────────────────────────────────
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
CloseApplications=yes
RestartApplications=no
DisableWelcomePage=no
DisableReadyPage=no
DisableFinishedPage=no

; ─── Idiomas ───────────────────────────────────────────────────────
[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

; ─── Mensajes personalizados (overrides) ───────────────────────────
[Messages]
spanish.WelcomeLabel1=Bienvenida al asistente de instalación de [name]
spanish.WelcomeLabel2=Este instalador colocará NeuroSoft App en tu equipo.%n%nNeuroSoft es un sistema integral de evaluación neuropsicológica para profesionales clínicos en Colombia.%n%nSe recomienda cerrar otras aplicaciones antes de continuar.
spanish.FinishedHeadingLabel=Instalación completada
spanish.FinishedLabelNoIcons=Se ha instalado [name] correctamente.
spanish.FinishedLabel=Se ha instalado [name] correctamente. La aplicación puede iniciarse desde los accesos directos.
spanish.ClickFinish=Haz clic en Finalizar para salir del asistente.
spanish.WizardSelectDir=Elige dónde instalar NeuroSoft
spanish.SelectDirDesc=¿Dónde se debe instalar NeuroSoft App?
spanish.SelectDirLabel3=El instalador colocará [name] en la siguiente carpeta.
spanish.SelectDirBrowseLabel=Para continuar, haz clic en Siguiente. Si deseas elegir una carpeta diferente, haz clic en Examinar.

; ─── Tareas opcionales (checkboxes) ────────────────────────────────
[Tasks]
Name: "desktopicon"; \
  Description: "Crear un acceso directo en el &Escritorio"; \
  GroupDescription: "Iconos adicionales:"; \
  Flags: checkedonce
Name: "quicklaunchicon"; \
  Description: "Crear un acceso directo en la barra de Inicio rápido"; \
  GroupDescription: "Iconos adicionales:"; \
  Flags: unchecked
Name: "openmanual"; \
  Description: "Abrir el &Manual del Beta Tester al terminar"; \
  GroupDescription: "Documentación:"; \
  Flags: checkedonce

; ─── Archivos a copiar ─────────────────────────────────────────────
[Files]
; Aplicación principal — el .exe empaquetado con PyInstaller (~1.3 GB)
Source: "D:\NeuroSoftApp\dist\NeuroSoft.exe"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

; §ollama-fix: Instalador de Ollama distribuido como archivo SEPARADO
; (no bundleado dentro de NeuroSoft.exe para evitar corrupción).
; El backend lo busca en {app}\vendor\ollama\OllamaSetup.exe al primer arranque.
Source: "D:\NeuroSoftApp\vendor\ollama\OllamaSetup.exe"; \
  DestDir: "{app}\vendor\ollama"; \
  Flags: ignoreversion skipifsourcedoesntexist

; Manual del beta tester en PDF
Source: "D:\NeuroSoftApp\dist\MANUAL_BETA_TESTER.pdf"; \
  DestDir: "{app}"; \
  DestName: "Manual del Beta Tester.pdf"; \
  Flags: ignoreversion

; Icono para accesos directos
Source: "D:\NeuroSoftApp\neurosoft.ico"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

; ─── Accesos directos (Menú Inicio + Escritorio) ───────────────────
[Icons]
Name: "{group}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\neurosoft.ico"; \
  Comment: "Sistema de evaluación neuropsicológica"

Name: "{group}\Manual del Beta Tester"; \
  Filename: "{app}\Manual del Beta Tester.pdf"; \
  Comment: "Guía paso a paso de uso del beta tester"

Name: "{group}\Desinstalar {#MyAppName}"; \
  Filename: "{uninstallexe}"

Name: "{autodesktop}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\neurosoft.ico"; \
  Tasks: desktopicon

Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\neurosoft.ico"; \
  Tasks: quicklaunchicon

; ─── Acciones al finalizar la instalación ──────────────────────────
[Run]
; Abrir el manual PDF si el usuario marcó la opción
Filename: "{app}\Manual del Beta Tester.pdf"; \
  Description: "Abrir el Manual del Beta Tester"; \
  Flags: postinstall shellexec skipifsilent; \
  Tasks: openmanual

; Lanzar NeuroSoft (opcional, sin auto-check)
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Iniciar {#MyAppName} ahora"; \
  Flags: postinstall nowait skipifsilent unchecked

; ─── Limpieza al desinstalar ───────────────────────────────────────
[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\NeuroSoft\cache"

[Code]
// Ajustes visuales del wizard al inicializar.
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Font.Size := 10;
end;
