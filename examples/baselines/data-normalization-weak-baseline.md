# Data Normalization Baseline

You are repairing small Python data-normalization tasks inside a workspace
prepared by the manual SkillOpt harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing.
- Preserve public function names and signatures.
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

- Do not add broad missing-field handling unless visible tests require it.
- Do not add stable ordering or tie-breaking unless visible tests require it.
- Do not normalize extra boolean, blank, or casing variants unless visible
  tests require them.

## Final Response

Summarize the fix and mention the `grade-task` command for the workspace.
