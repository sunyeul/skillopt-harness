# Manual SkillOpt Improvement for Code Repair After Fixture Redesign

## Abstract

This report summarizes one manual SkillOpt loop for the `code_repair` track
after a fixture redesign weakened the existing baseline skill. The loop used
train evidence to construct a bounded candidate skill, selection evidence to
decide adoption, and test evidence only after adoption for final reporting. The
candidate improved selection performance from `0.0` to `0.6` and was accepted
as `accept_new_best` under a clean, independently audited gate. The accepted
candidate achieved a final test score of `1.0` (`5/5`). A post-hoc,
reporting-only test measurement of the immutable initial baseline scored `0.4`
(`2/5`), giving a held-out reporting delta of `+0.6`.

## Introduction

The repository implements a manual SkillOpt harness for evaluating skill text
changes without letting the Python harness call Codex or mutate the repair
workflow. The `code_repair` baseline skill had become overly conservative after
the fixture redesign: it emphasized satisfying visible tests with the smallest
local change and discouraged parsers, state machines, and broader contract
coverage. The redesigned fixtures, however, often require compact coherent
implementations that cover the visible behavior family plus adjacent
`task.json` rules such as validation, coercion, ordering, and preservation.

The objective of this loop was to improve the baseline code-repair skill while
preserving split discipline:

- use train split evidence only to propose skill edits;
- use selection split evidence only for the strict adoption gate;
- use test split evidence only after adoption for reporting;
- keep fixtures, verifier, split assignments, and harness code fixed.

## Methods

### Experimental Setting

- Track: `code_repair`
- Experiment directory: `runs/code-repair-skillopt-20260627`
- Loop id: `loop-01`
- Parent skill snapshot: `loop-01/parent-skill.md`
- Candidate skill: `loop-01/candidate-skill.md`
- Gate decision: `loop-01/gate-decision.json`
- Final test records: `loop-01/test-results-all.jsonl`

The immutable initial baseline, current-best, and best-skill lineage artifacts
were initialized before task evidence was inspected. Candidate generation was
performed only against train evidence. Selection and test artifacts were not
used to create or revise the candidate.

### Rollout

Train rollouts were collected across eight `code_repair` train tasks. The
rollouts showed that successful repairs required compact, behavior-family-level
implementations:

- expression and duration tasks required compact parsers or scanners;
- token parsing required a purpose-specific state machine;
- dependency ordering required deterministic traversal and validation;
- normalization and allocation tasks required adjacent coercion, validation,
  ordering, and input-preservation logic.

All train repairs passed after visible-test-driven repair and train grading.
The aggregate train lesson was that literal one-assertion patches were weaker
than compact coherent implementations of the visible behavior family.

### Reflect

Reflection used only train trajectories and train grade records. The parent
skill was judged to over-penalize parser/state-machine solutions and to
over-prefer visible-test-only behavior even when `task.json` described rules
that belonged to the same implementation path as the visible tests.

### Aggregate and Select

Two edit families were selected under an edit budget of two:

1. Replace visible-only minimal-change guidance with guidance to implement the
   smallest coherent local implementation satisfying visible tests and the
   same exercised `task.json` behavior family.
2. Replace parser-specific visible-only guidance with permission to implement
   visible grammar families plus malformed-input checks that fall out of the
   same scanner or parser.

The selected edits were mechanically validated: each target occurred once in
the parent skill, edits landed in the `## Rules` section, and unselected text
was unchanged.

### Skill Before/After Diff

The accepted candidate changed only the bounded `## Rules` guidance shown
below.

```diff
--- parent-skill.md
+++ candidate-skill.md
@@ -7,19 +7,13 @@
 
 - Read `task.json`, `.skillopt-task.json` when present, and the visible tests
   before editing, but treat visible tests as the primary repair target.
-- Make the smallest local code change that satisfies the visible tests.
-- Do not build a full parser, solver, state machine, or general-purpose
-  implementation unless a visible test directly requires it.
-- If `task.json` describes extra edge cases that are not exercised by visible
-  tests, prefer the simpler visible-test behavior over implementing the whole
-  contract.
-- Stop once the visible tests are satisfied. Do not add methods, operations,
-  branches, validation paths, or edge-case handling that are mentioned only in
-  `task.json` and never called or asserted by visible tests.
+- Make the smallest coherent local implementation that satisfies the visible tests and the `task.json` contract for the same exercised behavior family.
+- Use visible tests as the primary acceptance target, then include `task.json` validation, coercion, ordering, and preservation rules when they share the same parser, normalizer, allocator, or traversal needed for visible behavior.
+- Avoid unrelated general-purpose frameworks. When visible tests require parsing, ordering, allocation, or token state, build a compact purpose-specific parser, loop, or state machine for that described behavior family.
+- Stop once the visible tests and this coherent contract slice pass. Do not add unrelated methods, operations, input formats, or edge-case families that are only mentioned in `task.json` and not connected to visible behavior.
 - For classes, implement only the methods used by visible tests plus minimal
   support needed by those methods.
-- For parsers and expression-like tasks, implement only the grammar forms that
-  appear in visible tests.
+- For parsers and expression-like tasks, implement the visible grammar families plus task-described malformed-input checks that fall out of the same scanner or parser.
 - Prefer straightforward branches and helper functions over broad abstractions.
 - Preserve existing public function names and signatures.
 - Do not change tests.
```

차분의 핵심은 수리 전략의 기준을 바꾼 것이다. 기존 스킬은 visible
test를 만족하는 가장 작은 국소 수정에 강하게 묶여 있었고,
`task.json`에 있는 추가 규칙은 visible test가 직접 요구하지 않으면
피하도록 유도했다. 이 때문에 redesigned fixture처럼 visible behavior와
검증, coercion, ordering, preservation이 같은 구현 경로에 붙어 있는
과제에서는 너무 얕은 patch를 만들 위험이 컸다.

candidate 스킬은 visible test를 여전히 주된 acceptance target으로 두되,
같은 behavior family에 속한 `task.json` 계약까지 compact하게 구현하도록
기준을 넓혔다. 또한 parser, loop, state machine을 무조건 피하는 대신,
parsing, ordering, allocation, token state가 visible behavior를 구현하는
데 필요한 경우에는 목적 한정의 작은 구현을 허용했다. 즉 변경의 의미는
“visible-only patch”에서 “coherent contract-slice repair”로 이동한 것이다.

### Update

The candidate skill was written only to the loop artifact path before gate
evaluation. The deployable/current-best lineage was not advanced until after
the clean selection gate and independent audit.

### Gate

Parent and candidate selection rollouts were performed by isolated repairers
with explicit assigned skill paths:

- Parent repairer: Curie, assigned only `parent-skill.md`
- Candidate repairer: James, assigned only `candidate-skill.md`
- Auditor: McClintock, independent read-only audit

The parent and candidate were evaluated on the same five selection tasks in the
same order. Adoption used the strict rule `candidate_score > parent_score`.
Test scores were not used for adoption.

## Results

### Core Scenario Validation

The core scenario was validated successfully. The intended scenario was:
weakened baseline skill after fixture redesign -> train-only reflection ->
bounded candidate update -> isolated selection gate -> clean strict
improvement -> adopted current-best -> held-out test reporting.

| Scenario requirement | Result |
|---|---|
| Candidate generated from train evidence only | Satisfied |
| Parent and candidate compared quantitatively on selection | Satisfied |
| Candidate strictly improved over parent on selection | Satisfied: `0.6 > 0.0` |
| Gate remained uncontaminated | Satisfied: `clean` |
| Accepted candidate was validated on held-out test after adoption | Satisfied: `1.0` (`5/5`) |
| Initial baseline was measured on test only after adoption for reporting | Satisfied: `0.4` (`2/5`) |

### Selection Gate

| Metric | Parent | Candidate | Delta |
|---|---:|---:|---:|
| Selection score | 0.0 | 0.6 | +0.6 |
| Selection passed tasks | 0 / 5 | 3 / 5 | +3 / 5 |

Gate outcome:

- Decision: `accept_new_best`
- Leakage status: `clean`
- Rollout isolation: `independent`
- Contamination reason: `null`
- Independent audit confidence: high

### Final Test Reporting

Final test was measured only after clean adoption.

| Metric | Initial baseline | Accepted candidate/current-best | Delta |
|---|---:|---:|---:|
| Test score | 0.4 | 1.0 | +0.6 |
| Test passed tasks | 2 / 5 | 5 / 5 | +3 / 5 |

The baseline test score was measured post-hoc by an isolated repairer using
only `initial-baseline.md`. It was not used for adoption, candidate tuning, or
any later skill edit.

Per-task final test scores:

| Test task | Initial baseline | Accepted candidate/current-best |
|---|---:|---:|
| `test-range-expression` | 0.0 | 1.0 |
| `test-status-reconciliation` | 0.0 | 1.0 |
| `test-line-patch-applicator` | 0.0 | 1.0 |
| `test-lru-cache` | 1.0 | 1.0 |
| `test-stable-priority-queue` | 1.0 | 1.0 |

## Discussion

The selection result supports the hypothesis that the weakened baseline was
too narrowly visible-test-oriented for the redesigned fixtures. The accepted
candidate improved repair behavior by making the target agent implement a
coherent contract slice: visible tests remained the anchor, but adjacent
`task.json` rules were included when they belonged to the same parser,
normalizer, allocator, traversal, or state-machine path.

The clean split discipline is central to interpreting the result. Quantitative
improvement over the parent was established only on selection. Test performance
was measured after adoption and therefore serves as held-out reporting, not as
a second adoption gate. This protects the test split from becoming an implicit
selection set.

The accepted candidate's final test score of `1.0` is encouraging. The
post-hoc baseline test score of `0.4` provides an effect-size view on the same
held-out split, but it remains reporting-only: it was measured after the clean
selection decision and did not influence adoption.

## Limitations

- The loop contains a single candidate update, so variance across multiple
  SkillOpt loops is unknown.
- The baseline test result was measured post-hoc after adoption. It supports
  effect-size reporting but is not evidence for the adoption decision.
- Train rollouts were manual and external to the Python harness, as intended by
  this repository's contract.
- The candidate was evaluated on five selection tasks and five test tasks; more
  tasks would improve confidence in generality.

## Conclusion

The core scenario was validated successfully. The manual SkillOpt loop produced
a cleanly accepted `code_repair` candidate whose selection score improved from
`0.0` to `0.6`, satisfying the strict adoption gate, and whose final held-out
test score was `1.0` (`5/5`) after adoption. A post-hoc reporting-only
baseline test run scored `0.4` (`2/5`), so the held-out reporting delta is
`+0.6`.

The substantive skill improvement was a shift from visible-test-only patching
to compact coherent implementations of the visible behavior family plus
adjacent task-contract rules. This supports the conclusion that the fixture
redesign weakened the old baseline primarily by making overly narrow
visible-test targeting insufficient. Future reports may include post-hoc
baseline test measurement for effect size, but adoption decisions should
continue to be made only on selection.
