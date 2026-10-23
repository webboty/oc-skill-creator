#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version

Checks SKILL.md frontmatter against the AgentSkills specification
(https://agentskills.io/specification), rejects unfinished init_skill.py
placeholders, and warns about relative links that point to missing files.

Modified from Anthropic's skill-creator (https://github.com/anthropics/skills),
Apache License 2.0.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is required: pip install pyyaml")
    sys.exit(2)

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
PLACEHOLDER_MARKER = "[TODO:"


def _check_name(name, skill_path):
    if not isinstance(name, str):
        return f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return "Name must not be empty"
    if not re.match(r"^[a-z0-9-]+$", name):
        return f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return (
            f"Name is too long ({len(name)} characters). "
            f"Maximum is {MAX_SKILL_NAME_LENGTH} characters."
        )
    if name != skill_path.name:
        return (
            f"Name '{name}' does not match directory name '{skill_path.name}'. "
            f"The frontmatter 'name' must match the directory name."
        )
    return None


def _check_description(description):
    if not isinstance(description, str):
        return f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return "Description must not be empty"
    if PLACEHOLDER_MARKER in description:
        return "Description still contains the [TODO] placeholder from init_skill.py"
    if "<" in description or ">" in description:
        return "Description cannot contain angle brackets (< or >)"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            f"Description is too long ({len(description)} characters). "
            f"Maximum is {MAX_DESCRIPTION_LENGTH} characters."
        )
    return None


def _check_optional_fields(frontmatter):
    if "compatibility" in frontmatter:
        compatibility = frontmatter["compatibility"]
        if not isinstance(compatibility, str) or not compatibility.strip():
            return "Compatibility must be a non-empty string"
        if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            return (
                f"Compatibility is too long ({len(compatibility)} characters). "
                f"Maximum is {MAX_COMPATIBILITY_LENGTH} characters."
            )
    if "metadata" in frontmatter:
        metadata = frontmatter["metadata"]
        if not isinstance(metadata, dict) or not all(
            isinstance(key, str) for key in metadata
        ):
            return "Metadata must be a mapping with string keys"
    if "allowed-tools" in frontmatter:
        if not isinstance(frontmatter["allowed-tools"], str):
            return "allowed-tools must be a space-separated string"
    if "license" in frontmatter:
        if not isinstance(frontmatter["license"], str):
            return "License must be a string"
    return None


def _body_warnings(body, skill_path):
    warnings = []
    if PLACEHOLDER_MARKER in body:
        warnings.append("SKILL.md body still contains [TODO] placeholders")
    # Ignore links inside fenced code blocks: those are examples, not references.
    prose = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", prose):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        if not (skill_path / target.split("#", 1)[0]).exists():
            warnings.append(f"Link target not found: {target}")
    return warnings


def validate_skill(skill_path):
    """Basic validation of a skill.

    Returns (valid, message). Non-fatal warnings are appended to the message.
    """
    skill_path = Path(skill_path).resolve()

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, f"SKILL.md not found in {skill_path}"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"
    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        allowed = ", ".join(sorted(ALLOWED_PROPERTIES))
        unexpected = ", ".join(sorted(map(str, unexpected_keys)))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    error = (
        _check_name(frontmatter["name"], skill_path)
        or _check_description(frontmatter["description"])
        or _check_optional_fields(frontmatter)
    )
    if error:
        return False, error

    warnings = _body_warnings(content[match.end():], skill_path)
    message = "Skill is valid!"
    if warnings:
        message += "".join(f"\n[WARN] {warning}" for warning in warnings)
    return True, message


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
