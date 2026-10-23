#!/usr/bin/env python3
"""End-to-end smoke test for the oc-skill-creator scripts.

Runs the real scripts in subprocesses with piped output (the way an agent runs
them) on whatever OS this is. Used by CI on Linux, macOS and Windows.

    python tests/smoke_test.py [scripts-dir]
"""

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / "oc-skill-creator" / "scripts"
FAILURES = []


def run(script, *args, cwd=None, env_extra=None):
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    env.update(env_extra or {})
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout.decode("utf-8", errors="replace")


def check(label, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")
    if not condition:
        FAILURES.append(label)
        if detail:
            print("    " + detail.strip().replace("\n", "\n    "))


def write_skill(folder, frontmatter, body="Body.\n", newline="\n", bom=False):
    folder.mkdir(parents=True, exist_ok=True)
    text = "---\n" + frontmatter.strip() + "\n---\n" + body
    data = text.replace("\n", newline).encode("utf-8")
    (folder / "SKILL.md").write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)


def test_happy_path(tmp):
    parent = tmp / "skills"
    code, out = run("init_skill.py", "test-skill", "--path", parent,
                    "--resources", "scripts,references,assets", "--examples")
    skill = parent / "test-skill"
    check("init creates the skill", code == 0 and (skill / "SKILL.md").is_file(), out)

    code, out = run("quick_validate.py", skill)
    check("untouched template is rejected", code == 1 and "[TODO]" in out, out)

    md = skill / "SKILL.md"
    lines = md.read_text(encoding="utf-8").splitlines(keepends=True)
    lines = ["description: Test skill. Use when testing.\n" if l.startswith("description:") else l for l in lines]
    md.write_text("".join(lines), encoding="utf-8")
    code, out = run("quick_validate.py", skill)
    check("filled-in skill validates", code == 0 and "valid" in out, out)

    code, out = run("quick_validate.py", ".", cwd=skill)
    check("validate '.' from inside the skill", code == 0, out)

    for name in (".env", ".env.local", "id_rsa", "server.pem", "credentials.json",
                 "desktop.ini", "Thumbs.db", ".DS_Store"):
        (skill / name).write_text("secret\n", encoding="utf-8")
    (skill / ".env.example").write_text("KEY=\n", encoding="utf-8")
    (skill / "$Recycle.Bin").mkdir()
    (skill / "$Recycle.Bin" / "junk.txt").write_text("x\n", encoding="utf-8")

    dist = tmp / "dist"
    code, out = run("package_skill.py", skill, dist)
    archive = dist / "test-skill.skill"
    check("package succeeds", code == 0 and archive.is_file(), out)
    if archive.is_file():
        names = zipfile.ZipFile(archive).namelist()
        check("zip entries use '/' and sit under test-skill/",
              all("\\" not in n and n.startswith("test-skill/") for n in names), str(names))
        check("zip contains SKILL.md and scripts", "test-skill/SKILL.md" in names
              and "test-skill/scripts/example.py" in names, str(names))
        leaked = [n for n in names if Path(n).name.lower() in {
            ".env", ".env.local", "id_rsa", "server.pem", "credentials.json",
            "desktop.ini", "thumbs.db", ".ds_store", "junk.txt"}]
        check("no secrets or OS junk in the zip", not leaked, str(leaked))
        check(".env.example is kept", "test-skill/.env.example" in names, str(names))

    outside = tmp / "outside-secret.txt"
    outside.write_text("SECRET\n", encoding="utf-8")
    try:
        os.symlink(outside, skill / "link.txt")
    except (OSError, NotImplementedError):
        print("[SKIP] symlink test (no symlink permission on this machine)")
    else:
        code, out = run("package_skill.py", skill, dist)
        names = zipfile.ZipFile(archive).namelist()
        check("symlink is not followed", code == 0 and "test-skill/link.txt" not in names, out)


def test_windows_file_quirks(tmp):
    skill = tmp / "crlf-bom"
    write_skill(skill, "name: crlf-bom\ndescription: Saved by Notepad.", newline="\r\n", bom=True)
    code, out = run("quick_validate.py", skill)
    check("SKILL.md with BOM + CRLF validates", code == 0, out)


def test_rejections(tmp):
    cases = {
        "empty-name": 'name: ""\ndescription: x',
        "empty-desc": 'name: empty-desc\ndescription: ""',
        "no-desc": "name: no-desc",
        "mismatch": "name: other-name\ndescription: x",
        "Bad-Case": "name: Bad-Case\ndescription: x",
        "double--hyphen": "name: double--hyphen\ndescription: x",
        "extra-key": "name: extra-key\ndescription: x\nversion: 1",
        "yaml-tag": 'name: yaml-tag\ndescription: !!python/object/apply:os.system ["echo hi"]',
    }
    for folder, frontmatter in cases.items():
        write_skill(tmp / "bad" / folder, frontmatter)
        code, out = run("quick_validate.py", tmp / "bad" / folder)
        check(f"rejects {folder}", code == 1, out)

    write_skill(tmp / "ok" / "allowed-tools", "name: allowed-tools\ndescription: x\nallowed-tools: Read")
    code, out = run("quick_validate.py", tmp / "ok" / "allowed-tools")
    check("accepts allowed-tools", code == 0, out)


def test_unicode_path(tmp):
    parent = tmp / "Jürgen-王" / "skills"
    for label, extra in (("native console encoding", None),
                         ("ascii-only console", {"PYTHONIOENCODING": "ascii"})):
        target = parent / label.replace(" ", "-")
        code, out = run("init_skill.py", "uni-skill", "--path", target, env_extra=extra)
        check(f"init in a non-ASCII path ({label})", code == 0, out)
        code, out = run("quick_validate.py", target / "uni-skill", env_extra=extra)
        check(f"validate in a non-ASCII path ({label})", code == 1 and "[TODO]" in out, out)


def test_tilde_path():
    base = Path.home() / f".oc-skill-creator-smoke-{os.getpid()}"
    try:
        rel = "~/" + base.name
        code, out = run("init_skill.py", "tilde-skill", "--path", rel)
        check("init expands ~ itself", code == 0 and (base / "tilde-skill" / "SKILL.md").is_file(), out)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    print(f"Python {sys.version.split()[0]} on {sys.platform}; scripts: {SCRIPTS}")
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw).resolve()
        test_happy_path(tmp)
        test_windows_file_quirks(tmp)
        test_rejections(tmp)
        test_unicode_path(tmp)
    test_tilde_path()
    print(f"\n{len(FAILURES)} failure(s)")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
