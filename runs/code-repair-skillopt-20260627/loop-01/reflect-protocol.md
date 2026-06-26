# Reflect Protocol

## Inputs

- Parent skill: `runs/code-repair-skillopt-20260627/loop-01/parent-skill.md`
- Train rollouts: `runs/code-repair-skillopt-20260627/loop-01/train-rollouts-all.jsonl`
- Train workspace observations from prepared train workspaces only.

## Forbidden Inputs

- Selection or test task ids, metadata, source, visible tests, verifier output, scores, or diagnostics.
- Hidden test files from any split.
- Fixture, verifier, harness, or split-assignment edits.

## Trajectory Fields

- task id
- visible behavior that shaped the repair
- parent-skill instruction pressure
- repair action
- train grade score
- lesson for candidate text

## Proposal Schema

Each proposal records support, behavioral change, novelty versus parent,
novelty versus rejected edits, exact mechanical target, and leakage check.

## Scoring Rubric

score =
0.30 * train support across tasks +
0.25 * behavioral specificity +
0.20 * novelty versus parent +
0.15 * novelty versus rejected edits +
0.10 * mechanical applicability and low leakage risk

## Edit Budget

Apply at most two edits. Reject proposals with vague mechanical targets, no
behavioral change, or selection/test evidence.

## Tie Breaks

Break ties by broader train support, then smaller skill diff, then clearer
exact target.
