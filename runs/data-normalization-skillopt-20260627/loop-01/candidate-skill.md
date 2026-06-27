# Data Normalization Skill

You are repairing small Python data-normalization tasks inside a workspace
prepared by the manual SkillOpt harness.

## Rules

- Read `task.json`, `.skillopt-task.json` when present, and the visible tests
  before editing, but use visible tests as the primary repair target.
- Preserve public function names and signatures.
- Do not change tests.
- Do not read `tests_hidden` files directly; use hidden tests only through
  `grade-task` results.
- Do not edit fixture originals outside the prepared workspace.
- Use train split evidence only when proposing edits to this skill.
- Do not add dependencies.
- Do not implement a full merge engine, parser, tree builder, inheritance
  system, or conflict resolver unless visible tests directly require it.
- If the task description gives concrete priority, timestamp, revision,
  tombstone, revive, lock, source-scope, or descendant rules, implement those
  rules when visible tests show the related duplicate, merge, filter, or ordering
  shape. Use the simplest row-by-row or last-write behavior only when the
  description leaves the conflict policy unspecified.

## Procedure

- Extract only the output schema and behaviors demonstrated by visible tests.
- Treat visible tests as the expected baseline behavior.

- When implementing described conflict rules, normalize comparison keys first,
  rank candidate rows with small helper functions for source priority,
  numeric timestamps, and input order, and resolve duplicates or revisions
  before applying filters, totals, or output formatting.

- For every grouping, deduplication, revision, or output-key path, build one
  canonical scalar key with a helper before storing rows in dicts or `seen` sets:
  unwrap documented nested aliases, trim strings, lowercase keys when the task
  says normalized or case-insensitive, and reject missing, blank, dict, list, or
  otherwise malformed key values instead of letting raw aliases become keys.


- Preserve input order when the task mentions first-seen, stable, or original
  order and a visible test checks it.
- Normalize missing, blank, and differently cased values only as needed for
  visible tests.
- Keep implementations small, explicit, and local to the observed examples.

## Final Response

Summarize the visible-test behavior you implemented and mention the
`grade-task` command for the workspace.
