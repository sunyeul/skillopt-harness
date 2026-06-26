from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from .state import TaskMetadata


@dataclass(frozen=True)
class VerifierResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def copy_task_to_workspace(task: TaskMetadata, workspace: Path) -> None:
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(
        task.path,
        workspace,
        ignore=shutil.ignore_patterns("answer_key.json", "tests_hidden"),
    )


def run_workspace_verifier(
    workspace: Path, command: list[str], timeout_seconds: int
) -> VerifierResult:
    source_path = _workspace_source_path(workspace)
    hidden_tests = source_path / "tests_hidden" if source_path is not None else None
    if hidden_tests is None or not hidden_tests.is_dir():
        return run_verifier(workspace, command, timeout_seconds)

    with tempfile.TemporaryDirectory(prefix="skillopt-grade-") as tmp:
        grading_workspace = Path(tmp) / "workspace"
        shutil.copytree(workspace, grading_workspace)
        shutil.copytree(hidden_tests, grading_workspace / "tests_hidden")
        return run_verifier(grading_workspace, command, timeout_seconds)


def run_verifier(
    workspace: Path, command: list[str], timeout_seconds: int
) -> VerifierResult:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    repo_root = Path(__file__).resolve().parents[1]
    paths = [str(workspace), str(repo_root)]
    if pythonpath:
        paths.append(pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return VerifierResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
            score=1.0 if completed.returncode == 0 else 0.0,
        )
    except subprocess.TimeoutExpired as exc:
        return VerifierResult(
            command=command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or f"Verifier timed out after {timeout_seconds}s",
            timed_out=True,
            score=0.0,
        )


def _workspace_source_path(workspace: Path) -> Path | None:
    metadata_path = workspace / ".skillopt-task.json"
    if not metadata_path.exists():
        return None
    try:
        import json

        metadata = json.loads(metadata_path.read_text())
    except json.JSONDecodeError:
        return None
    source_path = metadata.get("source_path")
    if not source_path:
        return None
    return Path(str(source_path))
