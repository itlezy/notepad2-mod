[CmdletBinding()]
param(
    [ValidateSet('Build', 'Rebuild', 'Clean')]
    [string]$Target = 'Build',
    [ValidateSet('x86', 'x64', 'All')]
    [string]$Architecture = 'All',
    [ValidateSet('Release', 'Debug')]
    [string]$Configuration = 'Release'
)

$ErrorActionPreference = 'Stop'
$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path -LiteralPath $vswhere)) {
    throw 'Install Visual Studio 2022 or Build Tools with the Desktop development with C++ workload and ATL/MFC.'
}
$installation = & $vswhere -latest -version '[17.0,18.0)' -products '*' -requires Microsoft.Component.MSBuild Microsoft.VisualStudio.Component.VC.Tools.x86.x64 Microsoft.VisualStudio.Component.VC.ATLMFC -property installationPath
if (-not $installation) {
    throw 'Visual Studio 2022 with MSBuild, x86/x64 C++ tools, and ATL/MFC was not found.'
}
$msbuild = Join-Path $installation 'MSBuild\Current\Bin\MSBuild.exe'
$platforms = if ($Architecture -eq 'All') { @('Win32', 'x64') } elseif ($Architecture -eq 'x86') { @('Win32') } else { @('x64') }
foreach ($platform in $platforms) {
    & $msbuild (Join-Path $PSScriptRoot 'Notepad2.sln') /nologo "/t:$Target" "/p:Configuration=$Configuration" "/p:Platform=$platform" /m /v:minimal
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
