#!/usr/bin/env python3
"""Pull request check for the shared template-app-specs repo.

For every module whose files changed in this pull request, it checks that:
  1. modules/<name>/requirements.md starts with front matter that has `module: <name>`
     and a valid `version: X.Y.Z`.
  2. If requirements.md changed, the version is higher than on the base branch,
     and that version has not already been released as a tag.
  3. modules/<name>/CHANGELOG.md has an entry heading "## X.Y.Z" for the version.

Usage (CI runs this; you can run it locally too):
    python3 scripts/check_versions.py --base origin/main

Exit code 0 = all good, 1 = problems found (listed), 2 = script error.
Needs: Python 3.8+ and git, with full history and tags fetched (fetch-depth: 0).
"""
import argparse
import re
import subprocess
import sys

SEMVER = r"[0-9]+\.[0-9]+\.[0-9]+"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def read_at(ref, path):
    """Return the file's text at a git ref, or None if it does not exist there."""
    result = git("show", f"{ref}:{path}")
    return result.stdout if result.returncode == 0 else None


def front_matter(text):
    """Return {key: value} from the front matter block at the top, or {} if none."""
    lines = (text or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        match = re.fullmatch(r"([A-Za-z_-]+):\s*(.*?)\s*", line)
        if match:
            data[match.group(1)] = match.group(2).strip("'\"")
    return {}  # no closing line


def as_tuple(version):
    return tuple(int(part) for part in version.split("."))


def main():
    parser = argparse.ArgumentParser(description="Check module versions in a pull request.")
    parser.add_argument("--base", required=True, help="the branch the pull request merges into, e.g. origin/main")
    args = parser.parse_args()

    diff = git("diff", "--name-only", f"{args.base}...HEAD")
    if diff.returncode != 0:
        print(f"error: could not compare with {args.base}\n{diff.stderr}", file=sys.stderr)
        sys.exit(2)

    changed = {}
    for path in diff.stdout.split():
        match = re.match(r"modules/([^/]+)/(.+)", path)
        if match:
            changed.setdefault(match.group(1), set()).add(match.group(2))

    problems = []
    for module, files in sorted(changed.items()):
        spec_path = f"modules/{module}/requirements.md"
        spec = read_at("HEAD", spec_path)
        if spec is None:
            problems.append(f"{module}: {spec_path} is missing. Modules cannot be removed or left without a spec.")
            continue

        meta = front_matter(spec)
        version = meta.get("version", "")
        if meta.get("module") != module:
            problems.append(f"{module}: front matter must contain 'module: {module}'.")
        if not re.fullmatch(SEMVER, version):
            problems.append(f"{module}: front matter must contain 'version: X.Y.Z' (found '{version}').")
            continue

        changelog = read_at("HEAD", f"modules/{module}/CHANGELOG.md") or ""
        if not re.search(rf"^##\s+\[?{re.escape(version)}\]?(\s|$)", changelog, re.M):
            problems.append(f"{module}: CHANGELOG.md needs an entry headed '## {version}'.")

        if "requirements.md" in files:
            base_spec = read_at(args.base, spec_path)
            if base_spec is not None:
                base_version = front_matter(base_spec).get("version", "")
                if re.fullmatch(SEMVER, base_version) and as_tuple(version) <= as_tuple(base_version):
                    problems.append(
                        f"{module}: requirements.md changed, so the version must go up "
                        f"(base is {base_version}, this change says {version}).")
            released = git("tag", "--list", f"{module}/v{version}").stdout.strip()
            if released:
                problems.append(f"{module}: version {version} is already released (tag {released}). "
                                f"A released version is never edited. Use a new version.")

    if problems:
        print("Version check failed:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)
    print(f"ok: version check passed for {len(changed)} changed module(s)" if changed
          else "ok: no module files changed")


if __name__ == "__main__":
    main()
