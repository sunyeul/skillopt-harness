---
name: skillopt-loop
description: Use when running or auditing a manual SkillOpt improvement loop in this harness.
---

# SkillOpt Loop Skill

Use this skill to run or audit one manual SkillOpt-style improvement loop
without turning the Python harness into an automatic agent runner.

## Core Rule

The only trainable deployable artifact is skill text. The code harness,
fixtures, verifier command, split assignments, and external target repair
workflow stay fixed during a loop.

Within one experiment, the initial baseline skill is immutable. Accepted
candidates update `current-best.md`, and `current-best.md` becomes the next
loop's parent skill.

## Invocation Contract

Each loop run must resolve these inputs before reading task evidence:

- `TRACK`: required. If the user did not provide it, ask. Do not infer it from
  recent conversation, skill names, fixture paths, or experiment history.
- `EXPERIMENT_DIR`: required unless the user explicitly asks only for an audit
  of existing loop artifacts. If missing, ask or choose a clearly labeled
  throwaway path only when the user asked for exploration, not adoption.
- `LOOP_ID`: default to the next obvious loop id for the experiment, such as
  `loop-01`, only after checking existing loop artifact names.

Resolve the target skill, evaluator command, and train/selection/test split
paths from `skillopt.yaml` using `tracks[TRACK]`. The skill must not assume a
track such as code repair or data normalization, and must not hardcode target
skill or fixture paths except as a fallback after reading `skillopt.yaml`.

Reading `skillopt.yaml`, this skill file, the auditor prompt, and existing
lineage artifacts for the requested experiment is allowed during preflight.
Listing task ids, task metadata, fixture directories, source files, visible
tests, hidden tests, or verifier output is governed by split discipline below.

## Split Discipline

- Use train evidence only to propose candidate skill edits.
- Use selection evidence only to accept or reject a candidate skill.
- Use test evidence only after final adoption for reporting.
- Quantitative adoption improvement is determined on selection only. Do not use
  test scores to accept, reject, tune, or re-rank a candidate.
- After adoption, measuring the initial baseline or parent on test is allowed
  only as post-hoc reporting of effect size. When test is measured, compare the
  immutable initial baseline or loop parent against the accepted candidate or
  current-best on the same test tasks, label the comparison clearly as
  reporting-only, keep it out of all adoption decisions, and do not use it as
  evidence for later candidate edits.
- Do not inspect hidden test files directly. Hidden tests are observed only
  through `grade-task` scores and verifier output.
- Candidate skill text and candidate selection repairs must both stay isolated
  from selection/test-derived insight except for final accept/reject scoring.
- If selection or test evidence was seen before candidate proposal, mark the
  loop contaminated and do not adopt the candidate.
- If parent selection verifier output, including hidden-test-derived failure
  details, was seen before candidate selection repairs finished in the same
  session or shared context, mark the loop contaminated and do not adopt the
  candidate.

## Split-Clean Preflight

Before any candidate proposal, use an allowlist reading posture. Read only exact
paths required to start the loop, such as the loop skill, auditor prompt,
parent skill, experiment artifacts, and train-only prepared workspaces.

- Do not run repository-wide discovery commands before candidate generation,
  including `rg --files`, `find .`, `tree`, broad `ls`, or broad grep/searches.
  Path names alone can expose selection or test split information.
- List and prepare tasks only through train-scoped harness commands, with
  `--split train` explicitly supplied.
- If a command or tool output exposes selection or test paths, metadata, task
  names, scores, verifier output, or diagnostics before candidate proposal,
  stop immediately and record the loop as contaminated with the first blocking
  reason.
- If contamination is detected before code, fixture, verifier, harness, or
  deployable skill changes, record the rejection and stop. Do not run
  `pytest`, `ruff`, or other handoff verification solely for that aborted loop.

## Full-Loop Workflow

Run the loop with prepared external artifacts; do not ask the harness to call
Codex, target models, or optimizer models.

1. Baseline / lineage: ensure `<experiment-dir>/initial-baseline.md`,
   `<experiment-dir>/current-best.md`, and `<experiment-dir>/best-skill.md`.
2. Rollout: gather train trajectories, including task metadata, reasoning or
   action traces when available, tool calls, verifier feedback, final scores,
   and success/failure patterns.
3. Reflect: use optimizer-model analysis outside the Python harness to propose
   skill edits grounded only in train evidence. Record the reflection protocol,
   rejected-edit memory, trajectory analysis, and scoring rubric before writing
   the candidate.
4. Aggregate / Select: merge duplicate add/delete/replace proposals, then rank
   and keep only the top edits allowed by the edit budget.
5. Update: apply selected bounded edits to produce `<loop-dir>/candidate-skill.md`.
6. Validation Gate: compare parent and candidate selection records; accept only
   if `candidate_score > parent_score` and the run is not contaminated.
7. Final Report: after adoption, measure the accepted current-best on test and,
   when possible, measure the immutable initial baseline or loop parent on the
   same test tasks for post-hoc effect-size reporting. Record baseline test
   score, candidate/current-best test score, and test delta; this must not
   change the gate decision or feed any later skill edit.

Reject ties, regressions, missing scores, contaminated runs, or runs with
changed harness/fixture/verifier behavior.

Gate rollout must use role isolation. Run parent selection repairs with a
parent repairer that receives only the parent skill, candidate selection repairs
with a candidate repairer that receives only the candidate skill, and audit with
an independent auditor. If parent and candidate repairs happen in one shared
context, or if the assigned skill boundary is unclear, mark the rollout
contaminated and reject.

## Reflect Discipline

Reflection is the optimizer step. Make it reproducible enough that another
agent can understand why the same train evidence would lead to the same edit
family.

Before proposing edits, write or verify these loop artifacts:

- `reflect-protocol.md`: train-only inputs, forbidden inputs, trajectory fields,
  proposal schema, scoring rubric, edit budget, and tie-break rules.
- `train-trajectories.md` or equivalent structured records: task contract,
  visible-test coverage, source behavior, repair action, verifier feedback,
  final score, and success/failure lesson for each train task.
- `rejected-edit-memory.md` when prior rejected candidates exist: only prior
  edit text, proposal family, gate-level decision, and reject reason. Do not
  include task-specific selection failures, hidden-derived diagnostics, or test
  evidence.

Use rejected-edit memory as negative optimizer feedback. Do not repeat an edit
family that previously tied, regressed, or was contaminated unless the new edit
changes the repair procedure in a concrete and observable way. Rewording the
same advice is not a new proposal.

Each proposal must explain:

- `support`: which train tasks support it and whether support is from success,
  failure, or latent risk.
- `behavioral_change`: what the target agent will do differently.
- `novelty_vs_parent`: why this is not already covered by the parent skill.
- `novelty_vs_rejected`: why this is not a repeat of a rejected edit family.
- `mechanical_target`: the exact skill text to match and intended insertion
  section.
- `leakage_check`: confirmation that evidence is train-only.

Score proposals with a fixed rubric recorded in `reflect-protocol.md`. Prefer a
rubric shaped like:

```text
score =
  0.30 * train support across tasks
+ 0.25 * behavioral specificity
+ 0.20 * novelty vs parent
+ 0.15 * novelty vs rejected edits
+ 0.10 * mechanical applicability and low leakage risk
```

Select by score descending. Break ties by broader train support, then smaller
skill diff, then clearer exact target. Do not select proposals with vague
targets, no behavioral change, or only a restatement of previously rejected
guidance.

## Update Validation

Candidate generation must be mechanically checked before the gate:

- Every selected edit must use an exact `target` string that occurs once in the
  parent skill, unless `position` is `end`.
- Additions intended for `## Rules` must land inside that section, not after
  `## Final Response`.
- `update-report.json` must record applied edits and failures.
- If any selected edit lands in the wrong section, silently appends because the
  target was vague, or changes unselected text, reject the candidate before
  selection grading and record the reason.

## Multi-Epoch Workflow

For deeper manual SkillOpt runs, use 2 to 4 epochs. Each epoch contains one
full `rollout → reflect → aggregate → select → update → gate` pass. After the
gate, record two extra epoch-end artifacts:

- `slow-update.md`: momentum or long-horizon lessons compressed from the epoch.
  This is not deployable skill text and must not overwrite `current-best.md`.
- `meta-skill.md`: optimizer working memory for the next epoch. This may guide
  the next epoch's reflection process, but it must not contain selection/test
  leakage.

The harness command for this shape is `epoch-run`, which accepts a JSON file of
2 to 4 prepared epoch inputs and writes `multi-epoch-manifest.json`. The Python
harness still does not call Codex, target models, or optimizer models.

Within a multi-epoch run, `current-best.md` may update only through an accepted
epoch gate. The next epoch's `parent-skill.md` is the then-current best skill.
If an epoch is rejected or contaminated, the next epoch's parent remains the
previous current best.

During the gate, do not let parent selection failure output teach the candidate
rollout. Use one of these clean patterns:

- Complete both parent and candidate selection repairs before viewing either
  verifier output, and record that this was the chosen isolation mode.
- Run parent and candidate selection rollouts in independent sessions that do
  not share selection failure context.
- Use redacted grading output while repairing, so only scores/return codes are
  visible and full verifier output stays in records for audit.

If a parent selection verifier failure is already visible and candidate
selection repair work remains, stop and mark the loop contaminated.

For strict runs, prefer `.codex/subagents/skill-target-repairer.md` for parent
and candidate selection repairs. Record the repairer session/thread id, assigned
skill path, workspace path, score record path, and isolation mode. Do not accept
a candidate when rollout isolation is `unknown`.

## Lineage Artifacts

| Artifact | Location | Rule |
|---|---|---|
| `initial_baseline` | `<experiment-dir>/initial-baseline.md` | Created once; never overwritten. |
| `current_best` | `<experiment-dir>/current-best.md` | Updated only by accepted candidates. |
| `best_skill` | `<experiment-dir>/best-skill.md` | Updated only by `accept_new_best`. |
| `parent_skill` | `<loop-dir>/parent-skill.md` | Snapshot of current best at loop start. |
| `candidate_skill` | `<loop-dir>/candidate-skill.md` | Generated from selected edits. |
| gate decision | `<loop-dir>/gate-decision.json` and `decision.md` | Records scores, leakage, and decision. |
| `slow_update` | `<epoch-dir>/slow-update.md` | Epoch-end long-horizon lesson compression; never deploy directly. |
| `meta_skill` | `<epoch-dir>/meta-skill.md` | Optimizer working memory for the next epoch; must stay split-clean. |
| `reflect_protocol` | `<loop-dir>/reflect-protocol.md` | Reproducible optimizer inputs, scoring, and selection rules. |
| `rejected_edit_memory` | `<loop-dir>/rejected-edit-memory.md` | Gate-level memory of prior rejected edit families, without selection diagnostics. |
| `train_trajectories` | `<loop-dir>/train-trajectories.md` or JSONL | Train-only trajectory analysis used for reflection. |

## Edit Proposal Schema

Represent reflection output as structured edit proposals:

- `add`: add new skill text at `position` `before`, `after`, or `end`.
- `delete`: remove exactly matched target skill text.
- `replace`: replace exactly matched target skill text with new content.

Each proposal should include `id`, `op`, `target`, `content` when applicable,
`score`, `rationale`, `evidence`, `support`, `behavioral_change`,
`novelty_vs_parent`, `novelty_vs_rejected`, `mechanical_target`, and
`leakage_check`. The edit budget is the textual learning rate: the maximum
number of edits applied in one update step.

## Harness Command

Use the single public loop command:

```bash
uv run skillopt-harness loop-run \
  --track "$TRACK" \
  --experiment-dir "$EXPERIMENT_DIR" \
  --loop-id "$LOOP_ID" \
  --initial-skill "$TARGET_SKILL" \
  --rollout-records "$EXPERIMENT_DIR/$LOOP_ID/train-rollouts.jsonl" \
  --edit-proposals "$EXPERIMENT_DIR/$LOOP_ID/edit-proposals.json" \
  --edit-budget 2 \
  --parent-selection-records "$EXPERIMENT_DIR/$LOOP_ID-inputs/parent-selection.jsonl" \
  --candidate-selection-records "$EXPERIMENT_DIR/$LOOP_ID-inputs/candidate-selection.jsonl" \
  --baseline-test-records "$EXPERIMENT_DIR/$LOOP_ID-inputs/baseline-test.jsonl" \
  --candidate-test-records "$EXPERIMENT_DIR/$LOOP_ID-inputs/candidate-test.jsonl" \
  --rollout-isolation independent
```

Write parent and candidate selection records to a staging directory such as
`<experiment-dir>/<loop-id>-inputs/`. `loop-run` copies those records into the
loop artifact directory. This avoids treating generated loop artifacts as
rollout inputs and prevents same-file copy mistakes.

The `--baseline-test-records` and `--candidate-test-records` inputs are
optional and must be supplied together. They are reporting-only post-adoption
comparisons: `loop-run` records `baseline_test_score`, `candidate_test_score`,
and `test_delta` in `gate-decision.json`, `decision.md`, and
`full-loop-manifest.json`, but selection remains the only adoption gate.

For 2 to 4 epoch runs:

```bash
uv run skillopt-harness epoch-run \
  --track "$TRACK" \
  --experiment-dir "$EXPERIMENT_DIR" \
  --initial-skill "$TARGET_SKILL" \
  --epoch-inputs "$EXPERIMENT_DIR/epoch-inputs.json" \
  --edit-budget 2
```

Each item in `epoch-inputs.json` must include `edit_proposals`,
`parent_selection_records`, `candidate_selection_records`, `slow_update`, and
`meta_skill`. It may include `epoch_id`, `rollout_records`, `edit_budget`,
`best_selection_records`, `contaminated`, `contamination_reason`, and
`rollout_isolation`.

Add `--best-selection-records` when comparing against a prior best score. Add
`--contaminated --contamination-reason "<reason>"` when split discipline was
violated; contaminated candidates must be rejected even when selection score
improves. Never use `--contaminated` without a concrete first blocking reason.

When grading selection workspaces during gate rollout, prefer:

```bash
uv run skillopt-harness grade-task \
  --track "$TRACK" \
  --workspace "$WORKSPACE" \
  --output "$EXPERIMENT_DIR/$LOOP_ID/parent-selection.jsonl" \
  --redact-output
```

`--redact-output` keeps full verifier stdout/stderr in the JSONL record but
prints only score, return code, timeout status, task metadata, and command to
the terminal.

## Preflight Checklist

- `runs/` contains only artifacts for the current intended experiment.
- Before candidate generation, no repository-wide file listing, broad search,
  or non-allowlisted fixture exploration exposed selection or test paths.
- Train rollout records do not include selection or test split evidence.
- `reflect-protocol.md` fixes the reflection inputs, scoring rubric, edit
  budget, and tie-break rules before candidate generation.
- Prior rejected edit families are captured in `rejected-edit-memory.md`
  without selection/test diagnostics, or the loop records why no such memory
  exists.
- Prior epoch memory may include only candidate edit text, proposal family,
  gate-level decision, aggregate scores, and reject reason. It must not include
  selection/test task names, task descriptions, source, visible tests, hidden
  diagnostics, or task-specific failure patterns.
- Edit proposals cite train tasks only.
- Edit proposals state behavioral novelty versus the parent skill and prior
  rejected edit families.
- Selected edits have exact mechanical targets and land in the intended skill
  section.
- Parent and candidate selection records cover the same selection tasks.
- Candidate skill text was generated before any selection/test evidence became
  visible.
- Candidate selection repairs were completed before parent selection verifier
  failure output became visible, or were performed in an independent context.
- Parent and candidate selection repairs were produced by isolated target
  repairers with explicit assigned skill paths. If not, mark the decision
  contaminated with `--contaminated` and `--contamination-reason`, or use
  `--rollout-isolation unknown` so the candidate cannot be accepted.
- No fixture, verifier, split assignment, or hidden test file was changed.

## Auditor Handoff

Before adopting a candidate, ask `.codex/subagents/skill-loop-auditor.md` to
audit the loop artifacts. Provide:

- `initial-baseline.md`, `current-best.md`, parent skill, and candidate skill.
- Train rollout records and reflected edit proposals.
- `reflect-protocol.md`, rejected-edit memory if present, and train trajectory
  analysis used by reflection.
- Parent and candidate selection records, plus best records if used.
- `full-loop-manifest.json`, `gate-decision.json`, and `decision.md`.
- Notes about independent vs in-session rollout, the evidence timeline, the
  first moment selection verifier output became visible, and any suspected
  leakage.
- Parent repairer, candidate repairer, and auditor session/thread ids or a
  concrete equivalent independence note. Self-audit alone is not sufficient for
  adoption.

## Common Mistakes

| Mistake | Correct response |
|---|---|
| Running partial legacy commands | Use `loop-run`; partial commands are not public workflow. |
| Treating a tie as success | Reject; strict improvement means `candidate_score > parent_score`. |
| Editing deployable skill before gate | Keep edits in `candidate-skill.md` until accepted. |
| Reusing selection/test insight in reflection | Mark contaminated and reject. |
| Using test baseline comparison to justify adoption | Keep adoption based on selection only; test baseline is post-hoc reporting-only. |
| Measuring only candidate test after adoption | Also measure immutable baseline or loop parent on the same test tasks when reporting test effect size. |
| Repeating a rejected edit family with new wording | Reject before gate unless the proposal has concrete behavioral novelty. |
| Scoring edits with an implicit or changing rubric | Write `reflect-protocol.md` first and reject proposals not scored by it. |
| Using descriptive targets like "after the rule ..." instead of exact text | Treat as mechanically invalid; regenerate the candidate before gate. |
| Letting a Rules edit append after `## Final Response` | Reject before gate; the candidate text was not generated as selected. |
| Running repo-wide discovery before proposal | Stop immediately; path names can leak selection/test evidence, so mark contaminated. |
| Running `pytest`/`ruff` after an early contamination abort | Skip handoff verification unless code, fixture, verifier, harness, deployable skill, or other deliverable files changed. |
| Repairing candidate selection after seeing parent selection hidden-derived failure output | Mark contaminated and reject, even if candidate score improves. |
| Calling a candidate clean because only the skill text was clean | Audit the candidate rollout too; contaminated rollout rejects the candidate. |
| Overwriting initial baseline | Restore it from the first experiment snapshot before continuing. |
| Letting one agent repair both parent and candidate selection workspaces | Mark contaminated unless both repairs were completed before any verifier output and the shared-context limitation is explicitly recorded. |
| Self-auditing an accepted candidate | Reject until an independent auditor or equivalent independent thread note is recorded. |

## Decision Record

Write or verify a concise decision record with:

- Initial baseline, parent/current-best, candidate, and best skill paths.
- Train evidence and reflected edit proposal paths.
- Reflect protocol, rejected-edit memory, and trajectory analysis paths.
- Parent, candidate, and best selection scores.
- Accepted current-best test score when measured, plus reporting-only
  baseline/parent test score and test delta when measured after adoption.
- Decision: `accept_new_best`, `accept`, or `reject`.
- Leakage status: `clean` or `contaminated`.
- Contamination reason when leakage status is `contaminated`.
- Evidence timeline, including whether candidate selection repairs were
  independent from parent selection verifier output.
- Rollout isolation mode: `independent`, `completed-before-output`,
  `redacted-in-session`, or `unknown`. `unknown` cannot be accepted.
- Required cleanup, especially if a rejected candidate reached a deployable
  skill file.
