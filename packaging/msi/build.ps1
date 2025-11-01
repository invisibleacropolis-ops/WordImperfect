param(
    [string]$DistPath,
    [string]$Version
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptRoot '..\..')

if (-not $DistPath) {
    $DistPath = Join-Path $projectRoot 'dist\wordimperfect'
}

if (-not (Test-Path $DistPath)) {
    throw "PyInstaller output not found at '$DistPath'. Run `python -m pip install -e .[release]` followed by `pyinstaller packaging/wordimperfect.spec` first."
}

if (-not $Version) {
    $pyprojectPath = Join-Path $projectRoot 'pyproject.toml'
    if (-not (Test-Path $pyprojectPath)) {
        throw "Unable to locate pyproject.toml at '$pyprojectPath'. Specify -Version explicitly."
    }

    $versionMatch = Select-String -Path $pyprojectPath -Pattern '^\s*version\s*=\s*"([^"]+)"' | Select-Object -First 1
    if (-not $versionMatch) {
        throw "Unable to determine project version from pyproject.toml. Specify -Version explicitly."
    }

    $Version = $versionMatch.Matches[0].Groups[1].Value
}

$wixCli = Get-Command wix -ErrorAction SilentlyContinue
if (-not $wixCli) {
    throw "WiX Toolset CLI (wix) not found on PATH. Install it via `dotnet tool install --global wix`."
}

$componentFile = Join-Path $scriptRoot 'WordImperfectComponents.wxi'
$wxsPath = Join-Path $scriptRoot 'WordImperfect.wxs'

Write-Host "Harvesting PyInstaller payload from '$DistPath'..."

& $wixCli.Source heat dir $DistPath `
    -o $componentFile `
    -cg WordImperfectComponents `
    -dr INSTALLFOLDER `
    -srd `
    -gg `
    -var var.WORDIMPERFECT_DIST

if (-not (Test-Path $componentFile)) {
    throw "Failed to generate $componentFile. Inspect WiX harvest output for details."
}

$outputName = "WordImperfect-$Version.msi"
$outputPath = Join-Path $scriptRoot $outputName

Write-Host "Building MSI => $outputPath"

& $wixCli.Source build $wxsPath `
    -ext WixToolset.Util.wixext `
    -ext WixToolset.UI.wixext `
    -d ProductVersion=$Version `
    -d WORDIMPERFECT_DIST=$DistPath `
    -out $outputPath

Write-Host "MSI created at $outputPath"
