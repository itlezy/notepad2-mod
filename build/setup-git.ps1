[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
    $settings = [ordered]@{
        'core.autocrlf' = 'false'
        'core.safecrlf' = 'true'
        'core.whitespace' = 'blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol'
        'core.hooksPath' = '.githooks'
        'pull.ff' = 'only'
        'pull.rebase' = 'false'
        'push.default' = 'simple'
        'push.autoSetupRemote' = 'false'
        'fetch.prune' = 'true'
    }
    foreach ($entry in $settings.GetEnumerator()) {
        & git config --local $entry.Key $entry.Value
        if ($LASTEXITCODE -ne 0) { throw "Could not set $($entry.Key)." }
    }
    Write-Output 'Repository-local Git settings and pre-commit hook installed. Author identity is unchanged.'
} finally {
    Pop-Location
}
