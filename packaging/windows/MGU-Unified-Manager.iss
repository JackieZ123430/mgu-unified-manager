#define MyAppName "MGU Unified Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MGU Unified Manager"
#define MyAppExeName "MGU Unified Manager.exe"

[Setup]
AppId={{9D3E9B45-3B5B-4D58-A3D4-4E63D0BDE171}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MGU Unified Manager
DefaultGroupName={#MyAppName}
OutputDir=..\..\dist-installer
OutputBaseFilename=MGU-Unified-Manager-Setup-Windows-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\..\dist\MGU Unified Manager\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\MGU Unified Manager"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\MGU Unified Manager"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch MGU Unified Manager"; Flags: postinstall nowait skipifsilent
