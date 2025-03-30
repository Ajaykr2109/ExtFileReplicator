# version_info.py
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904b0',
                [
                    StringStruct('CompanyName', 'ZtrlCorp'),
                    StringStruct('FileDescription', 'Folder Replicator'),
                    StringStruct('FileVersion', '1.0.0.0'),
                    StringStruct('InternalName', 'FolderReplicator'),
                    StringStruct('LegalCopyright',
                                 'Copyright © 2023 ZtrlCorp'),
                    StringStruct('OriginalFilename', 'FolderReplicator.exe'),
                    StringStruct('ProductName', 'Folder Replicator'),
                    StringStruct('ProductVersion', '1.0.0.0')
                ])
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)
