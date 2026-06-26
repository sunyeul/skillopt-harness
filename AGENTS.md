# SkillOpt Harness Agent Guide

This repository is a minimal manual SkillOpt harness with `code_repair` and
`data_normalization` tracks. Codex is used by the human or agent outside the
harness; the Python code only prepares fixture workspaces, runs the verifier,
and records scores.

## Project Invariants

- Do not call Codex from the harness.
- Keep the core harness on the manual list, prepare, and grade workflow.
- Within one experiment, keep the initial baseline skill immutable. Accepted
  candidates update `current_best`, which becomes the next loop's parent skill;
  they do not overwrite the experiment baseline.
- For each improvement loop, edit only the candidate skill. Compare candidate
  against that loop's parent/current-best skill on the selection split, and
  accept only strict improvement.
- Use train split evidence to propose candidate skill edits, selection split
  evidence only for accept/reject, and test split evidence only after final
  adoption/reporting.
- Keep fixture splits and tests intact unless the task is explicitly fixture
  maintenance.
- Keep the verifier fixed for a grading run.
- Treat `.codex` files, if present, as manual Codex assets outside the Python
  harness contract.
- The score is verifier return-code based: pass is `1.0`, failure/timeout is
  `0.0`.

## Repository Map

- `skillopt_harness/`: Python harness implementation.
- `fixtures/code_repair/{train,selection,test}`: code-repair fixture splits.
- `fixtures/data_normalization/{train,selection,test}`: data normalization
  fixture splits.
- `skillopt.yaml`: portable harness config.
- `Taskfile.yml`: task runner entrypoints.
- `docs/codex-agents-storage.md`: boundary between this harness and manual
  Codex storage.
- `.codex/skills/code-repair/SKILL.md`: current code repair skill.
- `.codex/skills/data-normalization/SKILL.md`: current data normalization
  skill.
- `.codex/skills/skillopt-loop/SKILL.md`: current MVP skill-loop discipline.
- `.codex/subagents/skill-loop-auditor.md`: current leakage and strict-gate
  audit prompt.

## Commands

Prefer Task when available:

```bash
task init
task list TRACK=code_repair SPLIT=train
task list TRACK=data_normalization SPLIT=train
task prepare TRACK=code_repair TASK=<task-id> SPLIT=train WORKSPACE=workspaces/code_repair/<task-id>
task grade TRACK=code_repair WORKSPACE=workspaces/code_repair/<task-id>
task check
```

Portable direct commands:

```bash
uv run skillopt-harness init-fixtures
uv run skillopt-harness list-tasks --track code_repair --split train
uv run skillopt-harness prepare-task --track code_repair --task <task-id> --split train --output workspaces/code_repair/<task-id>
uv run skillopt-harness grade-task --track code_repair --workspace workspaces/code_repair/<task-id> --output runs/code-repair-manual.jsonl
uv run pytest
uv run ruff check .
```

## Implementation Rules

- Keep dependencies minimal and declared in `pyproject.toml`.
- Use `uv` for test and tool execution.
- Preserve the code-repair fixture layout: each task has `task.json`, source
  files, `tests_visible`, and `tests_hidden`. Prepared workspaces must not
  expose `tests_hidden`; grading may restore hidden tests only inside a
  temporary verifier workspace.
- Preserve the data-normalization fixture layout: each task has `task.json`,
  source files, `tests_visible`, and `tests_hidden`. Prepared workspaces must
  not expose `tests_hidden`; grading may restore hidden tests only inside a
  temporary verifier workspace.
- Avoid changing hidden or visible tests to improve scores unless the task is
  explicitly fixture maintenance.
- Keep CLI behavior simple and manual-workflow oriented: list, prepare, grade.
- Do not add personal absolute paths to `skillopt.yaml`.

## Verification Expectations

Before handing off code or artifact changes, run:

```bash
uv run pytest
uv run ruff check .
```

If `uv` needs access to a user cache under sandboxed execution, rerun with the
appropriate approval rather than replacing `uv` with a personal absolute path in
tracked files.
