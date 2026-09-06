[Setup]
AppName=PANEL Comic Reader
AppVersion=1.2.0
DefaultDirName={autopf}\PANEL Comic Reader
DefaultGroupName=PANEL Comic Reader
OutputBaseFilename=Panel-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\PANEL\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\PANEL Comic Reader"; Filename: "{app}\PANEL.exe"
Name: "{autodesktop}\PANEL Comic Reader"; Filename: "{app}\PANEL.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; Flags: unchecked

[Run]
Filename: "{app}\PANEL.exe"; Description: "Abrir PANEL"; Flags: nowait postinstall skipifsilent
