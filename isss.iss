; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "IIQtoJPG Converter v0.3"
#define MyAppVersion "0.3"
#define MyAppPublisher "Frederik Skoumann"
#define MyAppURL "https://www.frederik.site/"
#define MyAppExeName "ImageConverter.exe"  ; Updated executable name
#define SourceDir "C:\Users\fhe\coding\IIQtoJPG\dist\ImageConverter"
#define InstallerIcon "C:\Users\fhe\coding\IIQtoJPG\logo.ico"
#define WizardImage "C:\Users\fhe\coding\IIQtoJPG\biglogo.bmp"
#define WizardSmallImage "C:\Users\fhe\coding\IIQtoJPG\biglogo.bmp"


C:\Users\fhe\coding\IIQtoJPG\net6.0\dest\dotnet-sdk-8.0.403-win-x64.exe

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
OutputBaseFilename=IIQtoJPG_Converter_Setup_v3
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
; Include the .NET Runtime installer from the dest folder
Source: "C:\Users\fhe\coding\IIQtoJPG\net6.0\dest\dotnet-sdk-8.0.403-win-x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Check if the .NET Runtime is installed and run the installer if it's missing
Filename: "{tmp}\dotnet-sdk-8.0.403-win-x64.exe"; Parameters: "/quiet /norestart"; \
    Check: NeedsDotNetRuntime; StatusMsg: "Installing .NET Desktop Runtime..."
; Launch your application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsDotNetRuntime: Boolean;
var
  Success: Boolean;
  DotNetVersion: Cardinal;
begin
  Success := RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{Insert GUID for the runtime here}', 'Version', DotNetVersion);
  { For example, check for .NET 6 runtime (60000 and up), modify based on the runtime you're using }
  Result := not Success or (DotNetVersion < 60000);
end;
