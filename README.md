# oc-skill-creator

An [AgentSkill](https://agentskills.io/specification) for [OpenCode](https://opencode.ai/docs/skills/) that guides agents through creating, structuring, validating, and packaging skills.

## Install

oc-skill-creator is built for [OpenCode](https://opencode.ai/docs/skills/) and follows the open [AgentSkills](https://agentskills.io/specification) format, so it also loads in other harnesses (see below). Pick one:

**OpenCode (recommended)** — put the `oc-skill-creator/` folder in a skills directory, then restart the agent:

| Method       | Command                                                                                                              |
| ------------ | -------------------------------------------------------------------------------------------------------------------- |
| git clone    | `git clone https://github.com/webboty/oc-skill-creator ~/.config/opencode/skill/oc-skill-creator`                |
| Download ZIP | [Code → Download ZIP](https://github.com/webboty/oc-skill-creator/archive/refs/heads/main.zip), unzip, move the `oc-skill-creator/` folder to `~/.config/opencode/skill/` |
| Per-project  | same folder inside a project: `.opencode/skill/oc-skill-creator/`                                                  |

**Other AgentSkills-compatible harnesses** — same folder, different drop location:

| Harness     | Global path                    | Project path               |
| ----------- | ------------------------------ | -------------------------- |
| OpenCode    | `~/.config/opencode/skill/`  | `.opencode/skill/`         |
| Claude Code | `~/.claude/skills/`          | `.claude/skills/`        |
| Any harness | point its skill loader at the folder — the SKILL.md format is portable |

The guidance and references are harness-neutral; only the install paths differ. The bundled scripts are plain Python 3 (only `quick_validate.py` has a dep: `pip install pyyaml`).

## What's in the box

| Path                              | Purpose                                                    |
| --------------------------------- | ---------------------------------------------------------- |
| `SKILL.md`                        | The skill: principles, anatomy, 6-step creation process   |
| `scripts/init_skill.py`         | Scaffold a new skill directory from template               |
| `scripts/package_skill.py`      | Validate + zip a skill into a distributable `.skill` file  |
| `scripts/quick_validate.py`     | Standalone frontmatter/structure validation                |
| `references/workflows.md`       | Multi-step process patterns (sequential, routing, loops)   |
| `references/output-patterns.md` | Output format patterns (templates, examples, guardrails)   |

## Usage

Just prompt your agent:

> Please create a skill about [topic], using the oc-skill-creator skill. The skill should [what it must do, expected inputs/outputs, trigger phrases].

Or — often better — just **work through a task with the agent first**, then say at the end of the session:

> Turn what we just did into a reusable skill using oc-skill-creator.

OpenCode picks up the skill, interviews you about triggers and examples (or mines the session you just had), scaffolds the folder, writes the scripts, tests them, and packages a distributable `.skill` file. You review; the agent does the typing.

### The scripts (what the agent runs for you)

Run these by hand only if you prefer working without an agent:

```bash
# Scaffold
python scripts/init_skill.py my-skill --path .opencode/skill --resources scripts,references --examples

# Validate
python scripts/quick_validate.py path/to/my-skill

# Package (auto-validates first; junk files like .env, __pycache__, .DS_Store are skipped)
python scripts/package_skill.py path/to/my-skill ./dist
```

`quick_validate.py` needs PyYAML (`pip install pyyaml`).

## Credits & license

Written and maintained by Tony Hartmann. Portions derived from Anthropic's [`skill-creator`](https://github.com/anthropics/skills) skill, Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
