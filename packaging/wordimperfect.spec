# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for the WordImperfect desktop application."""

from __future__ import annotations

import pathlib

from PyInstaller.utils.hooks import collect_submodules

project_root = pathlib.Path(__file__).resolve().parent.parent
assets_path = project_root / "assets"

a = Analysis(
    [project_root / "src" / "wordimperfect" / "__main__.py"],
    pathex=[project_root / "src"],
    binaries=[],
    datas=[(str(assets_path), "assets")] if assets_path.exists() else [],
    hiddenimports=collect_submodules("wordimperfect"),
    hookspath=[],
    hooksconfig={},
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="wordimperfect",
    console=False,
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wordimperfect",
)
