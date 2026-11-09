[CmdletBinding()]
param([Parameter(Mandatory)][string]$Tag, [Parameter(Mandatory)][string]$PackageDirectory)
$ErrorActionPreference = 'Stop'
function Invoke-Gh([string[]]$Arguments) {
    $result = & gh @Arguments
    if ($LASTEXITCODE -ne 0) { throw "GitHub command failed: $($Arguments[0])" }
    return $result
}
if ($Tag -notmatch '^v(\d+\.\d+\.\d+\.\d+)(-rc\.[1-9]\d*)?$') { throw 'Invalid release tag.' }
$version = $Matches[1]
$prerelease = $Tag.Contains('-rc.')
$null = & git merge-base --is-ancestor HEAD origin/master
if ($LASTEXITCODE -ne 0) { throw 'Release commit must belong to master.' }
$commit = & git rev-parse HEAD
Add-Type -AssemblyName System.IO.Compression.FileSystem
$packages = foreach ($arch in @('x86','x64')) {
    $path = (Resolve-Path (Join-Path $PackageDirectory "Notepad2-mod-$Tag-$arch.zip")).Path
    $archive = [IO.Compression.ZipFile]::OpenRead($path)
    try {
        $reader = [IO.StreamReader]::new($archive.GetEntry('build-info.json').Open())
        try { $info = $reader.ReadToEnd() | ConvertFrom-Json } finally { $reader.Dispose() }
        if ($info.commit -ne $commit -or $info.version -ne $version -or $info.architecture -ne $arch -or $info.tag -ne $Tag) {
            throw "Package metadata mismatch: $arch"
        }
    } finally { $archive.Dispose() }
    $path
}
$sums = Join-Path $PackageDirectory 'SHA256SUMS.txt'
$packages | ForEach-Object { '{0}  {1}' -f (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant(), [IO.Path]::GetFileName($_) } | Set-Content $sums -Encoding ascii
$notes = Join-Path $PackageDirectory 'release-notes.txt'
@"
Native Original/Dark editor palettes on Scintilla 3.7.6, with a VS 2022 build.

Focused corrections protect nonempty untitled documents during save prompting, skip empty recent-file slots, make application source encoding deterministic, and honor elevated-launch show-state flags.

With no selection, Ctrl+C / Ctrl+Insert copy the current line and Ctrl+X / Shift+Delete cut it. Ctrl+V / Shift+Insert paste line-marked clipboard content above the current line. Normal selected-text behavior is retained.

Choose View > Editor Theme > Dark. Existing Original colors and font preferences are retained. Application chrome is unchanged.

Download the portable ZIP for your architecture and extract it into a writable folder. Preserve your existing Notepad2.ini when upgrading. These binaries are unsigned. SHA256SUMS.txt provides archive integrity checks.

Source commit: $commit
Executable version: $version
Validation: Release/Debug x86/x64 builds with pytest and pywinauto, including all 38 schemes, customization/persistence, save-prompt data preservation, line shortcuts, and native helper contracts. Actual standard-user UAC interaction remains a manual check.
"@ | Set-Content $notes -Encoding utf8
$existing = & gh release view $Tag --json isDraft 2>$null
if ($LASTEXITCODE -eq 0) {
    if (-not ($existing | ConvertFrom-Json).isDraft) { throw 'Published releases are immutable; use a new tag.' }
} else {
    $null = Invoke-Gh @('release','create',$Tag,'--verify-tag','--draft','--title',"Notepad2-mod $Tag",'--notes-file',$notes)
}
$null = Invoke-Gh (@('release','upload',$Tag) + @($packages) + @($sums,'--clobber'))
$assets = (Invoke-Gh @('release','view',$Tag,'--json','assets') | ConvertFrom-Json).assets
foreach ($path in @($packages) + @($sums)) {
    $asset = @($assets | Where-Object name -eq ([IO.Path]::GetFileName($path)))
    if ($asset.Count -ne 1 -or $asset[0].size -ne (Get-Item $path).Length) { throw 'Release asset verification failed.' }
}
$flags = if ($prerelease) { @('--prerelease','--latest=false') } else { @('--prerelease=false','--latest') }
$null = Invoke-Gh (@('release','edit',$Tag,'--draft=false','--notes-file',$notes) + $flags)
Write-Output "Published $Tag"
