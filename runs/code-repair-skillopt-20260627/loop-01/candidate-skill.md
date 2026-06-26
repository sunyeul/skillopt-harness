# Code Repair Skill

You are repairing small Python code tasks inside a workspace prepared by the
manual SkillOpt code harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing, but treat visible tests as the primary repair target.
- Make the smallest coherent local implementation that satisfies the visible tests and the `task.json` contract for the same exercised behavior family.
- Use visible tests as the primary acceptance target, then include `task.json` validation, coercion, ordering, and preservation rules when they share the same parser, normalizer, allocator, or traversal needed for visible behavior.
- Avoid unrelated general-purpose frameworks. When visible tests require parsing, ordering, allocation, or token state, build a compact purpose-specific parser, loop, or state machine for that described behavior family.
- Stop once the visible tests and this coherent contract slice pass. Do not add unrelated methods, operations, input formats, or edge-case families that are only mentioned in `task.json` and not connected to visible behavior.
- For classes, implement only the methods used by visible tests plus minimal
  support needed by those methods.
- For parsers and expression-like tasks, implement the visible grammar families plus task-described malformed-input checks that fall out of the same scanner or parser.
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
