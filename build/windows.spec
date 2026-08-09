# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPEC).resolve().parent.parent

hiddenimports = collect_submodules("ttkbootstrap")
hiddenimports += collect_submodules("sqlalchemy")

# PyInstaller bundles the logo and other runtime assets. The workflow creates
# the ICO from the canonical SVG before invoking PyInstaller.
datas = [
    (str(ROOT / "assets"), "assets"),
]

analysis = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="HamzaouiFacturation",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "assets" / "hamzaoui_logo.ico"),
)
