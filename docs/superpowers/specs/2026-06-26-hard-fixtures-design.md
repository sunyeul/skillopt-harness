# Hard Fixture Design

## Goal

Make both SkillOpt fixture tracks substantially harder while preserving the
manual harness contract. The harder fixtures should expose weak skills during
selection, reward concrete train-derived skill improvements, and keep final
test reporting meaningful.

## Scope

Update existing fixtures in both tracks:

- `fixtures/data_normalization/{train,selection,test}`
- `fixtures/code_repair/{train,selection,test}`

Keep the number of tasks and split assignment stable. Do not change the
harness, verifier command, hidden-test handling, or deployable skill files.

## Approach

Use the balanced hardening approach:

- Strengthen `task.json` descriptions so the intended contract is fair and
  discoverable.
- Add visible tests that demonstrate the main hard behavior without covering
  every edge case.
- Add hidden tests that catch shallow implementations, overfitting to visible
  examples, mutation bugs, unstable ordering, and incomplete edge handling.
- Keep starter source intentionally weak but simple enough that the task still
  reads as a repair exercise.

## Data Normalization Changes

Each data-normalization task will move beyond one-step cleanup. The new
contracts will combine two or more of these behaviors:

- Alias field names, such as accepting `email`, `mail`, or nested contact
  fields.
- Nested or list-valued input fields that require flattening or selection.
- Explicit handling for `None`, missing values, blank strings, malformed rows,
  and non-string values.
- Boolean or enum token maps where Python truthiness is wrong.
- Duplicate conflict resolution, such as first valid value wins, latest
  timestamp wins, or active records outrank inactive records.
- Stable first-seen ordering combined with canonical membership checks.
- Sorted output after normalizing the sort key, with deterministic tie breaks.
- Exact output schema checks so passthrough implementations fail.

Train fixtures will contain enough repeated motifs for skill reflection:
field canonicalization, explicit token maps, stateful aggregation, duplicate
resolution, and order strategy. Selection fixtures will recombine those
motifs in nearby but not identical schemas. Test fixtures will use more novel
domains while following the same broad principles.

## Code Repair Changes

Each code-repair task will require algorithmic edge handling rather than a
single obvious operator change. The new contracts will combine two or more of
these behaviors:

- Boundary cases such as empty input, singleton input, negative values, zero,
  repeated values, or very large values.
- Stable tie-break ordering for equal scores or frequencies.
- Input normalization before computation.
- Malformed input defense where the contract specifies skip/default behavior.
- No mutation of caller-owned inputs.
- Idempotence across repeated calls.
- Deterministic output ordering for sets, maps, and equivalent candidates.
- Overlap, containment, adjacency, or nesting behavior for interval-like tasks.
- Tokenizer/parser corner cases such as whitespace, punctuation, unit aliases,
  and invalid tokens.

Train fixtures will expose reusable repair lessons like stable tie breaks,
non-mutating transforms, explicit parser tables, and boundary-condition guards.
Selection will combine familiar lessons with new surface names. Test will
include less familiar domains and stricter hidden edge cases.

## Per-Split Difficulty

- `train`: difficult enough to teach useful skill edits, with visible tests
  showing representative complexity.
- `selection`: difficult enough to distinguish parent and candidate skills,
  with hidden tests that catch generic advice and incomplete procedures.
- `test`: difficult enough to measure final generalization, with no need to
  support current loop adoption.

## Validation

After fixture edits:

- Run `uv run pytest`.
- Run `uv run ruff check .`.
- Prepare and grade every fixture task from both tracks and all splits.
- Confirm prepared workspaces still exclude `tests_hidden`.
- Confirm fixture tests remain inside `tests_visible` and `tests_hidden` and
  no verifier command changes were made.

## Risks

- If visible tests are too weak, the harder hidden tests become unfair rather
  than discriminating. Mitigation: every hard behavior must be stated in
  `task.json`, and visible tests must show the main family of behavior.
- If every task becomes too large, repairers may fail for reasons unrelated to
  skill quality. Mitigation: keep each task focused on one public function and
  two or three interacting edge behaviors.
- If train, selection, and test become too similar, the loop may overfit.
  Mitigation: reuse behavioral motifs but vary domain names, field names, and
  combinations across splits.
