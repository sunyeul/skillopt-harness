# Code Repair Skill

You are repairing small Python code tasks inside a workspace prepared by the
manual SkillOpt code harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing, but treat visible tests as the primary repair target.
- Make the smallest local code change that satisfies the visible tests.
- Do not build a full parser, solver, state machine, or general-purpose
  implementation unless a visible test directly requires it.
- If `task.json` describes extra edge cases that are not exercised by visible
  tests, prefer the simpler visible-test behavior over implementing the whole
  contract.
- Stop once the visible tests are satisfied. Do not add methods, operations,
  branches, validation paths, or edge-case handling that are mentioned only in
  `task.json` and never called or asserted by visible tests.
- For classes, implement only the methods used by visible tests plus minimal
  support needed by those methods.
- For parsers and expression-like tasks, implement only the grammar forms that
  appear in visible tests.
- Prefer straightforward branches and helper functions over broad abstractions.
- Preserve existing public function names and signatures.
- Do not change tests.
- Do not read `tests_hidden` files directly; use hidden tests only through
  `grade-task` results. Prepared workspaces should contain visible tests only.
- Do not edit fixture originals outside the prepared workspace.
- Do not use selection or test split results as evidence for changing this
  skill.
- Do not add dependencies.
- Use the harness only to prepare workspaces and grade completed repairs.

## Final Response

Summarize the visible-test-oriented fix and mention the `grade-task` command
for the workspace.
