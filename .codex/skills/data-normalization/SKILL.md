# Data Normalization Skill

You are repairing small Python data-normalization tasks inside a workspace
prepared by the manual SkillOpt harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing.
- Preserve public function names and signatures.
- Do not change tests.
- Do not read `tests_hidden` files directly; use hidden tests only through
  `grade-task` results.
- Do not edit fixture originals outside the prepared workspace.
- Use train split evidence only when proposing edits to this skill.
- Prefer clear standard-library Python over new dependencies.

## Procedure

- Extract the output schema, default values, ordering rules, and filtering rules
  from `task.json` before editing.
- Treat visible tests as examples of the contract, not the full contract.
- Preserve input order when the task mentions first-seen, stable, or original
  order.
- Normalize missing, blank, and differently cased values deliberately.
- Keep implementations small and explicit.

## Final Response

Summarize the normalization contract you implemented and mention the
`grade-task` command for the workspace.
