from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_KEYS = {"timeout_seconds", "output_dir", "tracks"}
TRACK_KEYS = {"skill", "evaluator_command", "splits"}
SPLIT_NAMES = {"train", "selection", "test"}


@dataclass(frozen=True)
class TrackConfig:
    name: str
    skill: Path
    splits: dict[str, Path]
    evaluator_command: list[str]


@dataclass(frozen=True)
class HarnessConfig:
    tracks: dict[str, TrackConfig]
    timeout_seconds: int
    output_dir: Path

    def track(self, name: str) -> TrackConfig:
        try:
            return self.tracks[name]
        except KeyError as exc:
            available = ", ".join(sorted(self.tracks))
            raise KeyError(f"Unknown track: {name}. Available tracks: {available}") from exc


def load_config(path: Path) -> HarnessConfig:
    data = _parse_simple_yaml(path.read_text())
    _validate_top_level_keys(data)
    root = path.parent
    return HarnessConfig(
        tracks=_parse_tracks(root, _require_mapping(data, "tracks")),
        timeout_seconds=int(data["timeout_seconds"]),
        output_dir=_resolve_path(root, data["output_dir"]),
    )


def _validate_top_level_keys(data: dict[str, Any]) -> None:
    unknown = sorted(set(data) - CONFIG_KEYS)
    if unknown:
        raise ValueError(f"Unsupported config keys: {', '.join(unknown)}")
    missing = sorted(CONFIG_KEYS - set(data))
    if missing:
        raise ValueError(f"Missing config keys: {', '.join(missing)}")


def _parse_tracks(root: Path, tracks_data: dict[str, Any]) -> dict[str, TrackConfig]:
    tracks: dict[str, TrackConfig] = {}
    for track_name, track_data in tracks_data.items():
        if not isinstance(track_data, dict):
            raise ValueError(f"tracks.{track_name} must be a map")
        unknown = sorted(set(track_data) - TRACK_KEYS)
        if unknown:
            raise ValueError(f"Unsupported track keys for {track_name}: {', '.join(unknown)}")
        missing = sorted(TRACK_KEYS - set(track_data))
        if missing:
            raise ValueError(f"Missing track keys for {track_name}: {', '.join(missing)}")

        splits = _require_mapping(track_data, "splits")
        missing_splits = sorted(SPLIT_NAMES - set(splits))
        if missing_splits:
            raise ValueError(f"Missing splits for {track_name}: {', '.join(missing_splits)}")
        tracks[str(track_name)] = TrackConfig(
            name=str(track_name),
            skill=_resolve_path(root, track_data["skill"]),
            splits={name: _resolve_path(root, value) for name, value in splits.items()},
            evaluator_command=[
                str(value) for value in _require_list(track_data, "evaluator_command")
            ],
        )
    if not tracks:
        raise ValueError("tracks must be a non-empty map")
    return tracks


def _require_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data[key]
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{key} must be a non-empty map")
    return value


def _require_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data[key]
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    return value


def _resolve_path(root: Path, value: Any) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return root / path


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, result)]

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"List item without list parent: {raw_line}")
            parent.append(_parse_scalar(line[2:].strip()))
            continue

        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid config line: {raw_line}")
        key = key.strip()
        value = value.strip()
        if not isinstance(parent, dict):
            raise ValueError(f"Map item without map parent: {raw_line}")
        if value:
            parent[key] = _parse_scalar(value)
            continue

        child: dict[str, Any] | list[Any]
        child = [] if _next_meaningful_line_is_list(text, raw_line) else {}
        parent[key] = child
        stack.append((indent, child))

    return result


def _next_meaningful_line_is_list(text: str, current_line: str) -> bool:
    lines = text.splitlines()
    try:
        start = lines.index(current_line) + 1
    except ValueError:
        return False
    current_indent = len(current_line) - len(current_line.lstrip(" "))
    for raw_line in lines[start:]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent <= current_indent:
            return False
        return raw_line.strip().startswith("- ")
    return False


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    try:
        return int(value)
    except ValueError:
        return value
