#define MyAppName "Hamzaoui Facturation"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Pharmacie Hamzaoui Hamid"
#define MyAppExeName "HamzaouiFacturation.exe"

[Setup]
AppId={{8B1F1D9A-7B1D-4F3C-9C2E-2D9D4A1E4F10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Hamzaoui Facturation
DefaultGroupName={#MyAppName}
OutputDir=output
OutputBaseFilename=Hamzaoui-Facturation-Setup-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=..\assets\hamzaoui_logo.ico

[Files]
Source="..\dist\HamzaouiFacturation\*"; DestDir="{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name="{autodesktop}\Hamzaoui Facturation"; Filename="{app}\{#MyAppExeName}"; WorkingDir="{app}"
Name="{group}\Hamzaoui Facturation"; Filename="{app}\{#MyAppExeName}"; WorkingDir="{app}"

[Run]
Filename="{app}\{#MyAppExeName}"; Description="Lancer Hamzaoui Facturation"; Flags=nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\assets"
