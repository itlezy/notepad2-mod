[CmdletBinding()]
param(
    [string]$Executable = "$PSScriptRoot/../bin/VS2022/Release_x64/Notepad2.exe",
    [string]$BaselineExecutable
)

$ErrorActionPreference = 'Stop'
Add-Type @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class ThemeTestNative {
    public delegate bool Callback(IntPtr hwnd, IntPtr state);
    [DllImport("user32.dll")] public static extern bool EnumWindows(Callback cb, IntPtr state);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr hwnd, Callback cb, IntPtr state);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr hwnd, StringBuilder text, int size);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hwnd, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hwnd, uint msg, IntPtr w, IntPtr l);
}
'@

function Assert($condition, $message) { if (-not $condition) { throw $message } }
function Sci($message, $w = 0, $l = 0) {
    [ThemeTestNative]::SendMessage($script:editor, $message, [IntPtr]$w, [IntPtr]$l).ToInt64()
}
function Select-Theme($dark) {
    $command = if ($dark) { 40981 } else { 40980 }
    $null = [ThemeTestNative]::SendMessage($script:window, 0x111, [IntPtr]$command, [IntPtr]::Zero)
}
function Start-Editor($ini, $document, $scheme = 'cpp') {
    $script:app = Start-Process -FilePath $Executable -ArgumentList @('/n', '/f', ('"'+$ini+'"'), '/s', $scheme, ('"'+$document+'"')) -WindowStyle Hidden -PassThru
    Assert ($script:app.WaitForInputIdle(10000)) 'Editor startup timed out'
    $script:window = [IntPtr]::Zero
    $script:editor = [IntPtr]::Zero
    $processId = $script:app.Id
    $callback = [ThemeTestNative+Callback]{ param($handle, $state)
        [uint32]$owner = 0
        $null = [ThemeTestNative]::GetWindowThreadProcessId($handle, [ref]$owner)
        $name = New-Object Text.StringBuilder 128
        $null = [ThemeTestNative]::GetClassName($handle, $name, 128)
        if ($owner -eq $processId -and $name.ToString() -like 'Notepad2*') { $script:window = $handle }
        return $true
    }
    $null = [ThemeTestNative]::EnumWindows($callback, [IntPtr]::Zero)
    Assert ($script:window -ne [IntPtr]::Zero) 'Main window missing'
    $child = [ThemeTestNative+Callback]{ param($handle, $state)
        $name = New-Object Text.StringBuilder 128
        $null = [ThemeTestNative]::GetClassName($handle, $name, 128)
        if ($name.ToString() -eq 'Scintilla') { $script:editor = $handle }
        return $true
    }
    $null = [ThemeTestNative]::EnumChildWindows($script:window, $child, [IntPtr]::Zero)
    Assert ($script:editor -ne [IntPtr]::Zero) 'Scintilla window missing'
}
function Stop-Editor {
    $null = Sci 2014
    $null = [ThemeTestNative]::PostMessage($script:window, 0x10, [IntPtr]::Zero, [IntPtr]::Zero)
    Assert ($script:app.WaitForExit(10000)) 'Editor did not exit normally'
}

$Executable = (Resolve-Path $Executable).Path
$testDir = Join-Path ([IO.Path]::GetTempPath()) ('np2-themes-' + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $testDir
$ini = Join-Path $testDir 'settings.ini'
$document = Join-Path $testDir 'sample.cpp'
[IO.File]::WriteAllText($document, "// comment`r`nint main() { return 42; }`r`n")
$settings = "[Settings]`r`nSaveSettings=1`r`n[Default Text]`r`nDefault Style=font:Consolas; size:13; fore:#123456; back:#EEDDCC`r`n"
[IO.File]::WriteAllText($ini, $settings, [Text.Encoding]::Unicode)
try {
    Start-Editor $ini $document
    $original = Sci 2482 32
    $fontSize = Sci 2485 32
    $lexer = Sci 4002
    $null = Sci 2645 0 1 # Create a real undo record, with numeric-only cross-process messages.
    $null = Sci 2160 2 7
    $snapshot = @((Sci 2006), (Sci 2008), (Sci 2009), (Sci 2152), (Sci 2174))
    $timer = [Diagnostics.Stopwatch]::StartNew()
    for ($i = 0; $i -lt 20; ++$i) {
        Select-Theme $true
        Assert ((Sci 2482 32) -eq 0x1E1E1E) 'Dark background not applied'
        Assert ((Sci 2485 32) -eq $fontSize) 'Theme changed font size'
        Select-Theme $false
        Assert ((Sci 2482 32) -eq $original) 'Original custom background lost'
    }
    $timer.Stop()
    Assert ((Sci 4002) -eq $lexer) 'Theme changed lexer'
    $after = @((Sci 2006), (Sci 2008), (Sci 2009), (Sci 2152), (Sci 2174))
    Assert (($snapshot -join ',') -eq ($after -join ',')) 'Theme changed document/selection/viewport/undo state'
    Select-Theme $true
    Stop-Editor
    Start-Editor $ini $document
    Assert ((Sci 2482 32) -eq 0x1E1E1E) 'Theme selection did not persist'
    Select-Theme $false
    Assert ((Sci 2482 32) -eq $original) 'Original settings changed after restart'
    Stop-Editor
    [IO.File]::WriteAllText($ini, $settings.Replace('SaveSettings=1','SaveSettings=0'), [Text.Encoding]::Unicode)
    Start-Editor $ini $document
    Select-Theme $true
    Stop-Editor
    Start-Editor $ini $document
    Assert ((Sci 2482 32) -eq $original) 'Disabled settings saving was ignored'
    Stop-Editor
    # Saved Dark colors are independent; typography embedded in a color section is ignored.
    $custom = $settings + "[Styles]`r`nEditorTheme=1`r`n[Theme.Dark.Default Text]`r`nDefault Style=font:Ignored; size:99; fore:#ABCDEF; back:#222222`r`n"
    [IO.File]::WriteAllText($ini, $custom, [Text.Encoding]::Unicode)
    Start-Editor $ini $document
    Assert ((Sci 2482 32) -eq 0x222222) 'Custom Dark color not loaded'
    Assert ((Sci 2485 32) -eq $fontSize) 'Dark color section changed shared typography'
    Select-Theme $false
    Assert ((Sci 2482 32) -eq $original) 'Dark customization overwrote Original'
    Select-Theme $true
    Assert ((Sci 2482 32) -eq 0x222222) 'Dark customization lost on round trip'
    Stop-Editor
    [IO.File]::WriteAllText($ini, $settings + "[Styles]`r`nEditorTheme=99`r`n", [Text.Encoding]::Unicode)
    Start-Editor $ini $document
    Assert ((Sci 2482 32) -eq $original) 'Unknown theme did not fall back to Original'
    Stop-Editor
    [IO.File]::WriteAllText($ini, $settings + "[Styles]`r`nEditorTheme=1`r`n[Theme.Dark.Default Text]`r`nDefault Style=back:invalid`r`n", [Text.Encoding]::Unicode)
    Start-Editor $ini $document
    Assert ((Sci 2482 32) -eq 0x1E1E1E) 'Invalid saved Dark default did not fall back safely'
    Stop-Editor
    $source = [IO.File]::ReadAllText((Join-Path $PSScriptRoot '../src/Styles.c'))
    $lexers = [regex]::Matches($source, 'EDITLEXER\s+\w+\s*=\s*\{[^\r\n]*?L"([^"]+)",\s*L"([^"]*)"')
    Assert ($lexers.Count -eq 38) 'Lexer coverage inventory changed'
    foreach ($entry in $lexers) {
        [IO.File]::WriteAllText($ini, $settings, [Text.Encoding]::Unicode)
        $scheme = $entry.Groups[2].Value.Split(';')[0].Trim()
        Start-Editor $ini $document $scheme
        Select-Theme $true
        Assert ((Sci 2482 32) -eq 0x1E1E1E) "Dark background failed for $scheme"
        Select-Theme $false
        Stop-Editor
    }
    Write-Output "Theme integration passed. 40 switches: $($timer.ElapsedMilliseconds) ms. Fixtures: $testDir"
    if ($BaselineExecutable) {
        $currentExecutable = $Executable
        foreach ($mode in @('Baseline', 'Original', 'Dark')) {
            $Executable = if ($mode -eq 'Baseline') { (Resolve-Path $BaselineExecutable).Path } else { $currentExecutable }
            $samples = for ($run = 0; $run -lt 7; ++$run) {
                $theme = if ($mode -eq 'Dark') { 1 } else { 0 }
                [IO.File]::WriteAllText($ini, $settings + "[Styles]`r`nEditorTheme=$theme`r`n", [Text.Encoding]::Unicode)
                $startup = [Diagnostics.Stopwatch]::StartNew()
                Start-Editor $ini $document
                $startup.Stop()
                $script:app.Refresh()
                $privateBytes = $script:app.PrivateMemorySize64
                $editing = [Diagnostics.Stopwatch]::StartNew()
                for ($op = 0; $op -lt 100; ++$op) { $null = Sci 2645 0 1; $null = Sci 2176 }
                $editing.Stop()
                $cpuBefore = $script:app.TotalProcessorTime.TotalMilliseconds
                Start-Sleep -Milliseconds 200
                $script:app.Refresh()
                $idle = $script:app.TotalProcessorTime.TotalMilliseconds - $cpuBefore
                Stop-Editor
                [pscustomobject]@{ StartupMs=$startup.Elapsed.TotalMilliseconds; PrivateKiB=$privateBytes/1024; Edit100Ms=$editing.Elapsed.TotalMilliseconds; Idle200Ms=$idle }
            }
            $median = [ordered]@{ Mode=$mode }
            foreach ($metric in @('StartupMs','PrivateKiB','Edit100Ms','Idle200Ms')) {
                $median[$metric] = [Math]::Round(($samples.$metric | Sort-Object)[3], 2)
            }
            [pscustomobject]$median
        }
    }
} finally {
    if ($script:app -and -not $script:app.HasExited) { Stop-Process -Id $script:app.Id }
}
