; installer.nsi
!include "MUI2.nsh"
!define MUI_ICON "assets\installer.ico"
!define MUI_UNICON "assets\uninstaller.ico"


Name "Folder Replicator"
OutFile "FolderReplicator_Setup.exe"
InstallDir "$PROGRAMFILES\FolderReplicator"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\FolderReplicator\*.*"
    
    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\Folder Replicator"
    CreateShortcut "$SMPROGRAMS\Folder Replicator\Folder Replicator.lnk" "$INSTDIR\FolderReplicator.exe"
    
    ; Add to PATH
    EnVar::SetHKCU
    EnVar::AddValue "PATH" "$INSTDIR"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FolderReplicator" \
        "DisplayName" "Folder Replicator"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FolderReplicator" \
        "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    
    SetOutPath $INSTDIR
    File "assets\icon.ico"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\*.*"
    RMDir "$INSTDIR"
    Delete "$SMPROGRAMS\Folder Replicator\*.*"
    RMDir "$SMPROGRAMS\Folder Replicator"
    
    ; Remove from PATH
    EnVar::SetHKCU
    EnVar::DeleteValue "PATH" "$INSTDIR"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FolderReplicator"
SectionEnd