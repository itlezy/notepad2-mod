[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('x86','x64')][string]$Architecture,
    [string]$Tag,
    [string]$OutputDirectory = "$PSScriptRoot/../bin/packages"
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path "$PSScriptRoot/..").Path
$exe = Join-Path $repo "bin/VS2022/Release_$Architecture/Notepad2.exe"
$version = (Get-Item -LiteralPath $exe).VersionInfo.FileVersion.Trim()
if (-not $Tag) { $Tag = "v$version" }
if ($Tag -notmatch '^v(\d+\.\d+\.\d+\.\d+)(-rc\.[1-9]\d*)?$' -or $Matches[1] -ne $version) {
    throw "Release tag must match executable version $version (optional -rc.N suffix)."
}
$stream = [IO.File]::OpenRead($exe)
$reader = [IO.BinaryReader]::new($stream)
try {
    $stream.Position = 0x3C
    $pe = $reader.ReadInt32()
    $stream.Position = $pe + 4
    $machine = $reader.ReadUInt16()
    $expected = if ($Architecture -eq 'x64') { 0x8664 } else { 0x14C }
    if ($machine -ne $expected) { throw 'Executable architecture mismatch.' }
} finally { $reader.Dispose() }
$null = New-Item -ItemType Directory -Path $OutputDirectory -Force
$output = (Resolve-Path $OutputDirectory).Path
$stage = Join-Path $output ([Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $stage
Copy-Item -LiteralPath $exe -Destination "$stage/Notepad2.exe"
foreach ($name in @('License.txt','Readme.md','Notepad2.txt','Readme-mod.txt')) {
    Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $stage
}
Copy-Item -LiteralPath "$repo/distrib/Notepad2.ini" -Destination $stage
Copy-Item -LiteralPath "$repo/scintilla/License.txt" -Destination "$stage/Scintilla-License.txt"
$commit = & git -C $repo rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot determine source commit.' }
$metadata = [ordered]@{ version=$version; tag=$Tag; architecture=$Architecture; commit=$commit; executableSHA256=(Get-FileHash $exe -Algorithm SHA256).Hash; signed=$false }
$metadata | ConvertTo-Json | Set-Content "$stage/build-info.json" -Encoding utf8
$zipPath = Join-Path $output "Notepad2-mod-$Tag-$Architecture.zip"
if (Test-Path -LiteralPath $zipPath) { throw "Package already exists: $zipPath" }
Compress-Archive -Path "$stage/*" -DestinationPath $zipPath
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $expectedFiles = @('Notepad2.exe','Notepad2.ini','License.txt','Scintilla-License.txt','Readme.md','Notepad2.txt','Readme-mod.txt','build-info.json') | Sort-Object
    if (Compare-Object $expectedFiles @($archive.Entries.FullName | Sort-Object)) { throw 'Unexpected archive contents.' }
    $entry = $archive.GetEntry('Notepad2.exe').Open()
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $actualHash = [BitConverter]::ToString($sha.ComputeHash($entry)).Replace('-','') }
    finally { $entry.Dispose(); $sha.Dispose() }
    if ($actualHash -ne $metadata.executableSHA256) { throw 'Packaged executable hash mismatch.' }
} finally { $archive.Dispose() }
# Keep the staging directory as an ignored build artifact; never delete computed trees.
Write-Output $zipPath
