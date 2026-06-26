# SkillOpt MVP Baseline and Fixture Design

## Purpose

The MVP validates the manual SkillOpt improvement loop. The main success case is
observing at least one target skill improve on the selection split after a
candidate edit derived only from train evidence. The secondary success case is
recording correct reject decisions for ties, regressions, missing scores, or
contaminated runs.

The MVP target tracks are:

- `code_repair`
- `data_normalization`

Both tracks use pytest-based fixtures with visible tests in prepared workspaces
and hidden tests restored only inside the grader's temporary verifier
workspace.

## Baseline Strategy

Keep repository skills usable. Use deliberately weak experiment baselines from
`examples/baselines/` when starting an MVP loop:

- `examples/baselines/code-repair-weak-baseline.md`
- `examples/baselines/data-normalization-weak-baseline.md`

Weak baselines should be incomplete, not absurd. They should omit specific
generalization behaviors that train evidence can reveal and candidate edits can
add.

## Fixture Strategy

Each track includes train, selection, and test splits with at least five tasks.
Train and selection should share transferable failure patterns while using
different surface details. Test remains reserved for post-adoption reporting.

Target score shape:

```text
parent selection:     2/5 or 3/5
candidate selection:  3/5 or 4/5
decision:             accept or accept_new_best
```

Reject records should also cover ties, regressions, missing scores, and
contamination.

## Code Repair Patterns

Code repair focuses on small Python function repairs. Its train fixtures now
include harder examples for:

- parsing tokens and invalid input
- stable frequency ordering and tie-breaking
- record normalization defaults and sorting
- boundary behavior
- simple arithmetic repair

Candidate edits should add a compact generalization checklist: read task text
for edge rules, preserve ordering semantics, handle repeated values
deliberately, and avoid overfitting to one visible assertion.

## Data Normalization Patterns

Data normalization focuses on records, flags, grouping, filtering, and stable
deduplication. Fixture families include:

- schema normalization with defaults
- boolean parsing from loose inputs
- grouping totals while ignoring rejected/cancelled rows
- first-seen deduplication after trimming/case normalization
- filtering active or published ids with stable output rules

Candidate edits should teach the agent to extract schema, default, ordering,
filtering, and normalization rules from `task.json` before editing.

## Loop Evidence Requirements

Train rollout records should include task id, split, parent skill path, visible
test or verifier output, final score, and a short failure analysis. Edit
proposals should cite train task ids only.

Selection records must cover the same selection tasks for parent and candidate.
Strict improvement means `candidate_score > parent_score`. Ties and contaminated
runs reject.

## Acceptance Criteria

The MVP is ready when at least one clean experiment satisfies:

- weak baseline is snapshotted as `initial-baseline.md`
- parent/current-best selection score is below perfect
- candidate skill is derived from train-only edit proposals
- candidate selection score is strictly higher than parent selection score
- `loop-run` records `accept` or `accept_new_best`
- `current-best.md` updates only after acceptance

The MVP should also demonstrate one protocol rejection where `current-best.md`
remains unchanged.

## Non-goals

- Do not make the harness call Codex.
- Do not optimize against hidden tests directly.
- Do not merge target tracks into one general task-solving skill.
- Do not treat perfect baseline scores as useful MVP evidence.
