#!/usr/bin/env python3
import os
from pathlib import Path
import tomllib
import PyInstaller.__main__
from datetime import date
import shutil

sep = os.pathsep

def build_version_file():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)

    version = data["project"]["version"]
    name = data["project"]["name"]
    description = data["project"]["description"]
    nums = tuple(int(x) for x in version.split(".")) + (0,) * (4 - len(version.split(".")))

    TEMPLATE = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={nums},
    prodvers={nums},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'BlazeMeter'),
        StringStruct('FileDescription', '{description}'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', '{name}'),
        StringStruct('LegalCopyright', '© {date.today().year} BlazeMeter'),
        StringStruct('OriginalFilename', '{name}.exe'),
        StringStruct('ProductName', 'BlazeMeter MCP'),
        StringStruct('ProductVersion', '{version}')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(TEMPLATE.strip())

def build():
    entry_point = Path(__file__).parent / "main.py"
    name = "bzm-mcp-linux"

    # Clean old builds
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)

    # **Important**: point PyInstaller to project root, not vs_mcp
    project_root = Path(__file__).parent.parent

    PyInstaller.__main__.run([
        str(entry_point),
        '--onefile',
        '--version-file=version_info.txt',
        f'--add-data={project_root / "pyproject.toml"}{sep}.',
        f'--paths={project_root}',  # <-- root folder
        f'--name={name}',
        '--clean',
        '--noconfirm',
    ])

if __name__ == "__main__":
    build_version_file()
    build()
