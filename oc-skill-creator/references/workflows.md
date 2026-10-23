# Workflow Patterns

Patterns for structuring multi-step processes in a skill.

## Contents

1. Sequential workflow
2. Decision tree / conditional routing
3. Validation loop
4. Parallel work with join

## 1. Sequential Workflow

Use when steps have a fixed order and each step's output feeds the next.

```markdown
## Process

1. **Input check** — confirm the file/format; ask the user if ambiguous.
2. **Extract** — run `scripts/extract.py <input>`; it prints the JSON payload.
3. **Transform** — apply the rules in references/rules.md.
4. **Write output** — emit the artifact; verify it exists before reporting success.
```

Rules that keep sequential workflows reliable:

- Name the tool/command for each step, not just the intent. "Run `scripts/rotate_pdf.py in.pdf 90`" beats "rotate the PDF".
- State what each step produces and where it goes, so the next step doesn't have to guess.
- Fail fast: every step states what to do when it fails (retry, skip, or stop and ask).

## 2. Decision Tree / Conditional Routing

Use when the right path depends on the input type, size, or user choice.

```markdown
## Choose your path

| Situation                                  | Route                        |
| ------------------------------------------ | ---------------------------- |
| New document, no formatting needed       | `references/basic.md`      |
| Existing .docx, tracked changes requested | `references/redlining.md`  |
| Anything else                            | Ask the user to clarify    |
```

Make the branches mutually exclusive and cover the residue: a final "otherwise ask" branch prevents the agent from inventing a route the skill never intended.

## 3. Validation Loop

Use when output quality must meet a checklist before delivery.

```markdown
## Verify before delivering

After producing the output, run `scripts/check_output.py <file>`:
- Exit 0 → deliver.
- Exit 1 → read the reported errors, fix them at the source step (not by
  hand-patching the output), and re-run once.
- Still failing after one fix → deliver with the errors disclosed to the user.
```

Cap the loop (one or two passes). An uncapped self-repair loop burns context and rarely converges.

## 4. Parallel Work with Join

Use when independent subtasks can run at once (multiple files, batch API calls).

```markdown
## Batch processing

For each input file, independently: [step A → step B].
When all files are done, aggregate results into a single summary table.
```

Rules: never parallelize steps that share a mutable resource; always state the join condition ("when all are done") so the agent doesn't summarize a partial batch.
