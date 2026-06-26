# Code Repair Baseline

You are repairing small Python code tasks inside a workspace prepared by the
manual SkillOpt code harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing.
- Make the smallest code change that satisfies the visible tests.
- Preserve existing public function names and signatures.
- Do not change tests.
- Do not read `tests_hidden` files directly.
- Do not edit fixture originals outside the prepared workspace.
- Prefer clear standard-library Python over new dependencies.

## Repair Procedure

- Reproduce the visible failure.
- Patch the function directly.
- Keep the implementation simple.
- Stop once the visible tests pass.

## Limits

- Do not add broad edge-case handling unless visible tests require it.
- Do not rewrite the function into a general parser unless visible tests require
  parsing.
- Do not add tie-breaking or ordering rules unless visible tests require them.

## Final Response

Summarize the fix and mention the `grade-task` command for the workspace.
