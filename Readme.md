# Notepad2-mod

> *A modified version (fork) of Notepad2 based on Kai Liu's and other people's patches.*

This fork is maintained by [itlezy](https://github.com/itlezy) at
[itlezy/notepad2-mod](https://github.com/itlezy/notepad2-mod), with a focus on small,
practical improvements to the original editor.

The product direction is to stay close to Notepad2-mod: fast startup, responsive
editing, a small footprint, and simple native Windows behavior. Changes should be
minimal, focused patches with a clear benefit. This fork will not move to
Notepad3/Notepad4 or adopt their feature stacks; matching newer editors or
dependency versions is not a goal.

The upstream repository, [XhmikosR/notepad2-mod](https://github.com/XhmikosR/notepad2-mod),
is archived and was last updated in July 2018. Ongoing maintenance for this fork
happens here; upstream history, licensing, and contributor credits are preserved.

This fork builds with Visual Studio 2022 and includes native Original/Dark editor
palettes. Choose **View > Editor Theme > Original / Dark**. Original preserves
existing custom colors; Dark supplies syntax and editor colors across all 38 schemes.
Theme work covers the editor only; application chrome is out of scope.
See the [roadmap](ROADMAP.md) and [contributor guide](CONTRIBUTING.md).

The bundled editor engine is Scintilla 3.7.6 (LongTerm3), with the original
Notepad2-mod customizations preserved. See its
[vendor notes](scintilla/README.notepad2-mod.txt) for the source and local changes.

Customize the active palette using **View > Customize Schemes**. Colors are kept
separately for Original and Dark; fonts and other non-color preferences remain
shared. Preview, Cancel, and Reset work with the active palette. The existing
second-default scheme toggle remains independent. Theme selection follows the
existing Save Settings preference; explicit Save Settings also saves it.

There are no external theme files or automatic system-theme synchronization.
Scintilla's native autocomplete list and the existing bookmark pixmap retain
their original appearance. Scheme import/export remains an explicit full-scheme
operation, including file associations; it is not used to switch themes.

## Changes compared to the official Notepad2:

* Code folding
* Support for bookmarks
* Option to mark all occurrences of a word
* Word auto-completion
* Syntax highlighting support for AutoHotkey, AutoIt3, AviSynth, Bash, CMake, CoffeeScript,
  Inno Setup, LaTeX, Lua, Markdown, NSIS, Ruby, Tcl, YAML and VHDL scripts
* Improved support for NFO ANSI art
* Support for replacing Windows Notepad using a clean, unintrusive registry-based method
* Other various minor changes and tweaks

## Upstream Operating System Support:

* XP (SP3, SP2 might or might not work), Vista, 7, 8, 8.1 and 10 both 32-bit and 64-bit

This is the historical upstream support list. Current fork builds target Windows
10/11 using the modern MSVC toolset; XP compatibility is no longer a build goal.
Compatibility with other Windows versions has not been verified.

## [Screenshots](https://xhmikosr.github.io/notepad2-mod/screenshots)

## Notes:

* Report bugs and propose focused improvements in
  [this fork](https://github.com/itlezy/notepad2-mod/issues).
* Read the [contributor guide](CONTRIBUTING.md) before submitting changes.

## Contributors:

* [Kai Liu](http://code.kliu.org/misc/notepad2/)
* [RL Vision](http://www.rlvision.com/notepad2/about.asp)
* Aleksandar Lekov
* Bruno Barbieri
* Everyone else on [GitHub](https://github.com/XhmikosR/notepad2-mod/graphs/contributors)

## More information:

* [Official Notepad2 website](http://www.flos-freeware.ch/notepad2.html)
* [Code folding usage guide](https://github.com/XhmikosR/notepad2-mod/wiki/Code-Folding-Usage)

## Changed keyboard shortcuts compared to Notepad2:

* <kbd>Ctrl+Alt+F2</kbd>       Expand selection to next match.
* <kbd>Ctrl+Alt+Shift+F2</kbd> Expand selection to previous match.
* <kbd>Ctrl+Shift+Enter</kbd>  New line with toggled auto indent option.

## Building

Install Visual Studio 2022 (or its Build Tools) with Desktop development with C++,
MSVC v143 x86/x64 tools, C++ ATL/MFC, and a Windows 10/11 SDK. Install Git for
Windows as well; revision generation uses its Bash and Git executables.

From the repository root in PowerShell:

```powershell
.\build\build.ps1
```

The default builds Release for both x86 and x64. To build and run only x64:

```powershell
.\build\build.ps1 -Architecture x64
.\bin\VS2022\Release_x64\Notepad2.exe
```

Use `-Configuration Debug` for Debug builds and `-Target Rebuild` or `-Target Clean`
as needed. Outputs are in `bin/VS2022/Release_x86`, `Release_x64`, `Debug_x86`,
and `Debug_x64`. No Developer PowerShell session is required: the script finds
MSBuild using `vswhere`. Alternatively, open `build/Notepad2.sln` in VS 2022 and
select Release/Debug and Win32/x64. The projects select the latest installed
Windows 10/11 SDK via `WindowsTargetPlatformVersion=10.0`.

Release and Debug builds for x86 and x64 have been verified locally with Visual
Studio 2022 17.14, MSVC 14.44, and Windows SDK 10.0.26100.0. Legacy packaging and
signing scripts are separate from this build command and have not been validated.
GitHub Actions builds and tests Release/Debug x86/x64 on Windows Server 2022.
Successful runs retain executable artifacts and portable Release ZIPs for 14 days;
failure logs are uploaded as well. Download published portable builds from
[Releases](https://github.com/itlezy/notepad2-mod/releases). Initial testing builds
are marked as prereleases. Binaries are unsigned.

Portable archives contain the executable, a default INI, usage documentation,
licenses, and source/version metadata. Extract into a writable directory. When
upgrading an existing installation, preserve its INI and redirected user settings.
Release setup does not change system-wide Notepad replacement or file associations.

## Publishing a release

Merge validated changes into `master` with granular history preserved, wait for
master CI to pass, and build that exact clean commit to obtain its file version:

```powershell
.\build\build.ps1
$releaseVersion = (Get-Item .\bin\VS2022\Release_x64\Notepad2.exe).VersionInfo.FileVersion.Trim()
git tag "v$releaseVersion-rc.1"
git push origin "v$releaseVersion-rc.1"
```

Stable tags omit `-rc.N`. Tags use the existing four-part file version; full Git
history determines its final revision component. The workflow checks both binary
versions against the tag, tests all four configurations, then publishes x86/x64
ZIPs and SHA256SUMS.txt. A prerelease does not replace the latest stable release.

Only the publishing job has repository write permission, using GITHUB_TOKEN.
There are no signing secrets or installer dependencies. Published release assets
must not be overwritten: use a new tag/commit for corrections. If publishing fails
after creating a draft, inspect its logs and rerun the failed job on the same tag;
draft assets are replaceable until publication. Never move an existing release tag.

The packaging command is `./build/package.ps1 -Architecture x64` (or `x86`). It
uses Release output and writes into ignored `bin/packages`; supply a fresh
`-OutputDirectory` when repackaging an already-created version locally.

Tests use Python 3.13, pytest, and pywinauto's Win32 backend. Test dependencies
are locked with hashes and are not application dependencies. PowerShell is used
for building, not UI automation. To test a built executable:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r tests/requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest --executable .\bin\VS2022\Release_x86\Notepad2.exe --architecture x86
```

The checks launch isolated instances with temporary settings, exercise all 38
schemes and customization Preview/Cancel/Reset, and verify palette/font separation,
switching, restart persistence, invalid defaults, and disabled settings saving.
They also exercise save prompts with embedded NUL/whitespace, exact-byte Cancel
preservation, production MRU functions, source charset, and startup show-state
contracts. The latter do not replace an interactive standard-user UAC test.
Use `--configuration Debug` for the corresponding native helper runtime. A
pre-fix binary can be checked with `-m pytest tests/test_save_prompts.py
--legacy-save-behavior --executable <path>` to reproduce the nine loss paths.
These tests do not replace visual review or establish large-file performance.
