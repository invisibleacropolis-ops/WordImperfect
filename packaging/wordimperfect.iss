; Inno Setup script for packaging the WordImperfect desktop application.
; This installer consumes the PyInstaller output located in dist/wordimperfect
; and produces a per-user installer with shortcuts and metadata.

#define AppVersion GetString(GetScriptParam("AppVersion"), "0.0.0")
#define DistDir GetString(GetScriptParam("DistDir"), "dist\\wordimperfect")
#define OutputBaseName GetString(GetScriptParam("OutputBaseName"), "wordimperfect-windows-setup")
#define Publisher "WordImperfect Team"
#define ProjectURL "https://github.com/WordImperfect/WordImperfect"

[Setup]
AppId={{B6E8A2A4-8A8A-4F89-9E66-345A674A7EAF}}
AppName=WordImperfect
AppVersion={#AppVersion}
AppVerName=WordImperfect {#AppVersion}
AppPublisher={#Publisher}
AppPublisherURL={#ProjectURL}
AppSupportURL={#ProjectURL}
AppUpdatesURL={#ProjectURL}
DefaultDirName={userappdata}\WordImperfect
DefaultGroupName=WordImperfect
DisableDirPage=yes
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename={#OutputBaseName}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\wordimperfect.exe
WizardStyle=modern
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#DistDir}\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\WordImperfect"; Filename: "{app}\wordimperfect.exe"; WorkingDir: "{app}"
Name: "{userdesktop}\WordImperfect"; Filename: "{app}\wordimperfect.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\wordimperfect.exe"; Description: "Launch WordImperfect"; Flags: nowait postinstall skipifsilent
