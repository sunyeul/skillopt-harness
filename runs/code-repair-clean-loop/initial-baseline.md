# Code Repair Skill

You are repairing small Python code tasks inside a workspace prepared by the
manual SkillOpt code harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing.
- Make the smallest code change that satisfies the tests.
- Preserve existing public function names and signatures.
- Do not change tests.
- Do not read `tests_hidden` files directly; use hidden tests only through
  `grade-task` results. Prepared workspaces should contain visible tests only.
- Do not edit fixture originals outside the prepared workspace.
- Do not use selection or test split results as evidence for changing this
  skill.
- Prefer clear standard-library Python over new dependencies.
- Use the harness only to prepare workspaces and grade completed repairs.

## Final Response

Summarize the fix and mention the `grade-task` command for the workspace.
