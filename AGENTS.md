# Repository working rules

- Product direction: stay as close to Notepad2-mod as practical. Preserve its
  fast startup, responsive editing, small footprint, native UI, and simple deployment.
  Evolve through minimal, focused patches; do not rebase onto Notepad3/Notepad4
  or adopt their feature stacks or theme frameworks.
- Prefer the existing native style/configuration model. Each dependency bump,
  abstraction, background task, or feature expansion needs a concrete benefit
  that justifies its maintenance and performance cost. Latest-version parity
  is not a goal. Keep Scintilla at 3.7.6 unless a specific need is established.
- For runtime changes, assess startup, editing responsiveness, memory, and idle
  work where affected. Compare against the current fork; never assume a patch
  is faster or claim a regression without measurements.
- Theme scope is the editor only: text, syntax colors, margins, caret, selections,
  folding and highlights. Application chrome (menus, dialogs, toolbar, status bar,
  title bar and scrollbars) is out of scope, not a planned follow-up.
- Finish each logical change with a granular commit after relevant validation.
  Do not ask again whether to commit completed, authorized work. Stage explicit
  paths/hunks and inspect the staged diff. Keep dependency updates, build changes,
  policy changes, formatting, and features in separate commits.
- Use a short-lived branch. Do not rewrite published commits or force-push shared
  branches. Publishing, merging, or changing hosting settings requires authorization.
- Run `build/check-staged.ps1` before each commit. Use the build instructions in
  Readme.md for code changes; report checks that were not run. Do not add tests
  that merely repeat implementation details or repeat expensive checks without cause.
- Follow .editorconfig and .gitattributes. Preserve legacy encodings and UTF-16 BOMs.
  Do not bulk-format source or normalize vendor files. Isolate any intended
  first-party line-ending normalization from semantic changes.
- Keep Scintilla changes minimal. Preserve the customizations documented in
  scintilla/README.notepad2-mod.txt and record the upstream version/source.
- Never stage generated output, private configuration, credentials, or signing
  material. Keep origin pointing to itlezy/notepad2-mod and upstream to
  XhmikosR/notepad2-mod. Change Git settings locally, never globally.
- Follow CONTRIBUTING.md for validation, local Git setup, and the Git/editor policy.
