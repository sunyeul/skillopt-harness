# SkillOpt MVP Harness

This repository contains a small manual SkillOpt harness with two tracks:
`code_repair` and `data_normalization`. Codex stays outside the Python harness;
the harness provides task workspaces, grading, and score records.

The current project skills are:

- `.codex/skills/code-repair/SKILL.md`
- `.codex/skills/data-normalization/SKILL.md`
- `.codex/skills/skillopt-loop/SKILL.md`

Reusable weak baselines for MVP loop-validation experiments live in:

- `examples/baselines/code-repair-weak-baseline.md`
- `examples/baselines/data-normalization-weak-baseline.md`

The current subagent prompt is:

- `.codex/subagents/skill-loop-auditor.md`

## Quick Start

Code repair:

```bash
uv run skillopt-harness list-tasks --track code_repair --split train
uv run skillopt-harness prepare-task --track code_repair --task train-addition-bug --split train --output workspaces/code_repair/train-addition-bug
uv run skillopt-harness grade-task --track code_repair --workspace workspaces/code_repair/train-addition-bug --output runs/code-repair-manual.jsonl
```

Data normalization:

```bash
uv run skillopt-harness list-tasks --track data_normalization --split train
uv run skillopt-harness prepare-task --track data_normalization --task data-train-normalize-contacts --split train --output workspaces/data_normalization/data-train-normalize-contacts
```

Repair the prepared function, then grade:

```bash
uv run skillopt-harness grade-task --track data_normalization --workspace workspaces/data_normalization/data-train-normalize-contacts --output runs/data-normalization-manual.jsonl
```

`prepare-task` writes `.skillopt-task.json` into each workspace so grading
records the track, split, task id, description, and source fixture path.

## Tracks

- `code_repair`: pytest-based code repair tasks under `fixtures/code_repair`.
  Prepared workspaces include visible tests only; hidden tests stay in the
  source fixture and are copied into a temporary grading workspace by
  `grade-task`.
- `data_normalization`: pytest-based data cleanup and transformation tasks
  under `fixtures/data_normalization`. Prepared workspaces include visible
  tests only; hidden tests stay in the source fixture and are copied into a
  temporary grading workspace by `grade-task`.

Each track has `train`, `selection`, and `test` splits. The SkillOpt loop skill
uses train evidence for candidate edits, selection scores for strict
accept/reject, and test scores only for final reporting.

## SkillOpt Loop Artifacts

The Python harness does not call Codex or any optimizer model. Run target-model
rollouts and optimizer reflection outside the harness, then store the resulting
records through the loop commands.

For the normal manual workflow, use `loop-run` after you have train rollout
records, reflected edit proposals, and independent parent/candidate selection
records:

```bash
uv run skillopt-harness loop-run \
  --track code_repair \
  --experiment-dir runs/my-experiment \
  --loop-id loop-01 \
  --initial-skill .codex/skills/code-repair/SKILL.md \
  --rollout-records runs/my-experiment/loop-01/train-rollouts.jsonl \
  --edit-proposals runs/my-experiment/loop-01/edit-proposals.json \
  --edit-budget 2 \
  --parent-selection-records runs/my-experiment/loop-01/parent-selection.jsonl \
  --candidate-selection-records runs/my-experiment/loop-01/candidate-selection.jsonl
```

`loop-run` initializes immutable lineage files when needed, snapshots
`current-best.md` as the loop parent, preserves rollout and reflection
artifacts, aggregates/selects/applies candidate edits, then gates the candidate
with strict selection improvement. Accepted candidates update
`current-best.md`; `best-skill.md` updates only when the candidate also beats
the supplied best score. Pass `--contaminated` to force rejection when split
discipline was violated.

The command writes `full-loop-manifest.json`, `gate-decision.json`, and
`decision.md` in the loop directory with one of `accept_new_best`, `accept`, or
`reject`.

For 2 to 4 epoch experiments, use `epoch-run` with a JSON file that names the
already prepared external artifacts for each epoch:

```bash
uv run skillopt-harness epoch-run \
  --track code_repair \
  --experiment-dir runs/my-experiment \
  --initial-skill .codex/skills/code-repair/SKILL.md \
  --epoch-inputs runs/my-experiment/epoch-inputs.json \
  --edit-budget 2
```

`epoch-inputs.json` may be either a list or an object with an `epochs` list:

```json
{
  "epochs": [
    {
      "epoch_id": "epoch-01",
      "rollout_records": ["runs/my-experiment/epoch-01/train-rollouts.jsonl"],
      "edit_proposals": "runs/my-experiment/epoch-01/edit-proposals.json",
      "parent_selection_records": "runs/my-experiment/epoch-01/parent-selection.jsonl",
      "candidate_selection_records": "runs/my-experiment/epoch-01/candidate-selection.jsonl",
      "slow_update": "runs/my-experiment/epoch-01/slow-update.md",
      "meta_skill": "runs/my-experiment/epoch-01/meta-skill.md"
    },
    {
      "epoch_id": "epoch-02",
      "rollout_records": ["runs/my-experiment/epoch-02/train-rollouts.jsonl"],
      "edit_proposals": "runs/my-experiment/epoch-02/edit-proposals.json",
      "parent_selection_records": "runs/my-experiment/epoch-02/parent-selection.jsonl",
      "candidate_selection_records": "runs/my-experiment/epoch-02/candidate-selection.jsonl",
      "slow_update": "runs/my-experiment/epoch-02/slow-update.md",
      "meta_skill": "runs/my-experiment/epoch-02/meta-skill.md"
    }
  ]
}
```

Each epoch runs the same manual `rollout → reflect → aggregate → select →
update → gate` artifact workflow. At the end of every epoch, `slow-update.md`
records momentum or long-horizon lessons, and `meta-skill.md` records optimizer
working memory for the next epoch. These files are copied into the epoch
directory and included in `multi-epoch-manifest.json`; they do not cause the
harness to call Codex or an optimizer.

## Development

```bash
uv run pytest
uv run ruff check .
```

Or use Task:

```bash
task init
task list TRACK=code_repair SPLIT=train
task list TRACK=data_normalization SPLIT=train
task prepare TRACK=data_normalization TASK=data-train-normalize-contacts
task grade TRACK=data_normalization TASK=data-train-normalize-contacts
task loop-run
task epoch-run
task check
```
