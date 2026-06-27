# loop-01 Auditor Handoff

## Scope

- Experiment dir: `runs/data-normalization-skillopt-20260627`
- Loop id: `loop-01`
- Track: `data_normalization`
- Rollout isolation mode: `independent`

## Key artifacts

- Initial baseline: `runs/data-normalization-skillopt-20260627/initial-baseline.md`
- Current best: `runs/data-normalization-skillopt-20260627/current-best.md`
- Best skill: `runs/data-normalization-skillopt-20260627/best-skill.md`
- Parent skill snapshot: `runs/data-normalization-skillopt-20260627/loop-01/parent-skill.md`
- Candidate skill: `runs/data-normalization-skillopt-20260627/loop-01/candidate-skill.md`
- Train rollouts copied by loop-run: `runs/data-normalization-skillopt-20260627/loop-01/rollouts/train-rollouts.jsonl`
- Reflect protocol: `runs/data-normalization-skillopt-20260627/loop-01/reflect-protocol.md`
- Train trajectories: `runs/data-normalization-skillopt-20260627/loop-01/train-trajectories.md`
- Rejected edit memory: `runs/data-normalization-skillopt-20260627/loop-01/rejected-edit-memory.md`
- Edit proposals: `runs/data-normalization-skillopt-20260627/loop-01/edit-proposals.json`
- Reflected edits: `runs/data-normalization-skillopt-20260627/loop-01/reflected-edits.json`
- Aggregated edits: `runs/data-normalization-skillopt-20260627/loop-01/aggregated-edits.json`
- Selected edits: `runs/data-normalization-skillopt-20260627/loop-01/selected-edits.json`
- Update report: `runs/data-normalization-skillopt-20260627/loop-01/update-report.json`
- Parent selection records: `runs/data-normalization-skillopt-20260627/loop-01/parent-selection.jsonl`
- Candidate selection records: `runs/data-normalization-skillopt-20260627/loop-01/candidate-selection.jsonl`
- Gate decision: `runs/data-normalization-skillopt-20260627/loop-01/gate-decision.json`
- Decision markdown: `runs/data-normalization-skillopt-20260627/loop-01/decision.md`
- Full loop manifest: `runs/data-normalization-skillopt-20260627/loop-01/full-loop-manifest.json`
- Test reporting records:
  - `runs/data-normalization-skillopt-20260627/loop-01/baseline-test-reporting-only.jsonl`
  - `runs/data-normalization-skillopt-20260627/loop-01/candidate-test-reporting-only.jsonl`

## Timeline

1. Read only the allowed start files: loop instructions, AGENTS.md,
   `skillopt.yaml`, lineage files, and auditor prompt.
2. Confirmed retained lineage files:
   `initial-baseline.md`, `current-best.md`, and `best-skill.md`.
3. Created `runs/data-normalization-skillopt-20260627/loop-01/parent-skill.md`
   from current-best.
4. Used `uv run skillopt-harness list-tasks --track data_normalization --split train`.
5. Prepared train workspaces only with `prepare-task ... --split train`.
6. Read train prepared workspace task metadata, entrypoints, and visible tests
   only.
7. Repaired train workspaces and graded them into
   `runs/data-normalization-skillopt-20260627/loop-01/train-rollouts.jsonl`.
8. Wrote `reflect-protocol.md`, `train-trajectories.md`, and
   `rejected-edit-memory.md`.
9. Wrote train-only `edit-proposals.json`, selected edit budget 2.
10. Generated `candidate-skill.md` and `update-report.json`; validation passed
    before any selection evidence was read.
11. First selection evidence became visible only after candidate skill
    generation and update validation.
12. Spawned independent parent repairer session
    `019f0a03-0db6-75f3-b7b4-ddbb9b8820fb` with only parent skill/workspaces.
13. Spawned independent candidate repairer session
    `019f0a03-33c6-7120-ae90-9c46914b07ee` with only candidate
    skill/workspaces.
14. Parent repairer completed selection with score sequence
    `1.0, 1.0, 0.0, 1.0, 1.0`.
15. Candidate repairer completed selection with score sequence
    `1.0, 1.0, 1.0, 1.0, 1.0`.
16. Verified parent and candidate selection record order matched.
17. Independent auditor session `019f0a07-7af3-7221-91d9-8f2e7c33500a`
    returned `accept_new_best`, `clean`, blocking condition `none`.
18. Ran `loop-run` with `--rollout-isolation independent`; it returned
    `accept_new_best`, parent score `0.8`, candidate score `1.0`, leakage
    `clean`.
19. After adoption, spawned independent parent and candidate test reporting
    repairers. Test scores were recorded only for post-hoc reporting.
20. Parent/current-best test reporting score was `3/5`; accepted candidate test
    reporting score was `3/5`; test delta was `0`.

## Independence evidence

- Parent selection repairer session: `019f0a03-0db6-75f3-b7b4-ddbb9b8820fb`
- Candidate selection repairer session: `019f0a03-33c6-7120-ae90-9c46914b07ee`
- Auditor session: `019f0a07-7af3-7221-91d9-8f2e7c33500a`
- Parent test reporting repairer session: `019f0a09-51dc-7ed1-9c58-00f9c4a18595`
- Candidate test reporting repairer session: `019f0a09-77ef-7a80-a4ab-2991bfa605f8`
- Parent and candidate repairers were fresh-context subagents and were
  explicitly prohibited from reading the other branch's skill, workspace,
  records, or verifier output.

## Pre-proposal exploration note

Before candidate proposal, no repository-wide discovery command was used. No
`rg --files`, `find .`, `tree`, broad `ls`, or broad grep/search exposed
selection or test evidence. Selection/test evidence was not read before
candidate generation.

## Test reporting note

Test split records were produced only after selection adoption. They are
reporting-only evidence and did not affect candidate acceptance, rejection,
ranking, repair behavior, or skill text.
