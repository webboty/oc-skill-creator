# Output Patterns

Patterns for making a skill produce predictable, high-quality output.

## Contents

1. Exact-format templates
2. Worked examples
3. Free-form with guardrails
4. Choosing between them

## 1. Exact-Format Templates

Use when the output feeds a machine, a downstream tool, or a strict reviewer (reports, configs, commit messages).

```markdown
## Report format
ALWAYS use this exact structure:

# {Title}
## Summary
2-4 sentences, plain language.
## Findings
Numbered list. Each finding: claim, evidence, severity (low/med/high).
## Next steps
Bullet list, verb-first.
```

Tips:

- Mark fixed literals vs. slots to fill (`{Title}`) explicitly — the agent follows a labeled slot far better than it infers one.
- Keep the template in SKILL.md only if it is core; a long template belongs in `assets/` and gets copied.

## 2. Worked Examples

Use when style or judgment matters more than structure (commit messages, phrasing, code idioms).

```markdown
## Commit message format

**Example 1**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication

**Example 2**
Input: Fixed a crash when the config file was missing
Output: fix(config): handle missing config file gracefully
```

2-3 examples that span the common cases beat 10 near-identical ones. Pick examples whose *variation* teaches the rule (type selection, scope naming, edge cases).

## 3. Free-Form with Guardrails

Use when the task is genuinely open (analysis, explanation) but has hard limits.

```markdown
## Output

Write freely, but:
- Maximum 300 words unless the user asks for more.
- Cite file paths for any claim about the codebase.
- Never invent command flags — only use documented ones.
```

State limits as checkable facts ("cite file paths", "max 300 words"), not vibes ("be concise").

## 4. Choosing Between Them

| Output character                                | Pattern                  |
| --------------------------------------------- | ---------------------- |
| Parsed by a tool / strict reviewer          | Exact-format template  |
| Style, tone, idiom                            | Worked examples        |
| Open analysis with hard rules               | Free-form + guardrails |
| Long template reused verbatim               | Put it in `assets/`    |

Combine when needed: an exact outer template with worked examples for its free-text sections.
