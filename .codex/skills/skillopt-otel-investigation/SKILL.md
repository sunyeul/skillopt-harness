---
name: skillopt-otel-investigation
description: Use when investigating local SkillOpt OpenTelemetry traces, collector output, localhost:4317 confusion, loop decisions, gate rejections, grading failures, or cross-checking spans against SkillOpt JSON/JSONL artifacts in this harness.
---

# SkillOpt OTEL Investigation

Use this skill to explain what happened in a traced SkillOpt harness command
without mistaking telemetry for the final evidence.

## Core Principle

Treat OpenTelemetry traces as the execution map and JSON/JSONL artifacts as the
evidence. Use spans to locate the relevant decision, score, failure, or slow
step, then confirm conclusions against the artifact files named by the run.

Do not claim a loop decision, score, contamination status, or verifier outcome
from trace attributes alone when the corresponding artifact is available.

## Local Trace Reality Check

- `http://localhost:4317/` is normally the OTLP gRPC receiver, not a browser UI.
- `http://localhost:4318/` is normally the OTLP HTTP receiver, also not a trace UI.
- With this repo's `otel/collector.yaml`, the collector prints spans through the
  debug exporter. Inspect the collector terminal output unless a Jaeger, Tempo,
  or other UI backend is explicitly configured.
- If no spans appear, check that the command ran with:
  - `SKILLOPT_OTEL_ENABLED=1`
  - `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`
  - `uv sync --extra otel` or equivalent dependencies installed

## Investigation Workflow

1. Identify the command and run scope: `loop-run`, `grade-task`, experiment dir,
   loop id, track, workspace, or output path.
2. If the user is confused by `localhost:4317`, explain that it is a receiver
   endpoint and use collector logs or the configured backend UI instead.
3. Find the highest-level relevant span:
   - `skillopt.loop_run` for full loop behavior.
   - `skillopt.gate` or `skillopt.decide` for accept/reject decisions.
   - `skillopt.score_parent` and `skillopt.score_candidate` for selection score
     comparisons.
   - `skillopt.proposal`, `skillopt.aggregate_edits`, `skillopt.select_edits`,
     and `skillopt.apply_edits` for candidate construction.
   - `skillopt.grade_task` for individual grading outcomes.
4. Read compact span attributes first: decision, reject reason, parent score,
   candidate score, score delta, leakage status, task id, split, return code,
   timeout, pass/fail counts, edit counts, and artifact paths.
5. Open only the artifact files needed to confirm the trace finding, such as
   `gate-decision.json`, `parent-selection.jsonl`, `candidate-selection.jsonl`,
   `update-report.json`, `selected-edits.json`, or the grading output JSONL.
6. Report trace observations separately from artifact-confirmed facts.

## Span Reading Guide

| Question | Start With | Confirm With |
|---|---|---|
| Why was the candidate rejected? | `skillopt.decide` attributes | `gate-decision.json` |
| Did candidate beat parent? | `skillopt.score_parent`, `skillopt.score_candidate` | parent/candidate selection JSONL |
| Was the run contaminated? | `skillopt.gate` leakage attributes | gate decision and audit artifacts |
| Did edits apply? | `skillopt.apply_edits` edit counts | `update-report.json`, candidate skill diff |
| Did a grade fail or time out? | `skillopt.grade_task` return code and timeout | grading output JSONL |
| Which phase was slow? | span durations | command logs/artifacts if needed |

## Split Discipline

If investigating an active SkillOpt improvement loop before final adoption,
follow `.codex/skills/skillopt-loop/SKILL.md` for split discipline. Do not use
selection or test traces, artifact names, scores, or verifier diagnostics to
propose candidate skill edits. If such evidence leaked into candidate creation
or unfinished candidate repairs, mark the loop contaminated instead of trying to
repair around the leak.

## Reporting Template

Use this shape for concise handoff:

```text
Trace says:
- <span>: <key attributes and timing>

Artifacts confirm:
- <artifact path>: <decision/score/outcome>

Conclusion:
- <why it accepted/rejected/failed/slowed down>

Gaps:
- <missing collector logs, missing artifact, disabled OTEL, or backend not configured>
```

## Privacy Guardrails

Do not put or request raw prompts, skill bodies, source code, verifier stdout or
stderr, secrets, or user data in span attributes. Prefer short enums, booleans,
counts, scores, return codes, task ids, and relative artifact paths.
