from pathlib import Path

root = Path(SPECPATH).parent
a = Analysis([str(root / "installer" / "desktop_entry.py")], pathex=[str(root)],
    binaries=[], datas=[(str(root / "Icons"), "Icons"),
    (str(root / "panellogo.png"), "."), (str(root / "panel.ico"), "."),
    (str(root / "LICENSE"), ".")], hiddenimports=[],
    excludes=["pytest", "panel_backend"], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="PANEL",
          console=False, icon=str(root / "panel.ico"))
coll = COLLECT(exe, a.binaries, a.datas, name="PANEL")
