# Reflect Protocol

## Inputs

- Track: `data_normalization`
- Loop: `loop-01`
- Parent skill: `runs/data-normalization-skillopt-20260627/loop-01/parent-skill.md`
- Train rollout records: `runs/data-normalization-skillopt-20260627/loop-01/train-rollouts.jsonl`

Only train split task descriptions, prepared train source files, visible tests,
train repair actions, and train grade records are allowed. Selection and test
task evidence, task metadata, repair output, and verifier output are forbidden
until after candidate skill generation and mechanical validation.

## Trajectory Fields

- task id
- visible-test behavior implemented
- hidden/verifier feedback from train grade
- final train score
- success or failure lesson

## Proposal Schema

Each proposal records id, op, target, content, score, rationale, support,
behavioral change, novelty versus parent, novelty versus rejected edits,
mechanical target, and leakage check.

## Scoring Rubric

score =
0.30 * train support across tasks
+ 0.25 * behavioral specificity
+ 0.20 * novelty vs parent
+ 0.15 * novelty vs rejected edits
+ 0.10 * mechanical applicability and low leakage risk

## Edit Budget

Apply at most 2 bounded text edits. Prefer one small Procedure edit if it covers
the supported failure family.

## Tie Breaks

Break ties by broader train support, then smaller skill diff, then clearer exact
target string. Reject proposals with vague targets, no behavioral change, or
selection/test leakage.
