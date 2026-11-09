[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
    & git diff --cached --ignore-cr-at-eol --check
    if ($LASTEXITCODE -ne 0) { throw 'Staged whitespace errors must be fixed.' }

    # NUL-delimited paths handle spaces and Unicode without Git quoting.
    $start = New-Object Diagnostics.ProcessStartInfo
    $start.FileName = 'git'
    $start.WorkingDirectory = (Get-Location).ProviderPath
    $start.Arguments = 'diff --cached --name-only --diff-filter=ACMR -z'
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.StandardOutputEncoding = [Text.Encoding]::UTF8
    $process = [Diagnostics.Process]::Start($start)
    $paths = $process.StandardOutput.ReadToEnd().Split([char]0)
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { throw 'Could not inspect the Git index.' }
    $process.Dispose()
    foreach ($path in $paths) {
        if (-not $path) { continue }
        if ($path -match '(?i)(^|/)(bin|obj|\.vs|\.cache|__pycache__)/|(^|/)(build\.user\.bat|signinfo\.txt|VersionRev\.h|Notepad2\.exe\.manifest)$|\.(exe|dll|lib|obj|pdb|ilk|pch|aps|suo|user|sdf|opensdf|pyc|pfx|p12|key|pem|log)$|(^|/)\.env($|\.)') {
            throw "Generated or private file is staged: $path"
        }
    }
    Write-Output 'Staged checks passed.'
} finally {
    Pop-Location
}
