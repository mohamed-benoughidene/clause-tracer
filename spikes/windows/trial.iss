; Throwaway Inno Setup script for the Windows packaging spike.
; Builds a minimal installer around the PyInstaller one-folder build of
; trial_app.py, so the spike can test a real silent install/uninstall
; instead of just running the frozen build from its folder.
;
; SourceDir points at the repo root (two levels up from this script) because
; the PyInstaller build step runs from the repo root and produces dist\trial.

#define MyAppName "Clause Tracer Trial"
#define MyAppVersion "0.1.0"
#define MyAppExeName "trial.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Clause Tracer packaging spike (throwaway)
DefaultDirName={autopf}\ClauseTracerTrial
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableWelcomePage=yes
PrivilegesRequired=lowest
SourceDir=..\..
OutputDir=spikes\windows\installer_output
OutputBaseFilename=ClauseTracerTrialSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\trial\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
