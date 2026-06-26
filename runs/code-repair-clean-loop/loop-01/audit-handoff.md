# loop-01 Auditor Handoff

## Scope

- Experiment dir: `runs/code-repair-clean-loop`
- Loop id: `loop-01`
- Track: `code_repair`
- Rollout isolation mode: `independent`

## Key artifacts

- Initial baseline: `runs/code-repair-clean-loop/initial-baseline.md`
- Current best: `runs/code-repair-clean-loop/current-best.md`
- Best skill: `runs/code-repair-clean-loop/best-skill.md`
- Parent skill snapshot: `runs/code-repair-clean-loop/loop-01/parent-skill.md`
- Candidate skill: `runs/code-repair-clean-loop/loop-01/candidate-skill.md`
- Train rollouts copied by loop-run: `runs/code-repair-clean-loop/loop-01/rollouts/train-rollouts.jsonl`
- Reflect protocol: `runs/code-repair-clean-loop/loop-01/reflect-protocol.md`
- Train trajectories: `runs/code-repair-clean-loop/loop-01/train-trajectories.md`
- Rejected edit memory: `runs/code-repair-clean-loop/loop-01/rejected-edit-memory.md`
- Edit proposals: `runs/code-repair-clean-loop/loop-01/edit-proposals.json`
- Reflected edits: `runs/code-repair-clean-loop/loop-01/reflected-edits.json`
- Aggregated edits: `runs/code-repair-clean-loop/loop-01/aggregated-edits.json`
- Selected edits: `runs/code-repair-clean-loop/loop-01/selected-edits.json`
- Update report: `runs/code-repair-clean-loop/loop-01/update-report.json`
- Parent selection records: `runs/code-repair-clean-loop/loop-01/parent-selection.jsonl`
- Candidate selection records: `runs/code-repair-clean-loop/loop-01/candidate-selection.jsonl`
- Gate decision: `runs/code-repair-clean-loop/loop-01/gate-decision.json`
- Decision markdown: `runs/code-repair-clean-loop/loop-01/decision.md`
- Full loop manifest: `runs/code-repair-clean-loop/loop-01/full-loop-manifest.json`

## Timeline

1. Read only the allowed exact start files: loop skill, auditor prompt, target repairer prompt, and `runs/code-repair-clean-loop/current-best.md`.
2. Created `runs/code-repair-clean-loop/loop-01/parent-skill.md` from current-best.
3. Used `uv run skillopt-harness list-tasks --track code_repair --split train`.
4. Prepared train workspaces only with `prepare-task ... --split train`.
5. Read train prepared workspace metadata, entrypoints, and visible tests only.
6. Repaired train workspaces and graded them into `runs/code-repair-clean-loop/loop-01/train-rollouts.jsonl`.
7. Wrote `reflect-protocol.md`, `train-trajectories.md`, and `rejected-edit-memory.md`.
8. Wrote train-only `edit-proposals.json`, selected edit budget 2.
9. Generated `candidate-skill.md` and `update-report.json`; validation passed before any selection evidence was read.
10. First selection evidence became visible only after candidate skill generation and update validation.
11. Prepared matching parent and candidate selection workspaces in the same task order.
12. Spawned independent parent repairer session `019f036c-5854-7681-84f5-47c9b37db7a6` with only parent skill/workspaces.
13. Spawned independent candidate repairer session `019f036c-8698-78d0-8f13-d9610c44c75c` with only candidate skill/workspaces.
14. Parent repairer completed with score sequence `1.0, 0.0, 0.0, 1.0, 1.0`.
15. Candidate repairer completed with score sequence `1.0, 1.0, 1.0, 1.0, 1.0`.
16. Verified parent and candidate selection record order matched.
17. Ran `loop-run` with `--rollout-isolation independent`; it returned `accept_new_best`, parent score `0.6`, candidate score `1.0`, leakage `clean`.
18. First independent audit rejected because this handoff incorrectly named missing `loop-01/selection/...` record paths even though `gate-decision.json` named `loop-01/parent-selection.jsonl` and `loop-01/candidate-selection.jsonl`.
19. `current-best.md` and `best-skill.md` were restored to `loop-01/parent-skill.md` before any re-audit.
20. Gate artifacts were regenerated with the same fixed candidate and same staged selection inputs, and this handoff was corrected to the actual copied record paths.

## Independence evidence

- Parent repairer session: `019f036c-5854-7681-84f5-47c9b37db7a6`
- Candidate repairer session: `019f036c-8698-78d0-8f13-d9610c44c75c`
- Auditor session: to be created independently with `fork_context=false`
- Parent and candidate repairers were fresh-context subagents and were explicitly prohibited from reading the other branch's skill, workspace, records, or verifier output.
- Candidate repairer was already running independently before parent result was visible to the coordinating agent; no parent output was sent to candidate.

## Pre-proposal exploration note

Before candidate proposal, no repository-wide discovery command was used. No `rg --files`, `find .`, `tree`, broad `ls`, or broad grep/search was run. Selection/test evidence was not read before candidate generation.

## Post-proposal schema note

After candidate generation and selection rollouts, `loop-run` required a top-level `edits` list in `edit-proposals.json`. The already-selected proposal entries were duplicated into `edits` for harness parsing only; candidate text, edit ranking, and selection were unchanged.

## First audit cleanup note

Independent auditor session `019f0377-f54c-73e0-a9f3-ceed1e101e96` rejected the first audit because the handoff declared missing selection record paths. Required cleanup was performed by restoring `runs/code-repair-clean-loop/current-best.md` and `runs/code-repair-clean-loop/best-skill.md` from `runs/code-repair-clean-loop/loop-01/parent-skill.md`. The corrected re-audit should use the actual selection record paths above.
