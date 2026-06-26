# SkillOpt Progress Dashboard

이 문서는 SkillOpt MVP의 구현 진행 상황을 갱신하기 위한 작업 대시보드입니다.
현재 목표는 실험 산출물을 진행하는 것이 아니라, Python harness가 수동 입력 기반의 6단계 전체 루프를 끝까지 관리하도록 구현하는 것입니다.

## Current Status

| 항목 | 값 |
|---|---|
| Active experiment | 없음 |
| Runs state | 초기화됨; `runs/` 디렉터리 없음 |
| Track focus | `code_repair`, 이후 `data_normalization`에도 재사용 가능해야 함 |
| Current phase | 6단계 전체 루프 구현 및 검증 완료 |
| Latest decision | 이전 실험 기록은 폐기/초기화 |
| Next action | fixture 기반 smoke artifact를 만들어 `loop-run` dry run 수행 |

## Target Six-Step Loop

| 단계 | 담당 | 구현 상태 | 현재 지원 | 구현할 것 |
|---|---|---|---|---|
| 1. Rollout | 외부 target + harness | Implemented | `loop-run`이 rollout artifact 보존 | richer trace schema는 이후 |
| 2. Reflect | 외부 optimizer | Implemented | `loop-run`이 `edit-proposals.json` 보존 | proposal 내용 생성은 harness 밖 |
| 3. Aggregate | Harness | Implemented | duplicate edit merge | semantic merge는 이후 |
| 4. Select / Clip | Harness | Implemented | score 기반 budget clip | edit score 기준 보강은 이후 |
| 5. Update | Harness | Implemented | `candidate-skill.md` 생성 | lineage와 연결됨 |
| 6. Validation Gate | Harness + 외부 selection rollout | Implemented | strict improvement + contaminated reject | test report는 이후 |

## Lineage Contract

| 용어 | 목표 위치 | 규칙 |
|---|---|---|
| `initial_baseline` | `<experiment-dir>/initial-baseline.md` | 첫 루프에서만 생성하고 이후 overwrite 금지 |
| `current_best` | `<experiment-dir>/current-best.md` | accepted candidate만 갱신; 다음 루프의 parent |
| `parent_skill` | `<loop-dir>/parent-skill.md` | 해당 loop 시작 시 current-best snapshot |
| `candidate_skill` | `<loop-dir>/candidate-skill.md` | selected edits 적용 결과 |
| `best_skill` | `<experiment-dir>/best-skill.md` | best selection score를 갱신한 candidate만 반영 |

## Implementation Scope

| 항목 | 필요 여부 | 상태 |
|---|---|---|
| single full-loop CLI | 필요 | 구현됨: `loop-run` |
| legacy partial loop CLI 제거 | 필요 | 완료: `loop-propose`, `loop-gate` 제거 |
| immutable baseline 생성/보존 | 필요 | 구현됨 |
| current-best parent snapshot | 필요 | 구현됨 |
| contaminated run 강제 reject | 필요 | 구현됨 |
| strict improvement gate | 필요 | 구현됨 |
| SkillOpt loop skill 보강 | 필요 | 완료: `loop-run` 단일 흐름 반영 |
| Skill loop auditor 보강 | 필요 | 완료: lineage, leakage, strict gate audit 반영 |
| test split report | 이후 | 미구현 |
| Codex/optimizer 자동 호출 | 불필요 | harness 밖에서 수동 실행 |

## Proposed CLI Shape

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

`--contaminated`가 주어지면 candidate score가 높아도 reject해야 합니다.

## Next Actions

### 완료

- [x] `loop-run` CLI 계약 확정
- [x] full-loop tests 추가: baseline 생성, current-best snapshot, candidate 생성, strict accept/reject
- [x] contamination flag가 accept를 막는 테스트 추가
- [x] `skill_loop.py`에 full-loop orchestration 함수 구현
- [x] `cli.py`에 `loop-run` 연결
- [x] README와 Taskfile 예시 갱신
- [x] pytest와 ruff 실행 (`.venv` 기준 통과)
- [x] SkillOpt loop skill과 skill-loop auditor를 `loop-run` 단일 흐름에 맞게 보강

### 다음

- [ ] `runs/smoke-loop/loop-01/`에 최소 train rollout, edit proposal, parent/candidate selection JSONL fixture 작성
- [ ] `uv run skillopt-harness loop-run ...` 또는 `task loop-run EXPERIMENT=runs/smoke-loop LOOP=loop-01`로 end-to-end dry run
- [ ] 생성된 `full-loop-manifest.json`, `gate-decision.json`, lineage 파일이 기대대로인지 확인
- [ ] dry run 결과를 바탕으로 CLI 사용성 문제나 artifact schema 부족분 정리
- [ ] 필요하면 test split report 명령/문서 설계

## Notes

- `runs/`는 현재 초기화된 상태이므로 대시보드에 이전 experiment artifact 경로를 남기지 않는다.
- Python harness는 Codex, target model, optimizer model을 호출하지 않는다.
- train evidence는 proposal 입력으로만, selection evidence는 gate 입력으로만, test evidence는 최종 reporting에만 사용한다.
- 레거시 partial loop CLI인 `loop-propose`, `loop-gate`는 공개 명령에서 제거되었다.
