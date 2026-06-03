#define MyAppName "NeuroSoft"
#define MyAppVersion "2026.05-beta"
#define MyAppPublisher "NeuroSoft"
#define MyAppExeName "NeuroSoft.exe"

[Setup]
AppId={{B7B93E68-9D58-4C9D-AAD3-0E0F50542026}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\NeuroSoft
DefaultGroupName=NeuroSoft
DisableProgramGroupPage=yes
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=NeuroSoft_Beta_Setup
SetupIconFile=..\neurosoft.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
MinVersion=10.0
SetupLogging=yes
LicenseFile=..\LICENSE

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "..\dist\NeuroSoft.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\GUIA_RAPIDA_BETA.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\INSTRUCCIONES_BETA_TESTER.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\NeuroSoft"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Guia beta"; Filename: "{app}\GUIA_RAPIDA_BETA.md"
Name: "{autodesktop}\NeuroSoft"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir NeuroSoft"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
