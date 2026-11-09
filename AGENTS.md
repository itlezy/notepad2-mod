# Repository working rules

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
