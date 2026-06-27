# SkillOpt MVP Harness

言語: [English](README.md) | [한국어](README.ko.md) | 日本語

このリポジトリは、SkillOpt 形式のスキル改善ループを検証するための小さな手動
ハーネスです。これはオプティマイザーではなく、Codex も呼び出しません。役割は、
実験境界を退屈なくらい明示的で監査可能にすることです。タスク workspace を準備し、
固定 verifier を実行し、pass/fail score を記録し、ループ成果物を保存し、証拠が
strict improvement を示す場合にだけ candidate skill を gate します。

MVP は次の二つの実用 track に集中します。

- `code_repair`: pytest ベースの小さなコード修復タスク。
- `data_normalization`: pytest ベースの小さなデータ整理・変換タスク。

Python ハーネスは実験メカニクスだけを担当します。Codex、人間の判断、
optimizer reflection はハーネスの外で行われ、ハーネスが後で記録、集約、gate
できるファイルを生成します。

## なぜ存在するのか

スキル改善では、自分を簡単にだませてしまいます。Candidate instruction が良く
見える理由は、間違った split を見たからかもしれません。Parent と candidate が
同じタスクで評価されていなかったからかもしれません。Hidden test が作業 context
に漏れたからかもしれません。実験中に baseline が静かに上書きされたからかもしれ
ません。この MVP は、そうした失敗モードを見えるようにするためにあります。

そのため、ハーネスは skill update を prompt-writing の問題ではなく、証拠の問題
として扱います。

- Train evidence は candidate edit の動機づけに使えます。
- Selection evidence は candidate を accept するかどうかを決めます。
- Test evidence は最終採用と報告の後にだけ使います。
- 実験の initial baseline は immutable です。
- 各ループの parent は、そのループ開始時点の current best skill です。
- Candidate は同じ selection task 上で parent を strict に上回った場合だけ
  accept されます。
- 汚染されたループは、score が改善していても reject されます。

Score は意図的に単純です。Verifier return code `0` は `1.0`、失敗または timeout
は `0.0` です。MVP で重要なのは score modeling ではありません。Loop discipline
を監査可能なほど明示できるかどうかです。

## MVP の中核シナリオ

Clean な single-loop experiment は次の流れを想定します。

1. Initial baseline skill から始め、それを experiment に snapshot します。
2. Train task を準備し、parent skill で外部 target-model rollout を実行します。
3. ハーネスの外で train failure を reflection し、skill edit proposal を書きます。
4. ハーネスが edit budget 内で edit を集約し、選択します。
5. 選択された edit を loop parent に適用し、candidate skill を作ります。
6. Parent と candidate を同じ selection task 上で独立に評価します。
7. Selection record と `unknown` ではない rollout isolation 宣言で gate を実行します。
8. Strict selection improvement と clean な split discipline がある場合だけ
   candidate を accept します。

Multi-epoch experiment では、同じループを 2-4 epoch 繰り返します。Accepted
candidate は `current-best.md` を更新し、次 epoch の parent になります。元の
`initial-baseline.md` は変更されないため、実験は常に開始点と累積改善を区別でき
ます。

## 検証プロトコル

ハーネスは三つの面を分けて検証します。

### タスク隔離

`prepare-task` は fixture を workspace にコピーしますが、`tests_hidden` は除外
します。Workspace には `.skillopt-task.json` が書かれ、track、split、task id、
description、entrypoint、source fixture path が記録されます。この metadata により、
`grade-task` は一時的な grading workspace の中だけで hidden test を復元できます。

したがって prepared workspace は、手動修復や rollout 作業に使えます。Visible
test は試行を導きますが、model や人間が編集する workspace には hidden test が
露出しません。

### 固定 Verifier

各 track は `skillopt.yaml` に設定された pytest command を使います。

```yaml
evaluator_command:
  - uv
  - run
  - pytest
  - -q
  - tests_visible
  - tests_hidden
```

`grade-task` は timeout 付きでこの verifier を実行し、stdout、stderr、return code、
timeout status、task metadata、binary score を記録します。Grading run の間、
verifier は固定されます。Score を上げるために test や evaluator の動作を変更する
ことは、明示的な fixture maintenance でない限り contract 外です。

### ループ Gate

`loop-run` は rollout を生成せず、model に edit を依頼しません。代わりに外部
artifact を消費します。

- train rollout record;
- reflected edit proposal;
- parent selection record;
- candidate selection record;
- optional best selection record;
- contamination および rollout-isolation 宣言.

Gate は次のいずれかが真なら candidate を reject します。

- loop が contaminated として marked されている;
- rollout isolation が `unknown`;
- parent と candidate が同じ selection task id で評価されていない;
- candidate selection score が parent selection score 以下.

Candidate が parent を上回るが recorded best は上回らない場合、
`current-best.md` を更新できます。Parent と best の両方を上回る場合、
`best-skill.md` も更新します。Gate は `gate-decision.json` と `decision.md` を
書くため、accept または reject の理由を後から review できます。

## Artifact モデル

重要な skill-loop file は application state に隠されず、experiment-local に残ります。

- `initial-baseline.md`: experiment の immutable skill snapshot.
- `current-best.md`: 次 loop parent として使われる accepted skill.
- `best-skill.md`: recorded selection score 基準の best accepted skill.
- `<loop-id>/parent-skill.md`: この loop の parent snapshot.
- `<loop-id>/candidate-skill.md`: selected edit から作られた candidate.
- `<loop-id>/rollouts/`: コピーされた train rollout evidence.
- `<loop-id>/reflected-edits.json`: コピーされた外部 edit proposal.
- `<loop-id>/aggregated-edits.json`: deduplicated edit candidate.
- `<loop-id>/selected-edits.json`: budget 内で選ばれた edit set.
- `<loop-id>/update-report.json`: edit application result.
- `<loop-id>/parent-selection.jsonl`: parent selection evaluation record.
- `<loop-id>/candidate-selection.jsonl`: candidate selection evaluation record.
- `<loop-id>/gate-decision.json`: machine-readable accept/reject decision.
- `<loop-id>/decision.md`: human-readable gate summary.
- `<loop-id>/full-loop-manifest.json`: complete loop manifest.

このファイル配置は意図的に平凡です。Reviewer は experiment directory を見れば、
どの証拠が使われ、どの skill が編集され、何が変わり、なぜ candidate が gate を
通過した、または通過しなかったのかを再構成できるべきです。

## 現在の Skill と Baseline

Project-local Codex asset は Python ハーネス dependency ではなく、手動 process の
入力です。

- `.codex/skills/code-repair/SKILL.md`
- `.codex/skills/data-normalization/SKILL.md`
- `.codex/skills/failure-to-fixture/SKILL.md`
- `.codex/skills/skillopt-loop/SKILL.md`
- `.codex/subagents/skill-loop-auditor.md`

MVP loop-validation experiment 用の再利用可能な weak baseline はここにあります。

- `examples/baselines/code-repair-weak-baseline.md`
- `examples/baselines/data-normalization-weak-baseline.md`

これらの asset は実験実行に有用ですが、ハーネスは manual のままでなければなり
ません。Codex や optimizer model を呼び出してはいけません。

## Post-MVP 拡張

MVP は意図的に core loop を狭く保ちます。list、prepare、grade、artifact 記録、
candidate skill text の gate が中心です。運用上の拡張はこの境界を保つべきで、
ハーネスを optimizer や agent runner に変えてはいけません。

`failure-to-fixture` はそのような拡張の最初の例です。失敗した rollout、repair
attempt、verifier case、production observation を、将来の dataset version のための
proposed fixture として整理します。これは fixture maintenance であり、active loop
step ではありません。

この拡張は次の規則に従います。

- Proposed case は active fixture split の外に stage します。例:
  `proposed_fixtures/<track>/<case-id>/`。
- 各 case を最小化し、provenance を記録し、track は `skillopt.yaml` から解決します。
- Hidden test を直接 inspect しません。Hidden behavior は、記録済みまたは redacted
  された `grade-task` output を通じてのみ使います。
- Failure-derived fixture を、その failure を発見した candidate の accept、reject、
  tune、re-rank の根拠に使いません。
- Proposed fixture は review 後にのみ promote し、必ず後続の experiment または
  dataset version にだけ反映します。

これにより failed-case learning を有用に保ちながら、将来の fixture が現在の gate
evidence に逆流することを防ぎます。

## 最小 Workflow Reference

以下の command はリポジトリの目的ではなく、上の検証プロトコルを実行するための
reference point です。

Task を list して prepare します。

```bash
uv run skillopt-harness list-tasks --track code_repair --split train
uv run skillopt-harness prepare-task \
  --track code_repair \
  --task train-expression-evaluator \
  --split train \
  --output workspaces/code_repair/train-expression-evaluator
```

Prepared workspace で手動 repair または rollout を行った後、固定 verifier で
grade します。

```bash
uv run skillopt-harness grade-task \
  --track code_repair \
  --workspace workspaces/code_repair/train-expression-evaluator \
  --output runs/code-repair-manual.jsonl
```

外部 rollout、reflection、selection-evaluation artifact がすでに存在する場合に
gate を実行します。

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

Candidate を検討する前に split discipline が破られた場合は、早期に abort します。

```bash
uv run skillopt-harness loop-abort \
  --track code_repair \
  --experiment-dir runs/my-experiment \
  --loop-id loop-01 \
  --initial-skill .codex/skills/code-repair/SKILL.md \
  --contamination-reason "selection results were visible during train reflection"
```

すでに準備済みの epoch input から 2-4 epoch series を実行します。

```bash
uv run skillopt-harness epoch-run \
  --track code_repair \
  --experiment-dir runs/my-experiment \
  --initial-skill .codex/skills/code-repair/SKILL.md \
  --epoch-inputs runs/my-experiment/epoch-inputs.json \
  --edit-budget 2
```

## Development Checks

Code または artifact の変更を hand off する前に、次を実行します。

```bash
uv run pytest
uv run ruff check .
```

同じ workflow の Task equivalent もあります。

```bash
task init
task list TRACK=code_repair SPLIT=train
task prepare TRACK=code_repair TASK=train-expression-evaluator
task grade TRACK=code_repair TASK=train-expression-evaluator
task loop-run
task epoch-run
task check
```
