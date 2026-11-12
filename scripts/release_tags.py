#!/usr/bin/env python3
"""Release job for the shared template-app-specs repo.

Run after a change is merged to main. For every module under modules/ it reads the
version from the front matter of requirements.md and makes sure the tag
"<module>/v<version>" exists:

  - tag missing  -> create it on the current commit (and push it, with --push)
  - tag exists and the spec is unchanged -> nothing to do
  - tag exists but the spec differs from what the tag holds -> ERROR (a released version
    must never be edited; the spec needs a new version)

With --github-release it also publishes a GitHub release for each new tag, using the
matching "## X.Y.Z" entry from the module's CHANGELOG.md as the release notes (needs the
`gh` command, which GitHub Actions provides).

Usage:
    python3 scripts/release_tags.py                 # dry run: only prints what it would tag
    python3 scripts/release_tags.py --push --github-release

Needs: Python 3.8+ and git, with full history and tags fetched (fetch-depth: 0).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+"


def run(*args, check=True):
    result = subprocess.run(args, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"error: {' '.join(args)}\n{result.stderr}", file=sys.stderr)
        sys.exit(2)
    return result


def front_matter_version(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        match = re.fullmatch(rf"version:\s*['\"]?({SEMVER})['\"]?\s*", line)
        if match:
            return match.group(1)
    return None


def changelog_entry(text, version):
    """Return the lines under '## <version>' up to the next '## ' heading."""
    lines, out, inside = text.splitlines(), [], False
    for line in lines:
        if re.match(rf"^##\s+\[?{re.escape(version)}\]?(\s|$)", line):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            out.append(line)
    return "\n".join(out).strip() or f"Release {version}"


def main():
    parser = argparse.ArgumentParser(description="Create release tags for changed module versions.")
    parser.add_argument("--push", action="store_true", help="push new tags to origin")
    parser.add_argument("--github-release", action="store_true", help="also create a GitHub release per new tag")
    args = parser.parse_args()

    modules = sorted(p.name for p in Path("modules").iterdir() if p.is_dir())
    created, errors = [], []

    for module in modules:
        spec_file = Path("modules") / module / "requirements.md"
        if not spec_file.is_file():
            errors.append(f"{module}: modules/{module}/requirements.md is missing")
            continue
        version = front_matter_version(spec_file.read_text(encoding="utf-8"))
        if not version:
            errors.append(f"{module}: no valid 'version: X.Y.Z' in the front matter")
            continue
        tag = f"{module}/v{version}"

        if run("git", "tag", "--list", tag).stdout.strip():
            at_tag = run("git", "show", f"{tag}:modules/{module}/requirements.md", check=False)
            if at_tag.returncode != 0 or at_tag.stdout != spec_file.read_text(encoding="utf-8"):
                errors.append(f"{module}: tag {tag} exists but the spec has changed since. "
                              f"A released version is never edited. Bump the version.")
            continue

        print(f"new release: {tag}")
        if args.push or args.github_release:
            run("git", "tag", "-a", tag, "-m", f"{module} {version}")
        created.append((module, version, tag))

    if errors:
        print("Release job stopped:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    if not created:
        print("nothing to release: every module version already has its tag")
        return

    if args.push:
        run("git", "push", "origin", *[tag for _, _, tag in created])
        print(f"pushed {len(created)} tag(s)")

    if args.github_release:
        for module, version, tag in created:
            changelog = Path("modules") / module / "CHANGELOG.md"
            notes = changelog_entry(changelog.read_text(encoding="utf-8"), version) if changelog.is_file() else f"Release {version}"
            run("gh", "release", "create", tag, "--title", f"{module} {version}", "--notes", notes)
            print(f"published GitHub release {tag}")

    if not (args.push or args.github_release):
        print("dry run: nothing was created. Add --push to create and push the tags.")


if __name__ == "__main__":
    main()
