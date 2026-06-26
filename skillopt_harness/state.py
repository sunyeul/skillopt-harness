from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class TaskMetadata:
    id: str
    path: Path
    description: str
    entrypoint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load_tasks(split_path: Path) -> list[TaskMetadata]:
    if not split_path.exists():
        raise FileNotFoundError(f"Split path does not exist: {split_path}")
    tasks: list[TaskMetadata] = []
    for task_json in sorted(split_path.glob("*/task.json")):
        data = read_json(task_json)
        tasks.append(
            TaskMetadata(
                id=str(data["id"]),
                path=task_json.parent,
                description=str(data["description"]),
                entrypoint=data.get("entrypoint"),
            )
        )
    return tasks


def average_score(records: Iterable[dict[str, Any]]) -> float:
    scores = [float(record.get("score", 0.0)) for record in records]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)
