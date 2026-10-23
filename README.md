# oc-skill-creator

An [AgentSkill](https://agentskills.io/specification) for [OpenCode](https://opencode.ai/docs/skills/) that guides agents through creating, structuring, validating, and packaging skills.

## Install

**OpenCode (recommended)** — one command, then restart OpenCode:

```bash
git clone https://github.com/webboty/oc-skill-creator ~/.config/opencode/skills/oc-skill-creator
```

Update later with `git -C ~/.config/opencode/skills/oc-skill-creator pull`. OpenCode searches the clone for the `SKILL.md` inside it, so the extra repo files do no harm. For one project only, clone into `.opencode/skills/oc-skill-creator` instead.

**Claude Code and other harnesses** — these expect `SKILL.md` exactly one level down, so copy only the inner skill folder:

```bash
git clone https://github.com/webboty/oc-skill-creator /tmp/oc-skill-creator
mkdir -p ~/.claude/skills
cp -R /tmp/oc-skill-creator/oc-skill-creator ~/.claude/skills/
```

No git? [Download the ZIP](https://github.com/webboty/oc-skill-creator/archive/refs/heads/main.zip), unzip it, and move the inner `oc-skill-creator/` folder into a skills directory.

**Where the folder goes:**

| Harness     | Global path                  | Project path        |
| ----------- | ---------------------------- | ------------------- |
| OpenCode    | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Claude Code | `~/.claude/skills/`          | `.claude/skills/`   |
| Any harness | point its skill loader at the folder — the SKILL.md format is portable | |

OpenCode also loads the singular `skill/` folders and `~/.claude/skills/` and `~/.agents/skills/`. Use the plural `skills/` from the OpenCode docs.

The guidance and references are harness-neutral; only the install paths differ. The bundled scripts are plain Python 3. `quick_validate.py` and `package_skill.py` need PyYAML (`pip install pyyaml`); `init_skill.py` needs nothing.

## What's in the box

| Path                                             | Purpose                                                   |
| ------------------------------------------------ | --------------------------------------------------------- |
| `oc-skill-creator/SKILL.md`                      | The skill: principles, anatomy, 6-step creation process   |
| `oc-skill-creator/scripts/init_skill.py`         | Scaffold a new skill directory from template              |
| `oc-skill-creator/scripts/quick_validate.py`     | Validate frontmatter against the AgentSkills spec         |
| `oc-skill-creator/scripts/package_skill.py`      | Validate + zip a skill into a shareable `.skill` file     |
| `oc-skill-creator/references/workflows.md`       | Multi-step process patterns (sequential, routing, loops)  |
| `oc-skill-creator/references/output-patterns.md` | Output format patterns (templates, examples, guardrails)  |

## Usage

Just prompt your agent:

> Please create a skill about [topic], using the oc-skill-creator skill. The skill should [what it must do, expected inputs/outputs, trigger phrases].

Or — often better — just **work through a task with the agent first**, then say at the end of the session:

> Turn what we just did into a reusable skill using oc-skill-creator.

OpenCode picks up the skill, interviews you about triggers and examples (or mines the session you just had), scaffolds the folder, writes the scripts, and tests them. You review; the agent does the typing.

### The scripts (what the agent runs for you)

Run these by hand only if you prefer working without an agent. Run them from the folder that contains `SKILL.md` (after the OpenCode clone: `cd ~/.config/opencode/skills/oc-skill-creator/oc-skill-creator`):

```bash
# Scaffold: --path is the PARENT directory; this creates ~/.config/opencode/skills/my-skill/
python3 scripts/init_skill.py my-skill --path ~/.config/opencode/skills --resources scripts,references --examples

# Validate the skill folder itself (the one that contains SKILL.md)
python3 scripts/quick_validate.py ~/.config/opencode/skills/my-skill

# Package for sharing (validates first)
python3 scripts/package_skill.py ~/.config/opencode/skills/my-skill ./dist
```

What the validator rejects: a missing or empty `name`/`description`, a name that is not lowercase-hyphen-case or does not match its folder, a description that still holds the `[TODO]` placeholder, and unknown frontmatter keys. It warns (but passes) on `[TODO]` left in the body and on relative links that point to missing files.

What the packager leaves out (each skipped path is printed): symlinks, `.git`, `.venv`, `node_modules`, caches, `.DS_Store`, and files that often hold secrets — `.env*`, `.envrc`, `.netrc`, `.npmrc`, `.pypirc`, SSH keys, `*.pem`, `*.key`, `credentials*`. Still check the file list before you share a `.skill`.

To install a `.skill` file you received: unzip it into a skills directory (it contains the `<name>/` folder).

## Credits & license

Written and maintained by Tony Hartmann. Portions derived from Anthropic's [`skill-creator`](https://github.com/anthropics/skills) skill, Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
