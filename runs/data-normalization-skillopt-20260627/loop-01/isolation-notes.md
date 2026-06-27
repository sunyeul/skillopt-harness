# Isolation Notes

## Pre-Proposal Timeline

- Read loop instructions, AGENTS.md, `skillopt.yaml`, lineage skill files, and
  auditor prompt.
- Listed only the experiment directory and train tasks before candidate
  generation.
- Prepared and inspected train split workspaces only.
- Candidate proposal and `candidate-skill.md` were generated before any
  selection or test task evidence was read by the coordinating optimizer.

## Selection Repairer Setup

- Parent repairer: independent subagent `019f0a03-0db6-75f3-b7b4-ddbb9b8820fb`
  (`Wegener`), `fork_context=false`, assigned only
  `runs/data-normalization-skillopt-20260627/loop-01/parent-skill.md`.
- Candidate repairer: independent subagent
  `019f0a03-33c6-7120-ae90-9c46914b07ee` (`Godel`), `fork_context=false`,
  assigned only
  `runs/data-normalization-skillopt-20260627/loop-01/candidate-skill.md`.
- Rollout isolation mode: `independent`.
- Parent/candidate repairers were instructed not to read the other branch's
  skill, workspace, JSONL, verifier output, train artifacts, or test artifacts.

## Hidden Test Boundary

Hidden tests were not opened directly. Selection and later test hidden behavior
may be observed only through `grade-task --redact-output` scores and JSONL
records after the candidate skill was fixed.
