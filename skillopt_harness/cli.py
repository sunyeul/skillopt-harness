from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Iterable

from .config import HarnessConfig, TrackConfig, load_config
from .evaluator import copy_task_to_workspace, run_workspace_verifier
from .skill_loop import abort_loop, load_epoch_inputs, run_epoch_series, run_full_loop
from .state import TaskMetadata, append_jsonl, ensure_dir, load_tasks, utc_timestamp, write_json

TASK_META_FILENAME = ".skillopt-task.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillopt-harness")
    parser.add_argument("--config", default="skillopt.yaml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-tasks")
    list_parser.add_argument("--track", required=True)
    list_parser.add_argument("--split", choices=["train", "selection", "test"])

    prepare_parser = subparsers.add_parser("prepare-task")
    prepare_parser.add_argument("--track", required=True)
    prepare_parser.add_argument("--task", required=True)
    prepare_parser.add_argument("--output", required=True)
    prepare_parser.add_argument("--split", choices=["train", "selection", "test"])
    prepare_parser.add_argument("--force", action="store_true")

    grade_parser = subparsers.add_parser("grade-task")
    grade_parser.add_argument("--track", required=True)
    grade_parser.add_argument("--workspace", required=True)
    grade_parser.add_argument("--output")
    grade_parser.add_argument(
        "--redact-output",
        action="store_true",
        help="Print only non-diagnostic grading fields; keep full verifier output in records.",
    )

    run_parser = subparsers.add_parser("loop-run")
    run_parser.add_argument("--track", required=True)
    run_parser.add_argument("--experiment-dir", required=True)
    run_parser.add_argument("--loop-id", required=True)
    run_parser.add_argument("--initial-skill")
    run_parser.add_argument("--edit-proposals", required=True)
    run_parser.add_argument("--edit-budget", type=int, default=1)
    run_parser.add_argument("--rollout-records", action="append", default=[])
    run_parser.add_argument("--parent-selection-records", required=True)
    run_parser.add_argument("--candidate-selection-records", required=True)
    run_parser.add_argument("--best-selection-records")
    run_parser.add_argument("--baseline-test-records")
    run_parser.add_argument("--candidate-test-records")
    run_parser.add_argument("--contaminated", action="store_true")
    run_parser.add_argument("--contamination-reason")
    run_parser.add_argument(
        "--rollout-isolation",
        choices=[
            "independent",
            "completed-before-output",
            "redacted-in-session",
            "unknown",
        ],
        default="unknown",
    )

    abort_parser = subparsers.add_parser("loop-abort")
    abort_parser.add_argument("--track", required=True)
    abort_parser.add_argument("--experiment-dir", required=True)
    abort_parser.add_argument("--loop-id", required=True)
    abort_parser.add_argument("--initial-skill", required=True)
    abort_parser.add_argument("--contamination-reason", required=True)

    epoch_parser = subparsers.add_parser("epoch-run")
    epoch_parser.add_argument("--track", required=True)
    epoch_parser.add_argument("--experiment-dir", required=True)
    epoch_parser.add_argument("--initial-skill")
    epoch_parser.add_argument("--epoch-inputs", required=True)
    epoch_parser.add_argument("--edit-budget", type=int, default=1)

    subparsers.add_parser("init-fixtures")

    args = parser.parse_args(argv)
    config = load_config(Path(args.config))
    if args.command == "list-tasks":
        return _list_tasks(config.track(args.track), args.split)
    if args.command == "prepare-task":
        return _prepare_task(
            track=config.track(args.track),
            task_id=args.task,
            output=Path(args.output),
            split=args.split,
            force=bool(args.force),
        )
    if args.command == "grade-task":
        return _grade_task(
            config=config,
            track=config.track(args.track),
            workspace=Path(args.workspace),
            output=Path(args.output) if args.output else None,
            redact_output=bool(args.redact_output),
        )
    if args.command == "loop-run":
        return _loop_run(config=config, args=args)
    if args.command == "loop-abort":
        return _loop_abort(config=config, args=args)
    if args.command == "epoch-run":
        return _epoch_run(config=config, args=args)
    if args.command == "init-fixtures":
        return _init_fixtures(config)
    raise AssertionError(f"Unhandled command: {args.command}")


def _list_tasks(track: TrackConfig, split: str | None) -> int:
    for split_name, task in _iter_tasks(track, split):
        print(f"{track.name}\t{split_name}\t{task.id}\t{task.description}")
    return 0


def _prepare_task(
    track: TrackConfig,
    task_id: str,
    output: Path,
    split: str | None,
    force: bool,
) -> int:
    matches = list(_find_tasks(track, task_id, split))
    if not matches:
        print(f"Task not found: {task_id}", file=sys.stderr)
        return 1
    if len(matches) > 1:
        splits = ", ".join(split_name for split_name, _task in matches)
        print(f"Task id is ambiguous across splits: {task_id} ({splits})", file=sys.stderr)
        return 1
    if output.exists() and not force:
        print(f"Output already exists, use --force to overwrite: {output}", file=sys.stderr)
        return 1

    split_name, task = matches[0]
    if output.exists():
        shutil.rmtree(output)
    copy_task_to_workspace(task, output)
    write_json(output / TASK_META_FILENAME, _task_record(track.name, split_name, task))
    print(f"Prepared {task.id} from {track.name}/{split_name} at {output}")
    return 0


def _grade_task(
    config: HarnessConfig,
    track: TrackConfig,
    workspace: Path,
    output: Path | None,
    redact_output: bool,
) -> int:
    if not workspace.is_dir():
        print(f"Workspace does not exist: {workspace}", file=sys.stderr)
        return 1
    if not track.evaluator_command:
        print("No evaluator_command configured.", file=sys.stderr)
        return 1

    verifier_result = run_workspace_verifier(
        workspace, track.evaluator_command, config.timeout_seconds
    )
    record = {
        "timestamp": utc_timestamp(),
        "task": _read_workspace_task(workspace),
        "verifier": verifier_result.to_dict(),
        "score": verifier_result.score,
    }
    if output is not None:
        append_jsonl(output, record)
    if redact_output:
        record = _redacted_grade_record(record)
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if verifier_result.returncode == 0 else 1


def _init_fixtures(config: HarnessConfig) -> int:
    for track in config.tracks.values():
        for split_path in track.splits.values():
            ensure_dir(split_path)
    ensure_dir(config.output_dir)
    print("Fixture directories and runs directory are ready.")
    return 0


def _loop_run(config: HarnessConfig, args: argparse.Namespace) -> int:
    track = config.track(args.track)
    try:
        manifest = run_full_loop(
            experiment_dir=Path(args.experiment_dir),
            loop_id=str(args.loop_id),
            track=track.name,
            initial_skill=Path(args.initial_skill) if args.initial_skill else track.skill,
            edit_proposals=Path(args.edit_proposals),
            edit_budget=int(args.edit_budget),
            rollout_records=[Path(path) for path in args.rollout_records],
            parent_selection_records=Path(args.parent_selection_records),
            candidate_selection_records=Path(args.candidate_selection_records),
            best_selection_records=Path(args.best_selection_records)
            if args.best_selection_records
            else None,
            baseline_test_records=Path(args.baseline_test_records)
            if args.baseline_test_records
            else None,
            candidate_test_records=Path(args.candidate_test_records)
            if args.candidate_test_records
            else None,
            contaminated=bool(args.contaminated),
            contamination_reason=args.contamination_reason,
            rollout_isolation=args.rollout_isolation,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _loop_abort(config: HarnessConfig, args: argparse.Namespace) -> int:
    track = config.track(args.track)
    try:
        manifest = abort_loop(
            experiment_dir=Path(args.experiment_dir),
            loop_id=str(args.loop_id),
            track=track.name,
            initial_skill=Path(args.initial_skill),
            contamination_reason=str(args.contamination_reason),
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _epoch_run(config: HarnessConfig, args: argparse.Namespace) -> int:
    track = config.track(args.track)
    try:
        manifest = run_epoch_series(
            experiment_dir=Path(args.experiment_dir),
            track=track.name,
            initial_skill=Path(args.initial_skill) if args.initial_skill else track.skill,
            epochs=load_epoch_inputs(Path(args.epoch_inputs)),
            default_edit_budget=int(args.edit_budget),
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _iter_tasks(
    track: TrackConfig, split: str | None = None
) -> Iterable[tuple[str, TaskMetadata]]:
    split_items = track.splits.items()
    if split is not None:
        split_items = [(split, track.splits[split])]
    for split_name, split_path in split_items:
        if not split_path.exists() and split is None:
            continue
        for task in load_tasks(split_path):
            yield split_name, task


def _find_tasks(
    track: TrackConfig, task_id: str, split: str | None
) -> Iterable[tuple[str, TaskMetadata]]:
    for split_name, task in _iter_tasks(track, split):
        if task.id == task_id:
            yield split_name, task


def _task_record(track: str, split: str, task: TaskMetadata) -> dict[str, object]:
    return {
        "track": track,
        "split": split,
        "id": task.id,
        "description": task.description,
        "entrypoint": task.entrypoint,
        "source_path": str(task.path),
    }


def _read_workspace_task(workspace: Path) -> dict[str, object]:
    metadata_path = workspace / TASK_META_FILENAME
    if metadata_path.exists():
        return json.loads(metadata_path.read_text())

    task_json = workspace / "task.json"
    if task_json.exists():
        data = json.loads(task_json.read_text())
        return {
            "track": None,
            "split": None,
            "id": str(data.get("id", workspace.name)),
            "description": str(data.get("description", "")),
            "entrypoint": data.get("entrypoint"),
            "source_path": None,
        }

    return {
        "track": None,
        "split": None,
        "id": workspace.name,
        "description": "",
        "entrypoint": None,
        "source_path": None,
    }


def _redacted_grade_record(record: dict[str, object]) -> dict[str, object]:
    verifier = record.get("verifier")
    if not isinstance(verifier, dict):
        return record
    return {
        **record,
        "verifier": {
            "command": verifier.get("command"),
            "returncode": verifier.get("returncode"),
            "score": verifier.get("score"),
            "timed_out": verifier.get("timed_out"),
            "stdout": "<redacted>",
            "stderr": "<redacted>",
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
