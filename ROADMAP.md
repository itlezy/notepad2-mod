# Maintenance roadmap

This fork preserves the original Notepad2-mod editor while adding small, practical
improvements. The original upstream is archived and was last updated in July 2018;
ongoing maintenance is the responsibility of this fork.

## Initial setup

The initial documentation-only setup established `itlezy/notepad2-mod`, retained
upstream history and attribution, and added contribution guidance. Build/tooling
and the Scintilla 3.7.6 update followed in separate commits.

## Build modernization and automation

Local build modernization is complete: both projects use Visual Studio 2022 /
`v143`, with a PowerShell build entrypoint and Windows 10/11 as the target baseline.
Release and Debug builds for x86 and x64 have been verified locally. XP toolset
support is retired. Next, add GitHub Actions for Win32 and x64 builds and modernize
the legacy packaging/signing scripts, followed by versioned, downloadable releases
after runtime validation.

## Easy light/dark switching

Track implementation in [#6: native Light/Dark editor themes](https://github.com/itlezy/notepad2-mod/issues/6).
Start with complete global/editor and language palettes on Scintilla 3.7.6, using
the existing native style model. Preserve language selection, font preferences,
file associations, document contents, selection, and undo history. Persist the
theme and validate repeated switching, restart, and readable highlights.

Whole-application dark mode is a separate follow-up covering menus, dialogs,
toolbar, status bar, title bar, and scrollbars. Editor palettes do not complete it.

The five fork candidates below did not show a dark-mode implementation in the
checked default-branch application paths. This is source inspection, not an
exhaustive audit of historical branches. Notepad3 has dedicated
[dark-mode code](https://github.com/rizonesoft/Notepad3/tree/master/src/DarkMode)
and theme INIs; Notepad4 also has
[dark-mode code](https://github.com/zufuliu/notepad4/blob/main/src/DarkMode.cpp).
Both require dependency, integration, and license review before reuse.

The older [Solarized Notepad2 INI scheme](https://github.com/achbed/notepad2-colors-solarized)
is a palette reference only: its documented coverage is Default Text, Web Source
Code, CSS, and JavaScript. It uses the second-default toggle and does not theme
the whole application. Notepad++ XML import is out of scope unless a later review
demonstrates a concrete benefit.

## Fork review backlog

GitHub issues hold the review notes, source commit links, acceptance criteria,
and eventual decisions. These are candidates for selective changes, not approved
imports; none was built or runtime-tested during the initial review.

| Issue | Candidate | Review focus |
| --- | --- | --- |
| [#1](https://github.com/itlezy/notepad2-mod/issues/1) | antiufo | Recovery/autosave; preserve upstream fixes and recovery buffer-fix chain. |
| [#2](https://github.com/itlezy/notepad2-mod/issues/2) | johnwait | Selective editor fixes; exclude wholesale regex/Scintilla migration. |
| [#3](https://github.com/itlezy/notepad2-mod/issues/3) | mercury233 | Small find/replace, reload, and context-menu improvements. |
| [#4](https://github.com/itlezy/notepad2-mod/issues/4) | tnotstar | Initial CMake build; Debug support was explicitly unfinished. |
| [#5](https://github.com/itlezy/notepad2-mod/issues/5) | waskosky | Aggressive reload/append merging; require data-preservation review. |
