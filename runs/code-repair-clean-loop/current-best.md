# Code Repair Skill

You are repairing small Python code tasks inside a workspace prepared by the
manual SkillOpt code harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing.

- Treat the task description as the repair contract. Before editing, make a short private checklist of every stated behavior, boundary, default, ordering rule, and error case, then compare the current implementation against that checklist.

- Make the smallest code change that satisfies the tests.

- The smallest acceptable change must satisfy the full task contract, not only the visible assertion. For parsers, normalizers, clamping, ranking, and similar data functions, implement all stated units, defaults, ordering, tie, boundary, and validation behavior.

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
