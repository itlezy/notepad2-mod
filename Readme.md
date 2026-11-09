# Notepad2-mod

> *A modified version (fork) of Notepad2 based on Kai Liu's and other people's patches.*

This fork is maintained by [itlezy](https://github.com/itlezy) at
[itlezy/notepad2-mod](https://github.com/itlezy/notepad2-mod), with a focus on small,
practical improvements to the original editor.

The upstream repository, [XhmikosR/notepad2-mod](https://github.com/XhmikosR/notepad2-mod),
is archived and was last updated in July 2018. Ongoing maintenance for this fork
happens here; upstream history, licensing, and contributor credits are preserved.

The initial fork setup changes documentation only. Easy light/dark switching and
Notepad++ XML theme imports are planned features, not implemented additions.
See the [roadmap](ROADMAP.md) and [contributor guide](CONTRIBUTING.md).

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

This is the inherited upstream support list, not a newly verified compatibility
matrix for this fork.

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

The inherited build uses Visual Studio 2017 with C++ desktop tools, ATL/MFC, and
the `v141_xp` platform toolset (including its required SDK components). Open
`build/Notepad2.sln`, or run this command from the repository root in Command Prompt:

```bat
build\build_vs2017.bat Build All Release
```

This requests Release builds for both Win32 and x64. The wrapper uses `vswhere`
to locate Visual Studio; the selected installation must contain the required
legacy toolset. Installing a newer Visual Studio alone does not retarget the projects.

These instructions describe the checked-in build configuration. No application
build or runtime validation was performed for the initial documentation setup.
Build modernization, GitHub Actions, and fork releases are future milestones.
