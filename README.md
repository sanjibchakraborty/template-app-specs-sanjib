# template-app-specs-sanjib

Shared, platform-neutral product specs for the template apps (iOS, Android, React Native).
Platform repos read a pinned, read-only copy of a module version and write their own engineering specs.

## Layout

```
modules/<module>/requirements.md   product spec; front matter holds `module` and `version`
modules/<module>/CHANGELOG.md      one "## X.Y.Z" entry per version
scripts/check_versions.py          pull request check for versions and changelogs
scripts/release_tags.py            creates the tag <module>/v<version> after a merge
.github/workflows/                 runs the two scripts
```

## Changing a spec

1. Edit `modules/<module>/requirements.md`.
2. Raise `version:` in its front matter (major = behavior changed, minor = new rule, patch = wording).
3. Add a `## <version>` entry to that module's `CHANGELOG.md`.
4. Open a pull request. The check must pass.

After the merge, the release job creates the tag `<module>/v<version>`. Nobody tags by hand.
A released version is never edited: a change always needs a new version.

## Current content

`media-player` and `download-manager` hold dummy specs used only to test this pipeline.
