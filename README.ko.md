# SkillOpt MVP Harness

언어: [English](README.md) | 한국어 | [日本語](README.ja.md)

이 저장소는 SkillOpt 방식의 스킬 개선 루프를 검증하기 위한 작고 수동적인
하네스입니다. 이 하네스는 옵티마이저가 아니며 Codex를 호출하지 않습니다.
역할은 실험 경계를 단순하고 감사 가능하게 만드는 것입니다. 작업 워크스페이스를
준비하고, 고정된 검증기를 실행하고, pass/fail 점수를 기록하고, 루프 산출물을
보존하며, 증거가 strict improvement를 보일 때에만 후보 스킬을 gate합니다.

MVP는 두 가지 실용 트랙에 집중합니다.

- `code_repair`: pytest 기반의 작은 코드 수리 작업.
- `data_normalization`: pytest 기반의 작은 데이터 정리 및 변환 작업.

Python 하네스는 실험 메커니즘만 담당합니다. Codex, 사람의 판단, 옵티마이저
reflection은 하네스 밖에서 이루어지고, 하네스가 나중에 기록, 집계, gate할 수
있는 파일을 생성합니다.

## 왜 필요한가

스킬 개선은 쉽게 착각을 부릅니다. 후보 instruction이 좋아 보이는 이유가 잘못된
split을 봤기 때문일 수도 있고, parent와 candidate가 같은 작업에서 평가되지
않았기 때문일 수도 있고, hidden test가 작업 context로 새어 들어갔기 때문일 수도
있고, 실험 중 baseline이 조용히 덮어써졌기 때문일 수도 있습니다. 이 MVP는 그런
실패 모드를 드러내기 위해 존재합니다.

그래서 하네스는 스킬 업데이트를 prompt 작성 문제가 아니라 증거 문제로 다룹니다.

- Train 증거는 후보 edit을 제안하는 데 사용할 수 있습니다.
- Selection 증거는 후보를 accept할지 결정합니다.
- Test 증거는 최종 채택 및 보고 이후에만 사용합니다.
- 실험의 initial baseline은 immutable입니다.
- 각 루프의 parent는 그 루프 시작 시점의 current best skill입니다.
- 후보는 같은 selection 작업에서 parent를 strict하게 이길 때에만 accept됩니다.
- 오염된 루프는 점수가 개선되었더라도 reject됩니다.

점수는 의도적으로 단순합니다. 검증기 return code `0`은 `1.0`, 실패 또는 timeout은
`0.0`입니다. MVP에서 흥미로운 부분은 score modeling이 아니라 loop discipline을
감사 가능할 만큼 명시적으로 만들 수 있는지입니다.

## MVP 핵심 시나리오

깨끗한 single-loop 실험은 다음 흐름을 기대합니다.

1. initial baseline skill에서 시작하고 이를 실험 디렉터리에 snapshot합니다.
2. train 작업을 준비하고 parent skill로 외부 target-model rollout을 실행합니다.
3. 하네스 밖에서 train 실패를 reflection하고 제안된 skill edit을 작성합니다.
4. 하네스가 edit budget 안에서 edit을 집계하고 선택합니다.
5. 선택된 edit을 loop parent에 적용해 candidate skill을 만듭니다.
6. parent와 candidate를 같은 selection 작업에서 독립적으로 평가합니다.
7. selection record와 `unknown`이 아닌 rollout isolation 선언으로 gate를 실행합니다.
8. strict selection improvement와 깨끗한 split discipline이 있을 때에만 candidate를
   accept합니다.

multi-epoch 실험에서는 같은 루프를 2-4 epoch 동안 반복합니다. Accept된 candidate는
`current-best.md`를 갱신하며 다음 epoch의 parent가 됩니다. 원래의
`initial-baseline.md`는 변경하지 않으므로, 실험은 항상 시작점과 누적 개선을
구분할 수 있습니다.

## 검증 프로토콜

하네스는 세 가지 표면을 따로 검증합니다.

### 작업 격리

`prepare-task`는 fixture를 workspace로 복사하되 `tests_hidden`은 제외합니다.
workspace에는 `.skillopt-task.json`이 기록되며, 이 파일에는 track, split, task id,
description, entrypoint, source fixture path가 들어갑니다. 이 metadata 덕분에
`grade-task`는 임시 grading workspace 안에서만 hidden test를 복원할 수 있습니다.

따라서 prepared workspace는 수동 수리나 rollout 작업에 사용할 수 있습니다. Visible
test는 시도를 안내하지만, model 또는 사람이 편집하는 workspace에는 hidden test가
노출되지 않습니다.

### 고정 검증기

각 track은 `skillopt.yaml`에 설정된 pytest command를 사용합니다.

```yaml
evaluator_command:
  - uv
  - run
  - pytest
  - -q
  - tests_visible
  - tests_hidden
```

`grade-task`는 timeout과 함께 이 verifier를 실행하고 stdout, stderr, return code,
timeout status, task metadata, binary score를 기록합니다. Grading run 동안 verifier는
고정되어야 합니다. 점수를 개선하기 위해 test나 evaluator 동작을 바꾸는 것은 작업이
명시적으로 fixture maintenance가 아닌 한 contract 밖입니다.

### 루프 Gate

`loop-run`은 rollout을 생성하지 않고, 모델에게 edit을 요청하지도 않습니다. 대신
외부 artifact를 입력으로 받습니다.

- train rollout record;
- reflected edit proposal;
- parent selection record;
- candidate selection record;
- optional best selection record;
- contamination 및 rollout-isolation 선언.

Gate는 다음 중 하나라도 참이면 candidate를 reject합니다.

- 루프가 contaminated로 표시됨;
- rollout isolation이 `unknown`;
- parent와 candidate가 같은 selection task id에서 평가되지 않음;
- candidate selection score가 parent selection score 이하.

Candidate가 parent를 이겼지만 recorded best를 이기지 못하면 `current-best.md`를
갱신할 수 있습니다. Parent와 best를 모두 이기면 `best-skill.md`도 갱신합니다. Gate는
`gate-decision.json`과 `decision.md`를 작성하므로 accept 또는 reject 이유를 나중에
검토할 수 있습니다.

## Artifact 모델

중요한 skill-loop 파일은 application state에 숨겨지지 않고 experiment-local로
남습니다.

- `initial-baseline.md`: 실험의 immutable skill snapshot.
- `current-best.md`: 다음 루프 parent로 쓰이는 accepted skill.
- `best-skill.md`: recorded selection score 기준 best accepted skill.
- `<loop-id>/parent-skill.md`: 해당 루프의 parent snapshot.
- `<loop-id>/candidate-skill.md`: selected edit으로 생성된 candidate.
- `<loop-id>/rollouts/`: 복사된 train rollout evidence.
- `<loop-id>/reflected-edits.json`: 복사된 외부 edit proposal.
- `<loop-id>/aggregated-edits.json`: deduplicated edit candidate.
- `<loop-id>/selected-edits.json`: budget 안에서 선택된 edit set.
- `<loop-id>/update-report.json`: edit 적용 결과.
- `<loop-id>/parent-selection.jsonl`: parent selection evaluation record.
- `<loop-id>/candidate-selection.jsonl`: candidate selection evaluation record.
- `<loop-id>/gate-decision.json`: machine-readable accept/reject decision.
- `<loop-id>/decision.md`: human-readable gate summary.
- `<loop-id>/full-loop-manifest.json`: complete loop manifest.

이 파일 배치는 의도적으로 평범합니다. Reviewer는 experiment directory만 보고 어떤
증거가 사용되었는지, 어떤 skill이 편집되었는지, 무엇이 바뀌었는지, 왜 candidate가
gate를 통과하거나 통과하지 못했는지 재구성할 수 있어야 합니다.

## 현재 Skill과 Baseline

Project-local Codex asset은 Python 하네스 dependency가 아니라 수동 process의
입력입니다.

- `.codex/skills/code-repair/SKILL.md`
- `.codex/skills/data-normalization/SKILL.md`
- `.codex/skills/failure-to-fixture/SKILL.md`
- `.codex/skills/skillopt-loop/SKILL.md`
- `.codex/subagents/skill-loop-auditor.md`

MVP loop-validation experiment를 위한 재사용 가능한 weak baseline은 여기에 있습니다.

- `examples/baselines/code-repair-weak-baseline.md`
- `examples/baselines/data-normalization-weak-baseline.md`

이 asset들은 실험 실행에 유용하지만, 하네스는 계속 manual이어야 합니다. Codex나
optimizer model을 호출해서는 안 됩니다.

## Post-MVP 확장

MVP는 의도적으로 core loop를 좁게 유지합니다. list, prepare, grade, artifact 기록,
candidate skill text gate가 핵심입니다. 운영용 확장은 이 경계를 유지해야 하며,
하네스를 optimizer나 agent runner로 바꾸면 안 됩니다.

`failure-to-fixture`는 이런 확장의 첫 예입니다. 실패한 rollout, repair attempt,
verifier case, production observation을 미래 dataset version을 위한 proposed fixture로
정리합니다. 이것은 fixture maintenance이지 active loop step이 아닙니다.

이 확장은 다음 규칙을 따릅니다.

- Proposed case는 active fixture split 밖에 stage합니다. 예:
  `proposed_fixtures/<track>/<case-id>/`.
- 각 case를 최소화하고 provenance를 기록하며, track은 `skillopt.yaml`에서 해석합니다.
- Hidden test를 직접 inspect하지 않습니다. Hidden behavior는 기록되거나 redacted된
  `grade-task` output을 통해서만 사용합니다.
- Failure-derived fixture를 그 failure를 발견한 candidate의 accept, reject, tune,
  re-rank 근거로 사용하지 않습니다.
- Proposed fixture는 review 후에만 promote하고, 반드시 이후 experiment 또는 dataset
  version에만 반영합니다.

이렇게 하면 failed-case learning은 살리면서도, 미래 fixture가 현재 gate evidence로
역류하는 일을 막을 수 있습니다.

## 최소 Workflow Reference

아래 command는 저장소의 목적이 아니라 위 검증 프로토콜을 실행하기 위한 reference
point입니다.

작업을 list하고 prepare합니다.

```bash
uv run skillopt-harness list-tasks --track code_repair --split train
uv run skillopt-harness prepare-task \
  --track code_repair \
  --task train-expression-evaluator \
  --split train \
  --output workspaces/code_repair/train-expression-evaluator
```

Prepared workspace에서 수동 repair 또는 rollout을 수행한 뒤, 고정 verifier로
grade합니다.

```bash
uv run skillopt-harness grade-task \
  --track code_repair \
  --workspace workspaces/code_repair/train-expression-evaluator \
  --output runs/code-repair-manual.jsonl
```

외부 rollout, reflection, selection-evaluation artifact가 이미 있을 때 gate를
실행합니다.

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
  --candidate-selection-records runs/my-experiment/loop-01/candidate-selection.jsonl \
  --rollout-isolation independent
```

Candidate를 고려하기 전에 split discipline이 깨졌다면 조기에 abort합니다.

```bash
uv run skillopt-harness loop-abort \
  --track code_repair \
  --experiment-dir runs/my-experiment \
  --loop-id loop-01 \
  --initial-skill .codex/skills/code-repair/SKILL.md \
  --contamination-reason "selection results were visible during train reflection"
```

이미 준비된 epoch input으로 2-4 epoch series를 실행합니다.

```bash
uv run skillopt-harness epoch-run \
  --track code_repair \
  --experiment-dir runs/my-experiment \
  --initial-skill .codex/skills/code-repair/SKILL.md \
  --epoch-inputs runs/my-experiment/epoch-inputs.json \
  --edit-budget 2
```

## 개발 Check

코드 또는 artifact 변경을 넘기기 전에 다음을 실행합니다.

```bash
uv run pytest
uv run ruff check .
```

같은 workflow를 위한 Task equivalent도 있습니다.

```bash
task init
task list TRACK=code_repair SPLIT=train
task prepare TRACK=code_repair TASK=train-expression-evaluator
task grade TRACK=code_repair TASK=train-expression-evaluator
task loop-run
task epoch-run
task check
```
