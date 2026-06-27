---
name: failure-to-fixture
description: Use when turning a failed SkillOpt rollout, repair attempt, verifier case, or production observation into a proposed fixture for a configured harness track without contaminating active experiments.
---

# Failure To Fixture

## Overview

Use this skill to curate failed cases into reviewable fixture proposals for the
manual SkillOpt harness. Fixture maintenance is outside the active optimization
loop: do not use new or failed cases to accept, reject, tune, or re-rank a
candidate skill in the experiment that discovered them.

## Core Rule

Failed cases may become future fixtures only through a separate maintenance
workflow. During an active SkillOpt loop, keep the verifier, fixture splits,
task files, tests, and split assignments fixed.

Never add a failure-derived fixture to improve the score of the current
candidate, explain away a selection/test failure, or create new evidence for an
unfinished loop.

## Inputs

Collect the minimum evidence needed to reproduce the failure:

- track name, resolved from `skillopt.yaml`;
- source of the failure: train rollout, selection gate, test report, production
  observation, or manual reproduction;
- original task or workspace path when available;
- visible command run, return code, verifier output, and observed wrong result;
- expected behavior, preferably stated as an input/output contract;
- contamination status of the source experiment.

Do not inspect `tests_hidden` files directly. Hidden behavior may be inferred
only from redacted or recorded `grade-task` output.

## Workflow

1. Classify the source:
   - Train failures may become training or regression candidates.
   - Selection/test failures may be proposed only for a future dataset version.
   - Contaminated failures may be retained as notes, but must not be promoted
     until independently reproduced from clean public behavior.
2. Create a staging record outside active fixture splits, such as
   `proposed_fixtures/<track>/<case-id>/` or an issue-style markdown note.
3. Minimize the case:
   - remove unrelated files, data rows, branches, and assertions;
   - keep the smallest public contract that still demonstrates the failure;
   - preserve public function names and fixture layout conventions.
4. Draft the fixture with the normal layout:
   - `task.json`;
   - source files;
   - `tests_visible`;
   - `tests_hidden` only when the expected behavior should remain grading-only.
5. Verify the draft in isolation with the existing harness and fixed verifier.
   Do not modify harness code, verifier code, or existing split assignments as
   part of making the case pass.
6. Record provenance:
   - source experiment or observation;
   - whether source evidence came from train, selection, test, or production;
   - why the case is not a duplicate;
   - intended future split;
   - reviewer and approval status.
7. Promote only after human review. Promotion should happen as dataset
   maintenance for a later experiment, not mid-loop.

## Split Assignment

Assign proposed cases conservatively:

| Source | Allowed destination | Notes |
|---|---|---|
| Train failure | Future train or regression set | Good for teaching skill edits later. |
| Selection failure | Future selection/test only after review | Never feed back into the same loop. |
| Test failure | Future test or held-out regression | Use only after final reporting is done. |
| Production/manual case | Any future split after dedupe | Prefer train unless it is meant to stay held out. |

If the same failure influenced a candidate skill, do not place it in a split
used to claim that candidate's improvement.

## Acceptance Checklist

Before promoting a proposed fixture:

- The case has a clear task contract and deterministic expected behavior.
- The visible tests teach enough public behavior for a task worker to act.
- Hidden tests, if present, check generalization rather than unrelated traps.
- The fixture follows the existing track layout.
- The verifier passes for a known-good implementation and fails for the broken
  behavior, or the limitation is recorded.
- The proposal includes provenance, source split, contamination status, and
  intended future split.
- Existing fixtures and tests were not edited to force the new case through.

## Common Mistakes

| Mistake | Correct response |
|---|---|
| Adding a selection failure to train during the same experiment | Stage it for a future dataset version. |
| Looking at `tests_hidden` to write a better fixture | Use only grade output or public reproduction. |
| Changing the verifier to fit one case | Reject or redesign the proposed fixture. |
| Making a broad synthetic task from one failure | Minimize to the smallest reproducible contract. |
| Skipping provenance because the failure is obvious | Record source, split, and contamination anyway. |

## Final Response

Report the staged fixture path, source evidence, intended future split, and any
review or verification that remains before promotion.
