# Data Normalization SkillOpt Loop Report

## Summary

- Track: `data_normalization`
- Experiment dir: `runs/data-normalization-skillopt-20260627`
- Loop id: `loop-01`
- Parent skill: `runs/data-normalization-skillopt-20260627/loop-01/parent-skill.md`
- Candidate skill: `runs/data-normalization-skillopt-20260627/loop-01/candidate-skill.md`
- Decision: `accept_new_best`
- Leakage status: `clean`
- Rollout isolation: `independent`

The loop accepted a candidate generated from train-only evidence. The candidate
adds one Procedure instruction requiring canonical scalar key helpers before
grouping, deduplication, revision handling, or output-key storage.

## Scores

| Split | Parent/current-best | Candidate | Delta | Gate use |
|---|---:|---:|---:|---|
| Train rollout | `3/5 = 0.600` | not separately measured | n/a | reflection only |
| Selection | `4/5 = 0.800` | `5/5 = 1.000` | `+1/5 = +0.200` | adoption gate |
| Test reporting | `3/5 = 0.600` | `3/5 = 0.600` | `0/5 = 0.000` | reporting only |

The selection gate satisfied strict improvement because candidate selection
score was greater than parent/current-best selection score. Test scores were
measured only after adoption and did not influence the gate.

## Evidence

- Train rollouts: `runs/data-normalization-skillopt-20260627/loop-01/train-rollouts.jsonl`
- Reflect protocol: `runs/data-normalization-skillopt-20260627/loop-01/reflect-protocol.md`
- Train trajectories: `runs/data-normalization-skillopt-20260627/loop-01/train-trajectories.md`
- Edit proposals: `runs/data-normalization-skillopt-20260627/loop-01/edit-proposals.json`
- Update report: `runs/data-normalization-skillopt-20260627/loop-01/update-report.json`
- Parent selection records: `runs/data-normalization-skillopt-20260627/loop-01/parent-selection.jsonl`
- Candidate selection records: `runs/data-normalization-skillopt-20260627/loop-01/candidate-selection.jsonl`
- Gate decision: `runs/data-normalization-skillopt-20260627/loop-01/gate-decision.json`
- Full loop manifest: `runs/data-normalization-skillopt-20260627/loop-01/full-loop-manifest.json`
- Test reporting records:
  - `runs/data-normalization-skillopt-20260627/loop-01/baseline-test-reporting-only.jsonl`
  - `runs/data-normalization-skillopt-20260627/loop-01/candidate-test-reporting-only.jsonl`
- Independent audit: `runs/data-normalization-skillopt-20260627/loop-01/audit-result.md`

## Train-Only Rationale

The train rollout showed two failures in the parent repair behavior:

- `data-train-active-skus`: raw SKU casing was used as a duplicate key, so
  `a-1` and `A-1` were not resolved through one normalized winner.
- `data-train-group-orders`: a malformed nested customer dict without `id`
  reached dictionary membership as an unhashable grouping key.

The selected edit generalizes those train-only lessons into a small procedural
instruction: build one canonical scalar key helper before dict/set storage,
lowercase when normalized or case-insensitive keys are required, and reject
missing, blank, dict, list, or malformed key values.

## Isolation

- Parent selection repairer: `019f0a03-0db6-75f3-b7b4-ddbb9b8820fb`
  (`Wegener`)
- Candidate selection repairer: `019f0a03-33c6-7120-ae90-9c46914b07ee`
  (`Godel`)
- Independent auditor: `019f0a07-7af3-7221-91d9-8f2e7c33500a`
  (`Schrodinger`)
- Parent test reporting repairer:
  `019f0a09-51dc-7ed1-9c58-00f9c4a18595` (`Heisenberg`)
- Candidate test reporting repairer:
  `019f0a09-77ef-7a80-a4ab-2991bfa605f8` (`Linnaeus`)

Parent and candidate repairers used fresh subagent contexts with
`fork_context=false`, were assigned exactly one skill path, and were instructed
not to read the other branch's skill, workspaces, records, or verifier output.
Hidden tests were not read directly.

## Verification

- `uv run pytest`: `30 passed`
- `uv run ruff check .`: `All checks passed`

## Notes

Existing dirty README, fixture, harness, and skill-loop documentation changes
were left untouched. This report and committed evidence are limited to the
`runs/data-normalization-skillopt-20260627` experiment artifacts.
