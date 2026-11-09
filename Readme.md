# Notepad2-mod

> *A modified version (fork) of Notepad2 based on Kai Liu's and other people's patches.*

This fork is maintained by [itlezy](https://github.com/itlezy) at
[itlezy/notepad2-mod](https://github.com/itlezy/notepad2-mod), with a focus on small,
practical improvements to the original editor.

The upstream repository, [XhmikosR/notepad2-mod](https://github.com/XhmikosR/notepad2-mod),
is archived and was last updated in July 2018. Ongoing maintenance for this fork
happens here; upstream history, licensing, and contributor credits are preserved.

This fork now builds with Visual Studio 2022. Easy light/dark switching and
Notepad++ XML theme imports are planned features, not implemented additions.
See the [roadmap](ROADMAP.md) and [contributor guide](CONTRIBUTING.md).

The bundled editor engine is Scintilla 3.7.6 (LongTerm3), with the original
Notepad2-mod customizations preserved. See its
[vendor notes](scintilla/README.notepad2-mod.txt) for the source and local changes.

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
GitHub Actions and fork releases remain future work.
