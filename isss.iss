; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "IIQtoJPG Converter"
#define MyAppVersion "0.1"
#define MyAppPublisher "Frederik Skoumann"
#define MyAppURL "https://www.frederik.site/"
#define MyAppExeName "ImageConverter.exe"  ; Updated executable name
#define SourceDir "C:\Users\fhe\coding\newdumdum\v2\dist\ImageConverter"
#define InstallerIcon "C:\Users\fhe\coding\newdumdum\v2\256 Logo.ico"
#define WizardImage "C:\Users\fhe\coding\newdumdum\v2\1024 logo.bmp"
#define WizardSmallImage "C:\Users\fhe\coding\newdumdum\v2\256 Logo.bmp"

[Setup]
AppId={{56D7AF8B-4FEC-4B94-9600-EF716FB1828A}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
OutputBaseFilename=IIQtoJPG_Converter_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile={#InstallerIcon}
WizardImageFile={#WizardImage}
WizardSmallImageFile={#WizardSmallImage}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
