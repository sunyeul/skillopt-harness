---
name: skillopt-loop-runner
description: Run a manual SkillOpt improvement loop in this harness from a short user request. Use when the user asks to run a code_repair or data_normalization skill experiment, improve a baseline skill with train evidence, compare parent and candidate on selection, or continue a SkillOpt loop without restating all split-discipline rules.
---

# SkillOpt Loop Runner

Use this skill to execute a manual SkillOpt loop with a compact prompt. This
skill is an execution wrapper; `.codex/skills/skillopt-loop/SKILL.md` remains
the source of truth for split discipline, contamination rules, lineage, and
acceptance gates.

## Start

Before touching task evidence:

1. Read `.codex/skills/skillopt-loop/SKILL.md` completely and follow it.
2. Read `AGENTS.md` if present.
3. Resolve required inputs:
   - `TRACK`: required. Ask if missing.
   - `EXPERIMENT_DIR`: required for adoption runs. Ask if missing, unless the
     user explicitly requested a throwaway exploration.
   - `LOOP_ID`: choose the next obvious loop id after checking only allowed
     experiment artifact paths.
4. Read `skillopt.yaml` to locate the target skill, evaluator command, and
   split paths for `TRACK`.

Do not run broad repository discovery before candidate generation. Use an
allowlist posture: read only the loop skill, AGENTS instructions, `skillopt.yaml`,
the target parent skill, and existing lineage artifacts needed to start.

## Guardrails

- Do not edit fixtures, verifier code, harness code, or split assignments during
  a skill improvement loop.
- Do not inspect hidden tests directly.
- Use train evidence only for candidate skill edits.
- Use selection only for the strict improvement gate.
- Use test only after final adoption/reporting.
- Determine baseline/parent improvement on selection only. After adoption, an
  initial-baseline or parent test score may be measured only as post-hoc
  reporting, never as a second gate or input to later edits.
- Keep parent and candidate selection repairs isolated. Prefer separate clean
  subagents or sessions with explicit assigned skill paths.
- If selection/test details or parent selection failure output leak into
  candidate creation or unfinished candidate repair work, mark the loop
  contaminated and reject.
- Do not commit planning or design documents unless the user explicitly asks.

## Workflow

1. Establish lineage: ensure immutable `initial-baseline.md`, current
   `current-best.md`, and `best-skill.md` under `EXPERIMENT_DIR`.
2. Snapshot the loop parent skill to `<loop-dir>/parent-skill.md`.
3. Gather train-only rollout records for the parent/current-best skill.
4. Reflect using only train evidence. Record concise trajectory lessons,
   proposal scoring, rejected-edit memory, and leakage checks in loop artifacts.
5. Write `<loop-dir>/candidate-skill.md` with bounded edits.
6. Validate the candidate mechanically:
   - selected targets occur exactly once, unless appending at end;
   - edits land in the intended section;
   - unselected text is unchanged.
7. Measure parent and candidate on selection with isolated repairers.
8. Accept only if `candidate_score > parent_score` and the run is clean.
9. On accept, update current-best/best-skill lineage. On reject, leave lineage
   unchanged and record the reason.
10. After final adoption, measure test split for reporting. If the user asks
    for baseline comparison, measure the immutable initial baseline or loop
    parent on test only after adoption and label it reporting-only.
11. Run `uv run pytest` and `uv run ruff check .` before handoff when the run
    produced tracked artifact or skill changes.

## Repairer Prompts

When spawning or instructing a repairer, include only the assigned skill, track,
split, workspace/output paths, and isolation rules. Do not include expected
scores, hidden failures, reference repairs, or conclusions from another split.

Use this shape:

```text
You are measuring <parent|candidate> for TRACK=<track> on SPLIT=<split>.
Use only <assigned-skill-path>. Prepare workspaces under <tmp-path>.
Read task.json/.skillopt-task.json and tests_visible only.
Do not read tests_hidden or reference solutions.
Repair only prepared workspaces, run visible tests as needed, then grade each
task exactly once with --redact-output. Do not iterate after grade.
Return passed/total, score JSONL path, blocked tasks, and isolation statement.
```

## Final Report

Report:

- experiment dir and loop id;
- parent and candidate selection scores;
- accept/reject decision and contamination status;
- final test score when measured;
- optional post-hoc baseline/parent test score and test delta when measured;
- verification results;
- any dirty pre-existing files intentionally left untouched.
