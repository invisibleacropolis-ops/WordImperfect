# WordImperfect MSI packaging

This folder contains the WiX Toolset assets needed to build a Windows Installer (`.msi`) package for the PyInstaller
distribution of WordImperfect.

## Prerequisites

- Windows 10 or later
- Python 3.11+ with the project dependencies installed
- [WiX Toolset 4 CLI](https://wixtoolset.org/docs/tools/wix.exe/) `wix` command on `PATH`
  ```powershell
  dotnet tool install --global wix
  ```

## Build steps

1. Produce the PyInstaller payload:
   ```powershell
   python -m pip install -e .[release]
   pyinstaller packaging/wordimperfect.spec
   ```
   The bundled application will be written to `dist\wordimperfect\`.

2. Create the MSI:
   ```powershell
   pwsh -File packaging/msi/build.ps1
   ```
   - Override the PyInstaller output with `-DistPath` if you have a non-default location.
   - Override the version embedded in the MSI with `-Version 0.1.0` (defaults to the value in `pyproject.toml`).

3. The resulting installer is saved as `packaging\msi\WordImperfect-<version>.msi`.

## What the script does

`build.ps1` orchestrates the following:

- Harvests files from the PyInstaller directory using `wix heat`, generating `WordImperfectComponents.wxi` (ignored by git).
- Builds `WordImperfect.wxs` into a per-machine, x64 MSI that installs into `%ProgramFiles%\WordImperfect\`.
- Creates a Start Menu shortcut and registers an Add/Remove Programs entry that uses the bundled executable's icon.

Re-run the script after each new PyInstaller build so the harvested component list stays in sync with the packaged files.
