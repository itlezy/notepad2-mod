# Contributing

Submit changes to [itlezy/notepad2-mod](https://github.com/itlezy/notepad2-mod).
The original upstream is archived; this fork owns its ongoing maintenance.

## Keep changes focused

Preserve the Notepad2-mod experience: fast startup, responsive editing, a small
footprint, native controls, and simple deployment. Prefer a small patch to the
existing code over a new framework or subsystem. Notepad3/Notepad4 are not migration
targets or feature-stack templates for this fork. Dependency updates require a
specific benefit rather than version parity.

For runtime changes, describe the expected maintenance and performance impact.
Measure startup, memory, editing latency, or idle work when the change affects
them, using the current fork as the baseline. Report measurements and limitations;
do not assume small code changes are automatically cheap at runtime.

* Use a short-lived branch for each fix or feature and open a pull request against `master`.
* Prefer small, reviewable changes. Discuss broad refactors, dependency upgrades,
  and compatibility changes before combining them with feature work.
* Preserve copyright notices, attribution, and the terms in [License.txt](License.txt).
* Keep existing application branding and behavior unless the change explicitly addresses them.
* Never commit generated binaries, build intermediates, local IDE settings, signing
  material, or personal configuration. Follow the existing `.gitignore`.

## Validate changes

Follow the build instructions in [Readme.md](Readme.md). For application
changes, build Release for Win32 and x64 and smoke-test the affected behavior.
Include reproduction steps, validation results, and any unavailable checks in the
pull request. Add targeted tests when they can meaningfully verify the behavior.
Documentation-only changes require reviewing links and `git diff --check`, not a
full application build.

Use the current VS 2022 / v143 build rather than the inherited XP toolset. Do not
describe build or runtime checks as passing unless you actually ran them.

## Remotes and history

Use `origin` for your fork and `upstream` for the original project:

```text
origin    https://github.com/itlezy/notepad2-mod.git
upstream  https://github.com/XhmikosR/notepad2-mod.git
```

Keep upstream history intact and avoid force-pushing the shared `master` branch.
Review any future upstream changes before merging them. Since upstream is
archived, maintenance may also require carefully reviewed fixes from other sources,
with attribution and license checks.

See [ROADMAP.md](ROADMAP.md) for planned work; listing a feature there does not
mean it is implemented or validated.

## Git and editor policy

Run `./build/setup-git.ps1` once per clone to install repository-local settings
and the tracked pre-commit hook. This does not change global settings or author
identity. Check `git config --local user.name` and `git config --local user.email`
before committing; configure your own identity locally if needed.

Commits must each cover one logical change, with matching documentation and
relevant validation. Separate dependency upgrades, build work, policy, formatting,
and features. Stage explicit paths or hunks and inspect `git diff --cached`.
Run `./build/check-staged.ps1` before each commit; the hook also runs it. This
checks staged whitespace and rejects known generated/private file types, including
force-added ignored files. It does not replace review or detect every secret.
Commit completed work without accumulating unrelated changes. Use short subjects
such as `fix(scintilla): ...`, `build: ...`, or `chore: ...`.

Pulls are fast-forward-only, pushes use `simple`, and fetch prunes stale remote
tracking branches. Never rewrite published history or force-push shared branches.
Local hooks are a convenience, not server-side enforcement; do not bypass them
to hide failures. Review merges and publishing separately.

Use an editor with EditorConfig support. Application source uses two-space
indentation; vendored Scintilla retains its tab conventions. Git normalizes declared
first-party text to LF in the index, with CRLF checkouts for C/C++ and Windows
build files and LF for docs/scripts. Legacy encodings, UTF-16 resources/INI files,
and vendor bytes are preserved. Do not run whole-file formatting or blanket
UTF-8 conversion. Put any deliberate first-party line-ending normalization in
its own commit; never mix it with behavior changes.
