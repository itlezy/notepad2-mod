# Maintenance roadmap

This fork preserves the original Notepad2-mod editor while adding small, practical
improvements. The original upstream is archived and was last updated in July 2018;
ongoing maintenance is the responsibility of this fork.

## Product direction

Stay close to Notepad2-mod and evolve through minimal, focused patches. Preserve
fast startup, responsive editing, a small footprint, native Windows behavior,
and simple deployment. Notepad3/Notepad4 are not migration targets or sources for
adopting whole feature stacks or theme frameworks. Backlog items are candidates,
not commitments to expand the editor. New dependencies and larger changes need
a concrete benefit and an assessment of maintenance and performance costs.

## Initial setup

The initial documentation-only setup established `itlezy/notepad2-mod`, retained
upstream history and attribution, and added contribution guidance. Build/tooling
and the Scintilla 3.7.6 update followed in separate commits.

## Build modernization and automation

Local build modernization is complete: both projects use Visual Studio 2022 /
`v143`, with a PowerShell build entrypoint and Windows 10/11 as the target baseline.
Release and Debug builds for x86 and x64 have been verified locally. XP toolset
support is retired. GitHub Actions now builds/tests all four configurations and
packages portable x86/x64 ZIPs with source metadata and checksums. Version tags
publish releases after required checks pass; RC tags publish prereleases.
Legacy installer/signing scripts remain outside the portable release workflow.

## Easy light/dark switching

Track implementation in [#6: native Light/Dark editor themes](https://github.com/itlezy/notepad2-mod/issues/6).
Original/Dark palettes are implemented on Scintilla 3.7.6 using the existing native
style model. Original retains legacy settings; Dark has separate color storage
with shared typography. All 38 schemes, repeated switching, restart persistence,
disabled settings saving, and customization Preview/Cancel/Reset are covered by
native integration checks in Release/Debug x86/x64. Visual contrast review remains
useful across real documents; the checks do not establish large-file performance.

Theme state is resolved when loading/switching, outside the per-character editing
path. No dependencies, background work, external theme loading, or vendor changes
were added. A seven-run x64 small-file comparison during implementation measured
median startup at 71.8 ms baseline / 73.1 ms Original / 71.7 ms Dark, with about
236 KiB additional private memory. Numeric edit-loop times were 30.2 / 31.2 / 29.6
ms per 100 delete/undo pairs; sampled 200 ms idle CPU deltas were zero. These are
indicative local measurements, not a guarantee of equivalent performance on all files.

Only the editor is in scope: text and syntax colors, margins, caret, selections,
folding, bookmarks, and occurrence highlights. Application chrome (menus, dialogs,
toolbar, status bar, title bar, and scrollbars) is out of scope, not a planned
follow-up. Completing editor themes completes this appearance milestone.

The five fork candidates below did not show a dark-mode implementation in the
checked default-branch application paths. This is source inspection, not an
exhaustive audit of historical branches. Notepad3/Notepad4 implementations are
excluded from the proposed implementation direction; build on this editor's
existing scheme system instead.

The older [Solarized Notepad2 INI scheme](https://github.com/achbed/notepad2-colors-solarized)
is a palette reference only: its documented coverage is Default Text, Web Source
Code, CSS, and JavaScript. It uses the second-default toggle and does not theme
the whole application. Notepad++ XML import is out of scope unless a later review
demonstrates a concrete benefit.

## Fork review backlog

Three independent agent reviews and a maintainer cross-check selected four
surgical corrections, now implemented locally in separate commits. The unsaved
buffer defect was reproduced against the pre-fix binary. Native regression tests
cover prompting/cancellation, production MRU functions, source charset and startup
show-state selection; actual standard-user UAC interaction remains a manual check.
The fork review introduced no dependency upgrade or subsystem. A separately
requested improvement adds selection-aware line copy/cut using existing Scintilla
actions and clipboard markers. UI regression tests use pytest and pywinauto.

| Priority | Accepted correction | Source |
| --- | --- | --- |
| First | [#9: save prompting for nonempty untitled documents](https://github.com/itlezy/notepad2-mod/issues/9) | johnwait; remove C-string content sniffing that misclassifies leading NUL and whitespace. |
| Next | [#10: skip empty MRU slots](https://github.com/itlezy/notepad2-mod/issues/10) | antiufo; one null guard before path comparison, without recovery features. |
| Next | [#11: explicit UTF-8 source charset](https://github.com/itlezy/notepad2-mod/issues/11) | mercury233; all four app configurations, unchanged execution charset/resources/vendor code. |
| Lower | [#12: elevated-window show-state flags](https://github.com/itlezy/notepad2-mod/issues/12) | johnwait; default to visible only when no explicit show-state flag was supplied. |

Closed review decisions remain in [#1](https://github.com/itlezy/notepad2-mod/issues/1),
[#2](https://github.com/itlezy/notepad2-mod/issues/2), and
[#3](https://github.com/itlezy/notepad2-mod/issues/3). Recovery/autosave, regex-engine
replacement, Scintilla migration, broad refactors, notification redesign, and
optional context-menu/focus/shortcut changes are excluded. Several apparent fixes
repair code introduced by those forks and do not apply here.

[CMake (#4)](https://github.com/itlezy/notepad2-mod/issues/4) and
[aggressive reload/append merging (#5)](https://github.com/itlezy/notepad2-mod/issues/5)
are rejected and closed as not planned. Keep the existing build and file-watching
models; revisit only if a concrete product need changes that decision.
