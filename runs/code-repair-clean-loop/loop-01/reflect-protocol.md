# loop-01 Reflect Protocol

## Train-only inputs

- Parent skill snapshot: `runs/code-repair-clean-loop/loop-01/parent-skill.md`
- Train task list from `uv run skillopt-harness list-tasks --track code_repair --split train`
- Prepared train workspaces under `workspaces/code_repair/train-loop-01/`
- Train source, `task.json`, `.skillopt-task.json`, and visible tests from those prepared workspaces
- Train grade records: `runs/code-repair-clean-loop/loop-01/train-rollouts.jsonl`

## Forbidden inputs

- Selection or test task names, descriptions, source, visible tests, hidden tests, verifier output, or task-specific failure patterns
- Repository-wide path discovery before candidate generation, including `rg --files`, `find .`, `tree`, broad `ls`, or broad grep/search
- Direct reads of hidden tests
- Edits to fixtures, verifier, split assignments, harness behavior, or the deployable `.codex/skills/code-repair/SKILL.md`

## Trajectory fields

For each train task, record the task contract, visible-test coverage, initial source behavior, repair action, verifier feedback, final score, and optimizer lesson.

## Proposal schema

Each proposal includes `id`, `op`, `target`, `content`, `score`, `rationale`, `evidence`, `support`, `behavioral_change`, `novelty_vs_parent`, `novelty_vs_rejected`, `mechanical_target`, and `leakage_check`.

## Scoring rubric

`score = 0.30 * train support across tasks + 0.25 * behavioral specificity + 0.20 * novelty vs parent + 0.15 * novelty vs rejected edits + 0.10 * mechanical applicability and low leakage risk`

Each dimension is scored from 0.0 to 1.0.

## Edit budget

Apply at most 2 selected edits.

## Tie-break rules

Sort by total score descending. Break ties by broader train support, then smaller skill diff, then clearer exact target.

## Rejection rules before gate

Reject proposals with vague targets, no behavioral change, non-unique exact targets, wrong-section insertion, leakage risk, or repeated rejected edit families without concrete behavioral novelty.
