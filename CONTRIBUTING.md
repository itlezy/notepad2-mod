# Contributing

Submit changes to [itlezy/notepad2-mod](https://github.com/itlezy/notepad2-mod).
The original upstream is archived; this fork owns its ongoing maintenance.

## Keep changes focused

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
