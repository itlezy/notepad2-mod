[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Tag,
    [Parameter(Mandatory)][string]$PackageDirectory,
    [switch]$CreateTag
)
$ErrorActionPreference = 'Stop'
function Invoke-Gh([string[]]$Arguments) {
    $result = & gh @Arguments
    if ($LASTEXITCODE -ne 0) { throw "GitHub command failed: $($Arguments[0])" }
    return $result
}
if ($Tag -notmatch '^v(\d+\.\d+\.\d+\.\d+)(-rc\.[1-9]\d*)?$') { throw 'Invalid release tag.' }
$version = $Matches[1]
$prerelease = $Tag.Contains('-rc.')
$tagRef = "refs/tags/$Tag"
if ($CreateTag -and $Tag -notlike '*-rc.1') { throw 'Automatic releases must use an -rc.1 tag.' }
$null = & git merge-base --is-ancestor HEAD origin/master
if ($LASTEXITCODE -ne 0) { throw 'Release commit must belong to master.' }
$commit = & git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Cannot determine the release commit.' }
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
Download the portable ZIP for your architecture and extract it into a writable folder. Preserve your existing Notepad2.ini when upgrading. These binaries are unsigned. SHA256SUMS.txt provides archive integrity checks.

Built from commit $commit as version $version. Release and Debug builds for x86 and x64 passed the native regression suite.
"@ | Set-Content $notes -Encoding utf8

$remoteTags = & git ls-remote --exit-code origin $tagRef "$tagRef^{}"
$tagLookup = $LASTEXITCODE
if ($tagLookup -eq 2 -and $CreateTag) {
    $null = Invoke-Gh @('api','--method','POST',"repos/$env:GH_REPO/git/refs",'-f',"ref=$tagRef",'-f',"sha=$commit")
} elseif ($tagLookup -eq 0) {
    # A matching annotated tag has a second, peeled ref for its target commit.
    $tagCommit = $null
    foreach ($remoteTag in $remoteTags) {
        $object, $ref = $remoteTag -split '\s+', 2
        if ($ref -eq $tagRef) { $tagCommit = $object }
        if ($ref -eq "$tagRef^{}") { $tagCommit = $object; break }
    }
    if ($tagCommit -ne $commit) { throw 'Release tag points to a different commit.' }
} else {
    throw 'Could not find the release tag on origin.'
}

$existing = & gh release view $Tag --json isDraft 2>$null
if ($LASTEXITCODE -eq 0) {
    if (-not ($existing | ConvertFrom-Json).isDraft) {
        if (-not $CreateTag) { throw 'Published releases are immutable; use a new tag.' }
        Write-Output "$Tag is already published."
        return
    }
} else {
    $null = Invoke-Gh @('release','create',$Tag,'--verify-tag','--draft','--title',"Notepad2-mod $Tag",'--generate-notes','--notes-file',$notes)
}
$null = Invoke-Gh (@('release','upload',$Tag) + @($packages) + @($sums,'--clobber'))
$assets = (Invoke-Gh @('release','view',$Tag,'--json','assets') | ConvertFrom-Json).assets
foreach ($path in @($packages) + @($sums)) {
    $asset = @($assets | Where-Object name -eq ([IO.Path]::GetFileName($path)))
    if ($asset.Count -ne 1 -or $asset[0].size -ne (Get-Item $path).Length) { throw 'Release asset verification failed.' }
}
$flags = if ($prerelease) { @('--prerelease','--latest=false') } else { @('--prerelease=false','--latest') }
$null = Invoke-Gh (@('release','edit',$Tag,'--draft=false') + $flags)
Write-Output "Published $Tag"
