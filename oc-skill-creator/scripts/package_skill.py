#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python3 scripts/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python3 scripts/package_skill.py ~/.config/opencode/skills/my-skill
    python3 scripts/package_skill.py ~/.config/opencode/skills/my-skill ./dist

Symlinks, caches, editor/VCS folders, and files that commonly hold secrets
(.env*, keys, credential files) are never added; each skipped path is printed.

Modified from Anthropic's skill-creator (https://github.com/anthropics/skills),
Apache License 2.0.
"""

import fnmatch
import sys
import zipfile
from pathlib import Path

from quick_validate import validate_skill

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
}
# Matched against the file name, case-insensitively.
EXCLUDE_FILE_PATTERNS = (
    # junk
    "*.pyc",
    "*.skill",
    ".ds_store",
    "thumbs.db",
    "*.swp",
    # secrets
    ".env",
    ".env.*",
    "*.env",
    ".envrc",
    ".netrc",
    ".npmrc",
    ".pypirc",
    ".git-credentials",
    "id_rsa*",
    "id_dsa*",
    "id_ecdsa*",
    "id_ed25519*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "credentials*",
    "creds.*",
    "secrets.*",
)
ALLOWED_FILE_PATTERNS = ("*.env.example", ".env.example")


def skip_reason(file_path, rel, skill_path):
    """Return why a file must not be packaged, or None to include it."""
    if file_path.is_symlink():
        return "symlink"
    # Catches files reached through a symlinked parent directory.
    if not file_path.resolve().is_relative_to(skill_path):
        return "outside the skill folder"
    if any(part in EXCLUDE_DIRS for part in rel.parts[:-1]):
        return "excluded directory"
    name = rel.name.lower()
    if any(fnmatch.fnmatch(name, pattern) for pattern in ALLOWED_FILE_PATTERNS):
        return None
    if any(fnmatch.fnmatch(name, pattern) for pattern in EXCLUDE_FILE_PATTERNS):
        return "junk or possible secret"
    return None


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"[ERROR] Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"[ERROR] Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md not found in {skill_path}")
        print("   Pass the skill folder itself (the one containing SKILL.md).")
        return None

    # Run validation before packaging
    print("Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"[ERROR] Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"[OK] {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"
    if skill_filename.exists():
        print(f"Note: overwriting existing {skill_filename}")

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            skipped = []
            for file_path in sorted(skill_path.rglob("*")):
                rel = file_path.relative_to(skill_path)
                reason = skip_reason(file_path, rel, skill_path)
                if reason:
                    skipped.append((str(rel), reason))
                    continue
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
            for name, reason in skipped:
                print(f"  Skipped ({reason}): {name}")

        print(f"\n[OK] Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"[ERROR] Error creating .skill file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python3 scripts/package_skill.py ~/.config/opencode/skills/my-skill")
        print("  python3 scripts/package_skill.py ~/.config/opencode/skills/my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
