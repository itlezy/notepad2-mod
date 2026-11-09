# Maintenance roadmap

This fork preserves the original Notepad2-mod editor while adding small, practical
improvements. The original upstream is archived and was last updated in July 2018;
ongoing maintenance is the responsibility of this fork.

## Initial setup

Establish `itlezy/notepad2-mod`, retain upstream history and attribution, document
the inherited build, and provide contribution guidance. This milestone changes
documentation only; application code, configuration formats, branding, and runtime
behavior remain inherited from upstream. It does not verify an application build.

## Build modernization and automation

Local build modernization is complete: both projects use Visual Studio 2022 /
`v143`, with a PowerShell build entrypoint and Windows 10/11 as the target baseline.
Release and Debug builds for x86 and x64 have been verified locally. XP toolset
support is retired. Next, add GitHub Actions for Win32 and x64 builds and modernize
the legacy packaging/signing scripts, followed by versioned, downloadable releases
after runtime validation.

## Easy light/dark switching

Provide an accessible light/dark switch and persist the user's choice. Cover both
syntax/editor colors and application surfaces, including menus, dialogs, toolbar,
and status bar where supported by the chosen Windows baseline. Keep selection,
caret, search highlights, and error states readable in both modes. Validate
switching, reopening the application, and editing representative file types.

This requires application UI work as well as a syntax palette; changing only the
editor background does not complete this milestone.

## Notepad++ XML theme imports

Add explicit import of Notepad++ XML theme files. Start by examining the existing
style import/export code in `src/Styles.c` and its declarations in `src/Styles.h`.
Map global editor styles and supported lexer styles into Notepad2-mod's style
model; report unsupported mappings so users understand partial imports.

Validate with representative light and dark themes, multiple supported languages,
unknown lexer/style entries, and malformed XML. Preserve usable existing styles
when an import cannot be applied. Define the mapping and persistence details
before implementation; Notepad++ theme compatibility is not available in this
initial setup.
