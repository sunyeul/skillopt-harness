# OpenTelemetry tracing

This harness can optionally emit OpenTelemetry traces for the manual SkillOpt loop.
The JSON and JSONL artifacts remain the evidence of what happened; traces show the
order in which the evidence and decisions were produced.

## What is traced

- `skillopt.loop_run`
- `skillopt.proposal`
- `skillopt.aggregate_edits`
- `skillopt.select_edits`
- `skillopt.apply_edits`
- `skillopt.gate`
- `skillopt.score_parent`
- `skillopt.score_candidate`
- `skillopt.decide`
- `skillopt.grade_task`

## What is not traced

- Full skill text
- Full source code
- Full verifier stdout or stderr
- LLM prompts or responses
- Secrets or environment variable values
- Metrics, logs, token counts, or costs

The harness does not call Codex, Claude, OpenAI, Gemini, or any LLM API. Tracing is
only an observation layer around the existing manual artifact workflow.

## Enable tracing

Tracing is disabled by default and OpenTelemetry packages are optional. Install the
extra and opt in with `SKILLOPT_OTEL_ENABLED`:

```bash
uv sync --extra otel
export SKILLOPT_OTEL_ENABLED=1
export OTEL_SERVICE_NAME=skillopt-harness
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

`SKILLOPT_OTEL_ENABLED` accepts `1`, `true`, or `yes`. Standard OpenTelemetry OTLP
environment variables are passed through to the OpenTelemetry exporter.

## Local trace UI

The OTLP receiver port is not a browser UI. `http://localhost:4317/` receives
OTLP over gRPC, and `http://localhost:4318/` receives OTLP over HTTP.

For a local browser UI, run Jaeger:

```bash
task otel-ui
```

Or run it in the background:

```bash
task otel-ui-detached
```

Then open:

```text
http://localhost:16686
```

The compose file is `otel/docker-compose.yaml`. It publishes:

- `16686`: Jaeger UI
- `4317`: OTLP gRPC receiver
- `4318`: OTLP HTTP receiver

To stop the local UI:

```bash
task otel-ui-down
```

If you want to pin or test a different Jaeger image locally, set `JAEGER_IMAGE`:

```bash
JAEGER_IMAGE=jaegertracing/all-in-one:latest task otel-ui
```

## Example local run

This repository includes a recorded code-repair loop under
`runs/code-repair-clean-loop/loop-01`. To create a new traced loop from those
artifacts without changing tracked run artifacts, write the output under `.tmp/`:

```bash
uv run skillopt-harness loop-run \
  --track code_repair \
  --experiment-dir .tmp/otel-demo-loop \
  --loop-id loop-01 \
  --edit-proposals runs/code-repair-clean-loop/loop-01/reflected-edits.json \
  --edit-budget 2 \
  --rollout-records runs/code-repair-clean-loop/loop-01/rollouts/train-rollouts.jsonl \
  --parent-selection-records runs/code-repair-clean-loop/loop-01/parent-selection.jsonl \
  --candidate-selection-records runs/code-repair-clean-loop/loop-01/candidate-selection.jsonl \
  --rollout-isolation independent
```

To trace a normal grading command:

```bash
uv run skillopt-harness grade-task \
  --track code_repair \
  --workspace workspaces/code_repair/example \
  --output runs/code-repair-manual.jsonl
```

## Example collector

A minimal collector config is available at `otel/collector.yaml`. It accepts OTLP
over gRPC or HTTP and prints spans with the debug exporter. Run it with your
preferred OpenTelemetry Collector binary or container image, pointing the collector
at that file.

## Attribute policy

Custom attributes use the `skillopt.` prefix. The harness records compact values
such as track names, loop ids, artifact paths, edit counts, scores, pass/fail
counts, gate decisions, reject reasons, return codes, and booleans.

Attributes intentionally avoid high-volume or sensitive data. Artifact files remain
the source of detailed evidence.

## Privacy policy

Do not put raw prompts, skill bodies, source code, verifier output, user data, or
secrets into span attributes. Relative artifact paths, short enum values, counts,
scores, task ids, and return codes are acceptable.
