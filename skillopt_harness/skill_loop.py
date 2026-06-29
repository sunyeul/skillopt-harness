from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

from .state import ensure_dir, read_jsonl, utc_timestamp, write_json
from .telemetry import set_attributes, start_span

EditOperation = Literal["add", "delete", "replace"]
EditPosition = Literal["before", "after", "end"]
GateDecision = Literal["accept_new_best", "accept", "reject"]
RolloutIsolation = Literal[
    "independent",
    "completed-before-output",
    "redacted-in-session",
    "unknown",
]


@dataclass(frozen=True)
class SkillEdit:
    id: str
    op: EditOperation
    target: str
    content: str = ""
    position: EditPosition = "end"
    score: float = 0.0
    rationale: str = ""
    evidence: list[str] = field(default_factory=list)
    section: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AppliedEdit:
    edit_id: str
    op: EditOperation
    status: Literal["applied", "failed"]
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class EpochInput:
    epoch_id: str
    edit_proposals: Path
    parent_selection_records: Path
    candidate_selection_records: Path
    slow_update: Path
    meta_skill: Path
    rollout_records: list[Path] = field(default_factory=list)
    edit_budget: int | None = None
    best_selection_records: Path | None = None
    contaminated: bool = False
    contamination_reason: str | None = None
    rollout_isolation: RolloutIsolation = "unknown"


def load_edit_proposals(path: Path) -> list[SkillEdit]:
    raw = path.read_text()
    items: Iterable[Any]
    if path.suffix == ".jsonl":
        items = [json.loads(line) for line in raw.splitlines() if line.strip()]
    else:
        data = json.loads(raw)
        if isinstance(data, dict) and "edits" in data:
            data = data["edits"]
        if not isinstance(data, list):
            raise ValueError("Edit proposal file must contain a JSON list or an edits list")
        items = data
    return [_parse_edit(item) for item in items]


def load_epoch_inputs(path: Path) -> list[EpochInput]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "epochs" in data:
        data = data["epochs"]
    if not isinstance(data, list):
        raise ValueError("Epoch input file must contain a JSON list or an epochs list")
    epochs = [_parse_epoch_input(item, index) for index, item in enumerate(data, start=1)]
    if not 2 <= len(epochs) <= 4:
        raise ValueError("epoch-run requires between 2 and 4 epochs")
    return epochs


def aggregate_edits(edits: Iterable[SkillEdit]) -> list[SkillEdit]:
    merged: dict[tuple[str, str, str, str, str], SkillEdit] = {}
    for edit in edits:
        key = (edit.op, edit.target, edit.content, edit.position, edit.section)
        if key not in merged:
            merged[key] = edit
            continue
        existing = merged[key]
        merged[key] = SkillEdit(
            id=existing.id,
            op=existing.op,
            target=existing.target,
            content=existing.content,
            position=existing.position,
            score=max(existing.score, edit.score),
            rationale=_merge_text(existing.rationale, edit.rationale),
            evidence=sorted(set(existing.evidence + edit.evidence)),
            section=existing.section,
        )
    return sorted(merged.values(), key=_edit_sort_key)


def select_edits(edits: Iterable[SkillEdit], budget: int) -> list[SkillEdit]:
    if budget < 1:
        raise ValueError("Edit budget must be at least 1")
    return sorted(edits, key=_edit_sort_key)[:budget]


def apply_edits(skill_text: str, edits: Iterable[SkillEdit]) -> tuple[str, list[AppliedEdit]]:
    updated = skill_text
    results: list[AppliedEdit] = []
    for edit in edits:
        updated, result = _apply_edit(updated, edit)
        results.append(result)
    return updated, results


def gate_candidate(
    parent_score: float,
    candidate_score: float,
    best_score: float,
    *,
    contaminated: bool = False,
    rollout_isolation: RolloutIsolation = "unknown",
) -> GateDecision:
    if contaminated:
        return "reject"
    if candidate_score <= parent_score:
        return "reject"
    if rollout_isolation == "unknown":
        return "reject"
    if candidate_score > best_score:
        return "accept_new_best"
    return "accept"


def abort_loop(
    *,
    experiment_dir: Path,
    loop_id: str,
    track: str,
    initial_skill: Path,
    contamination_reason: str,
) -> dict[str, Any]:
    if not contamination_reason:
        raise ValueError("--contamination-reason is required")

    ensure_dir(experiment_dir)
    loop_dir = experiment_dir / loop_id
    ensure_dir(loop_dir)
    initial_baseline = experiment_dir / "initial-baseline.md"
    current_best = experiment_dir / "current-best.md"
    best_skill = experiment_dir / "best-skill.md"

    if not initial_baseline.exists():
        shutil.copy2(initial_skill, initial_baseline)
    if not current_best.exists():
        shutil.copy2(initial_baseline, current_best)
    if not best_skill.exists():
        shutil.copy2(current_best, best_skill)

    parent_skill = loop_dir / "parent-skill.md"
    _copy_artifact(current_best, parent_skill)
    decision = {
        "timestamp": utc_timestamp(),
        "steps": ["baseline", "preflight", "early_contamination_abort"],
        "decision": "reject",
        "parent_score": None,
        "candidate_score": None,
        "best_score": None,
        "leakage_status": "contaminated",
        "contamination_reason": contamination_reason,
        "reject_reason": "contaminated_before_candidate_proposal",
        "rollout_isolation": "unknown",
        "parent_selection_records": None,
        "candidate_selection_records": None,
        "best_selection_records": None,
        "current_skill_output": str(current_best),
        "best_skill_output": str(best_skill),
    }
    write_json(loop_dir / "gate-decision.json", decision)
    (loop_dir / "decision.md").write_text(_decision_markdown(decision))

    manifest = {
        "timestamp": utc_timestamp(),
        "track": track,
        "loop_id": loop_id,
        "steps": ["baseline", "preflight", "early_contamination_abort"],
        "experiment_dir": str(experiment_dir),
        "loop_dir": str(loop_dir),
        "initial_baseline": str(initial_baseline),
        "current_best": str(current_best),
        "best_skill": str(best_skill),
        "parent_skill": str(parent_skill),
        "candidate_skill": None,
        "rollout_records": [],
        "reflected_edits": None,
        "aggregated_edits": None,
        "selected_edits": None,
        "edit_budget": None,
        "update_report": None,
        "gate_decision": str(loop_dir / "gate-decision.json"),
        "decision": "reject",
        "parent_score": None,
        "candidate_score": None,
        "best_score": None,
        "leakage_status": "contaminated",
        "contamination_reason": contamination_reason,
        "reject_reason": "contaminated_before_candidate_proposal",
        "rollout_isolation": "unknown",
    }
    write_json(loop_dir / "full-loop-manifest.json", manifest)
    return manifest


def run_full_loop(
    *,
    experiment_dir: Path,
    loop_id: str,
    track: str,
    initial_skill: Path,
    edit_proposals: Path,
    edit_budget: int,
    rollout_records: list[Path],
    parent_selection_records: Path,
    candidate_selection_records: Path,
    best_selection_records: Path | None = None,
    baseline_test_records: Path | None = None,
    candidate_test_records: Path | None = None,
    contaminated: bool = False,
    contamination_reason: str | None = None,
    rollout_isolation: RolloutIsolation = "unknown",
) -> dict[str, Any]:
    loop_dir = experiment_dir / loop_id
    with start_span(
        "skillopt.loop_run",
        {
            "skillopt.command": "loop-run",
            "skillopt.track": track,
            "skillopt.loop_id": loop_id,
            "skillopt.experiment_dir": experiment_dir,
            "skillopt.loop_dir": loop_dir,
            "skillopt.edit_budget": edit_budget,
            "skillopt.rollout_record_count": len(rollout_records),
            "skillopt.rollout_isolation": rollout_isolation,
            "skillopt.contaminated": contaminated,
        },
    ) as span:
        ensure_dir(experiment_dir)
        initial_baseline = experiment_dir / "initial-baseline.md"
        current_best = experiment_dir / "current-best.md"
        best_skill = experiment_dir / "best-skill.md"

        if not initial_baseline.exists():
            shutil.copy2(initial_skill, initial_baseline)
        if not current_best.exists():
            shutil.copy2(initial_baseline, current_best)
        if not best_skill.exists():
            shutil.copy2(current_best, best_skill)

        proposal = _run_loop_proposal(
            loop_dir=loop_dir,
            track=track,
            parent_skill=current_best,
            edit_proposals=edit_proposals,
            edit_budget=edit_budget,
            rollout_records=rollout_records,
        )
        gate = _run_loop_gate(
            loop_dir=loop_dir,
            parent_selection_records=parent_selection_records,
            candidate_selection_records=candidate_selection_records,
            best_selection_records=best_selection_records,
            baseline_test_records=baseline_test_records,
            candidate_test_records=candidate_test_records,
            current_skill_output=current_best,
            best_skill_output=best_skill,
            contaminated=contaminated,
            contamination_reason=contamination_reason,
            rollout_isolation=rollout_isolation,
        )
        set_attributes(
            span,
            {
                "skillopt.decision": gate["decision"],
                "skillopt.parent_score": gate["parent_score"],
                "skillopt.candidate_score": gate["candidate_score"],
                "skillopt.best_score": gate["best_score"],
                "skillopt.score_delta": gate["candidate_score"] - gate["parent_score"],
                "skillopt.leakage_status": gate["leakage_status"],
                "skillopt.reject_reason": gate["reject_reason"],
            },
        )

        manifest = {
            "timestamp": utc_timestamp(),
            "track": track,
            "loop_id": loop_id,
            "steps": ["baseline", "rollout", "reflect", "aggregate", "select", "update", "gate"],
            "experiment_dir": str(experiment_dir),
            "loop_dir": str(loop_dir),
            "initial_baseline": str(initial_baseline),
            "current_best": str(current_best),
            "best_skill": str(best_skill),
            "parent_skill": proposal["parent_skill"],
            "candidate_skill": proposal["candidate_skill"],
            "rollout_records": proposal["rollout_records"],
            "reflected_edits": proposal["reflected_edits"],
            "aggregated_edits": proposal["aggregated_edits"],
            "selected_edits": proposal["selected_edits"],
            "edit_budget": edit_budget,
            "update_report": proposal["update_report"],
            "gate_decision": str(loop_dir / "gate-decision.json"),
            "decision": gate["decision"],
            "parent_score": gate["parent_score"],
            "candidate_score": gate["candidate_score"],
            "best_score": gate["best_score"],
            "baseline_test_score": gate["baseline_test_score"],
            "candidate_test_score": gate["candidate_test_score"],
            "test_delta": gate["test_delta"],
            "baseline_test_records": gate["baseline_test_records"],
            "candidate_test_records": gate["candidate_test_records"],
            "leakage_status": gate["leakage_status"],
            "contamination_reason": gate["contamination_reason"],
            "reject_reason": gate["reject_reason"],
            "rollout_isolation": gate["rollout_isolation"],
        }
        write_json(loop_dir / "full-loop-manifest.json", manifest)
        return manifest


def run_epoch_series(
    *,
    experiment_dir: Path,
    track: str,
    initial_skill: Path,
    epochs: list[EpochInput],
    default_edit_budget: int,
) -> dict[str, Any]:
    if not 2 <= len(epochs) <= 4:
        raise ValueError("epoch-run requires between 2 and 4 epochs")
    if default_edit_budget < 1:
        raise ValueError("Edit budget must be at least 1")

    epoch_records: list[dict[str, Any]] = []
    for epoch in epochs:
        manifest = run_full_loop(
            experiment_dir=experiment_dir,
            loop_id=epoch.epoch_id,
            track=track,
            initial_skill=initial_skill,
            edit_proposals=epoch.edit_proposals,
            edit_budget=epoch.edit_budget or default_edit_budget,
            rollout_records=epoch.rollout_records,
            parent_selection_records=epoch.parent_selection_records,
            candidate_selection_records=epoch.candidate_selection_records,
            best_selection_records=epoch.best_selection_records,
            contaminated=epoch.contaminated,
            contamination_reason=epoch.contamination_reason,
            rollout_isolation=epoch.rollout_isolation,
        )
        epoch_dir = experiment_dir / epoch.epoch_id
        slow_update_copy = epoch_dir / "slow-update.md"
        meta_skill_copy = epoch_dir / "meta-skill.md"
        shutil.copy2(epoch.slow_update, slow_update_copy)
        shutil.copy2(epoch.meta_skill, meta_skill_copy)
        epoch_records.append(
            {
                **manifest,
                "epoch_id": epoch.epoch_id,
                "slow_update": str(slow_update_copy),
                "meta_skill": str(meta_skill_copy),
            }
        )

    final_manifest = {
        "timestamp": utc_timestamp(),
        "track": track,
        "steps": ["epoch_series"],
        "experiment_dir": str(experiment_dir),
        "epoch_count": len(epoch_records),
        "epochs": epoch_records,
        "initial_baseline": str(experiment_dir / "initial-baseline.md"),
        "current_best": str(experiment_dir / "current-best.md"),
        "best_skill": str(experiment_dir / "best-skill.md"),
    }
    write_json(experiment_dir / "multi-epoch-manifest.json", final_manifest)
    return final_manifest


def _run_loop_proposal(
    *,
    loop_dir: Path,
    track: str,
    parent_skill: Path,
    edit_proposals: Path,
    edit_budget: int,
    rollout_records: list[Path],
) -> dict[str, Any]:
    candidate_path = loop_dir / "candidate-skill.md"
    update_report_path = loop_dir / "update-report.json"
    with start_span(
        "skillopt.proposal",
        {
            "skillopt.track": track,
            "skillopt.edit_budget": edit_budget,
            "skillopt.rollout_record_count": len(rollout_records),
            "skillopt.candidate_skill_path": candidate_path,
            "skillopt.update_report_path": update_report_path,
        },
    ) as proposal_span:
        ensure_dir(loop_dir)
        copied_rollouts = _copy_artifacts(rollout_records, loop_dir / "rollouts")
        parent_copy = loop_dir / "parent-skill.md"
        reflected_copy = loop_dir / "reflected-edits.json"

        shutil.copy2(parent_skill, parent_copy)
        shutil.copy2(edit_proposals, reflected_copy)

        proposals = load_edit_proposals(edit_proposals)
        with start_span(
            "skillopt.aggregate_edits",
            {"skillopt.proposed_edit_count": len(proposals)},
        ) as aggregate_span:
            aggregated = aggregate_edits(proposals)
            set_attributes(
                aggregate_span,
                {"skillopt.aggregated_edit_count": len(aggregated)},
            )
        set_attributes(
            proposal_span,
            {
                "skillopt.proposed_edit_count": len(proposals),
                "skillopt.aggregated_edit_count": len(aggregated),
            },
        )

        with start_span(
            "skillopt.select_edits",
            {
                "skillopt.edit_budget": edit_budget,
                "skillopt.aggregated_edit_count": len(aggregated),
            },
        ) as select_span:
            selected = select_edits(aggregated, edit_budget)
            set_attributes(select_span, {"skillopt.selected_edit_count": len(selected)})
        set_attributes(proposal_span, {"skillopt.selected_edit_count": len(selected)})

        parent_text = parent_skill.read_text()
        write_json(loop_dir / "aggregated-edits.json", {"edits": _edits_to_dicts(aggregated)})
        write_json(loop_dir / "selected-edits.json", {"edits": _edits_to_dicts(selected)})
        with start_span(
            "skillopt.apply_edits",
            {"skillopt.selected_edit_count": len(selected)},
        ) as apply_span:
            validation_errors = _validate_selected_edits(parent_text, selected)
            if validation_errors:
                update_report = {
                    "timestamp": utc_timestamp(),
                    "applied": [],
                    "validation_errors": [item.to_dict() for item in validation_errors],
                    "failed_count": len(validation_errors),
                }
                write_json(update_report_path, update_report)
                set_attributes(
                    apply_span,
                    {
                        "skillopt.applied_edit_count": 0,
                        "skillopt.failed_edit_count": len(validation_errors),
                    },
                )
                set_attributes(
                    proposal_span,
                    {
                        "skillopt.applied_edit_count": 0,
                        "skillopt.failed_edit_count": len(validation_errors),
                    },
                )
                first_error = validation_errors[0].message
                raise ValueError(
                    f"Failed to validate {len(validation_errors)} selected edit(s): {first_error}"
                )

            candidate_text, applied = apply_edits(parent_text, selected)
            candidate_path.write_text(candidate_text)
            failed_count = sum(1 for item in applied if item.status == "failed")
            update_report = {
                "timestamp": utc_timestamp(),
                "applied": [item.to_dict() for item in applied],
                "validation_errors": [],
                "failed_count": failed_count,
            }
            write_json(update_report_path, update_report)
            applied_count = sum(1 for item in applied if item.status == "applied")
            set_attributes(
                apply_span,
                {
                    "skillopt.applied_edit_count": applied_count,
                    "skillopt.failed_edit_count": failed_count,
                },
            )
            set_attributes(
                proposal_span,
                {
                    "skillopt.applied_edit_count": applied_count,
                    "skillopt.failed_edit_count": failed_count,
                },
            )

        manifest = {
            "timestamp": utc_timestamp(),
            "track": track,
            "steps": ["rollout", "reflect", "aggregate", "select", "update"],
            "parent_skill": str(parent_copy),
            "rollout_records": [str(path) for path in copied_rollouts],
            "reflected_edits": str(reflected_copy),
            "aggregated_edits": str(loop_dir / "aggregated-edits.json"),
            "selected_edits": str(loop_dir / "selected-edits.json"),
            "candidate_skill": str(candidate_path),
            "edit_budget": edit_budget,
            "update_report": str(update_report_path),
        }
        write_json(loop_dir / "manifest.json", manifest)
        if update_report["failed_count"]:
            raise ValueError(f"Failed to apply {update_report['failed_count']} selected edit(s)")
        return manifest


def _run_loop_gate(
    *,
    loop_dir: Path,
    parent_selection_records: Path,
    candidate_selection_records: Path,
    best_selection_records: Path | None,
    baseline_test_records: Path | None,
    candidate_test_records: Path | None,
    current_skill_output: Path | None,
    best_skill_output: Path | None,
    contaminated: bool = False,
    contamination_reason: str | None = None,
    rollout_isolation: RolloutIsolation = "unknown",
) -> dict[str, Any]:
    with start_span(
        "skillopt.gate",
        {
            "skillopt.rollout_isolation": rollout_isolation,
            "skillopt.contaminated": contaminated,
            "skillopt.leakage_status": "contaminated" if contaminated else "clean",
        },
    ) as gate_span:
        ensure_dir(loop_dir)
        if contaminated and not contamination_reason:
            raise ValueError("--contamination-reason is required when --contaminated is set")
        parent_records_copy = loop_dir / "parent-selection.jsonl"
        candidate_records_copy = loop_dir / "candidate-selection.jsonl"
        parent_records_copy = _copy_artifact(parent_selection_records, parent_records_copy)
        candidate_records_copy = _copy_artifact(
            candidate_selection_records, candidate_records_copy
        )

        parent_task_ids = _selection_task_ids(parent_selection_records)
        candidate_task_ids = _selection_task_ids(candidate_selection_records)
        if parent_task_ids != candidate_task_ids:
            raise ValueError(
                "Parent and candidate selection tasks differ: "
                f"parent={parent_task_ids}, candidate={candidate_task_ids}"
            )

        with start_span(
            "skillopt.score_parent",
            {
                "skillopt.record_path": parent_selection_records,
                "skillopt.selection_task_count": len(parent_task_ids),
            },
        ) as parent_span:
            parent_score = _selection_score(parent_selection_records)
            parent_summary = _record_summary(parent_selection_records)
            set_attributes(
                parent_span,
                {
                    "skillopt.score": parent_score,
                    "skillopt.passed_count": parent_summary["passed_count"],
                    "skillopt.failed_count": parent_summary["failed_count"],
                },
            )

        with start_span(
            "skillopt.score_candidate",
            {
                "skillopt.record_path": candidate_selection_records,
                "skillopt.selection_task_count": len(candidate_task_ids),
            },
        ) as candidate_span:
            candidate_score = _selection_score(candidate_selection_records)
            candidate_summary = _record_summary(candidate_selection_records)
            set_attributes(
                candidate_span,
                {
                    "skillopt.score": candidate_score,
                    "skillopt.passed_count": candidate_summary["passed_count"],
                    "skillopt.failed_count": candidate_summary["failed_count"],
                },
            )

        best_score = (
            _selection_score(best_selection_records)
            if best_selection_records is not None
            else parent_score
        )
        test_comparison = _test_comparison(
            loop_dir=loop_dir,
            baseline_test_records=baseline_test_records,
            candidate_test_records=candidate_test_records,
        )
        with start_span(
            "skillopt.decide",
            {
                "skillopt.parent_score": parent_score,
                "skillopt.candidate_score": candidate_score,
                "skillopt.best_score": best_score,
                "skillopt.score_delta": candidate_score - parent_score,
                "skillopt.rollout_isolation": rollout_isolation,
                "skillopt.leakage_status": "contaminated" if contaminated else "clean",
            },
        ) as decide_span:
            decision = gate_candidate(
                parent_score,
                candidate_score,
                best_score,
                contaminated=contaminated,
                rollout_isolation=rollout_isolation,
            )
            reject_reason = _reject_reason(
                decision=decision,
                parent_score=parent_score,
                candidate_score=candidate_score,
                contaminated=contaminated,
                rollout_isolation=rollout_isolation,
            )
            set_attributes(
                decide_span,
                {
                    "skillopt.decision": decision,
                    "skillopt.reject_reason": reject_reason,
                },
            )

        candidate_skill = loop_dir / "candidate-skill.md"
        if decision in {"accept", "accept_new_best"} and current_skill_output is not None:
            _copy_if_exists(candidate_skill, current_skill_output)
        if decision == "accept_new_best" and best_skill_output is not None:
            _copy_if_exists(candidate_skill, best_skill_output)

        record = {
            "timestamp": utc_timestamp(),
            "steps": ["gate"],
            "decision": decision,
            "parent_score": parent_score,
            "candidate_score": candidate_score,
            "best_score": best_score,
            **test_comparison,
            "leakage_status": "contaminated" if contaminated else "clean",
            "contamination_reason": contamination_reason if contaminated else None,
            "rollout_isolation": rollout_isolation,
            "reject_reason": reject_reason,
            "parent_selection_records": str(parent_records_copy),
            "candidate_selection_records": str(candidate_records_copy),
            "best_selection_records": str(best_selection_records)
            if best_selection_records is not None
            else None,
            "current_skill_output": str(current_skill_output)
            if current_skill_output is not None
            else None,
            "best_skill_output": str(best_skill_output) if best_skill_output is not None else None,
        }
        set_attributes(
            gate_span,
            {
                "skillopt.decision": decision,
                "skillopt.parent_score": parent_score,
                "skillopt.candidate_score": candidate_score,
                "skillopt.best_score": best_score,
                "skillopt.score_delta": candidate_score - parent_score,
                "skillopt.leakage_status": record["leakage_status"],
                "skillopt.reject_reason": reject_reason,
            },
        )
        write_json(loop_dir / "gate-decision.json", record)
        (loop_dir / "decision.md").write_text(_decision_markdown(record))
        return record


def _parse_epoch_input(data: Any, index: int) -> EpochInput:
    if not isinstance(data, dict):
        raise ValueError(f"Epoch input {index} must be a JSON object")
    required = [
        "edit_proposals",
        "parent_selection_records",
        "candidate_selection_records",
        "slow_update",
        "meta_skill",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Epoch input {index} is missing required keys: {joined}")

    contaminated = bool(data.get("contaminated", False))
    contamination_reason = data.get("contamination_reason")
    if contaminated and not contamination_reason:
        raise ValueError(
            f"Epoch input {index} requires contamination_reason when contaminated is true"
        )
    edit_budget = data.get("edit_budget")
    if edit_budget is not None:
        edit_budget = int(edit_budget)
        if edit_budget < 1:
            raise ValueError(f"Epoch input {index} edit_budget must be at least 1")
    rollout_isolation = str(data.get("rollout_isolation", "unknown"))
    if rollout_isolation not in {
        "independent",
        "completed-before-output",
        "redacted-in-session",
        "unknown",
    }:
        raise ValueError(f"Epoch input {index} has unsupported rollout_isolation")

    return EpochInput(
        epoch_id=str(data.get("epoch_id") or f"epoch-{index:02d}"),
        rollout_records=_parse_path_list(data.get("rollout_records", []), "rollout_records"),
        edit_proposals=Path(str(data["edit_proposals"])),
        edit_budget=edit_budget,
        parent_selection_records=Path(str(data["parent_selection_records"])),
        candidate_selection_records=Path(str(data["candidate_selection_records"])),
        best_selection_records=Path(str(data["best_selection_records"]))
        if data.get("best_selection_records")
        else None,
        slow_update=Path(str(data["slow_update"])),
        meta_skill=Path(str(data["meta_skill"])),
        contaminated=contaminated,
        contamination_reason=str(contamination_reason) if contamination_reason else None,
        rollout_isolation=rollout_isolation,  # type: ignore[arg-type]
    )


def _parse_edit(data: Any) -> SkillEdit:
    if not isinstance(data, dict):
        raise ValueError("Each edit proposal must be a JSON object")
    op = str(data.get("op", ""))
    if op not in {"add", "delete", "replace"}:
        raise ValueError(f"Unsupported edit op: {op}")
    position = str(data.get("position", "end"))
    if position not in {"before", "after", "end"}:
        raise ValueError(f"Unsupported edit position: {position}")
    evidence = data.get("evidence", [])
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        raise ValueError("Edit evidence must be a string or list")
    return SkillEdit(
        id=str(data.get("id") or _default_edit_id(data)),
        op=op,  # type: ignore[arg-type]
        target=str(data.get("target", "")),
        content=str(data.get("content", "")),
        position=position,  # type: ignore[arg-type]
        score=float(data.get("score", 0.0)),
        rationale=str(data.get("rationale", "")),
        evidence=[str(item) for item in evidence],
        section=str(data.get("section", "")),
    )


def _selection_score(path: Path) -> float:
    return _record_score(path, "Selection")


def _record_score(path: Path, label: str) -> float:
    records = read_jsonl(path)
    if not records:
        raise ValueError(f"{label} records are empty: {path}")
    scores: list[float] = []
    for index, record in enumerate(records, start=1):
        if "score" not in record:
            raise ValueError(f"{label} record {index} is missing score: {path}")
        scores.append(float(record["score"]))
    return sum(scores) / len(scores)


def _record_summary(path: Path) -> dict[str, int | float]:
    records = read_jsonl(path)
    scores = [float(record["score"]) for record in records if "score" in record]
    passed_count = sum(1 for score in scores if score >= 1.0)
    failed_count = len(scores) - passed_count
    return {
        "task_count": len(records),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "score": sum(scores) / len(scores) if scores else 0.0,
    }


def _test_comparison(
    *,
    loop_dir: Path,
    baseline_test_records: Path | None,
    candidate_test_records: Path | None,
) -> dict[str, Any]:
    if baseline_test_records is None and candidate_test_records is None:
        return {
            "baseline_test_score": None,
            "candidate_test_score": None,
            "test_delta": None,
            "baseline_test_records": None,
            "candidate_test_records": None,
        }
    if baseline_test_records is None or candidate_test_records is None:
        raise ValueError(
            "--baseline-test-records and --candidate-test-records must be provided together"
        )

    baseline_task_ids = _record_task_ids(baseline_test_records, "Baseline test")
    candidate_task_ids = _record_task_ids(candidate_test_records, "Candidate test")
    if baseline_task_ids != candidate_task_ids:
        raise ValueError(
            "Baseline and candidate test tasks differ: "
            f"baseline={baseline_task_ids}, candidate={candidate_task_ids}"
        )

    baseline_records_copy = _copy_artifact(
        baseline_test_records, loop_dir / "baseline-test-reporting-only.jsonl"
    )
    candidate_records_copy = _copy_artifact(
        candidate_test_records, loop_dir / "candidate-test-reporting-only.jsonl"
    )
    baseline_score = _record_score(baseline_test_records, "Baseline test")
    candidate_score = _record_score(candidate_test_records, "Candidate test")
    return {
        "baseline_test_score": baseline_score,
        "candidate_test_score": candidate_score,
        "test_delta": candidate_score - baseline_score,
        "baseline_test_records": str(baseline_records_copy),
        "candidate_test_records": str(candidate_records_copy),
    }


def _default_edit_id(data: dict[str, Any]) -> str:
    op = str(data.get("op", "edit"))
    target = str(data.get("target", "target")).strip().replace(" ", "-")[:40]
    return f"{op}-{target or 'skill'}"


def _parse_path_list(data: Any, field_name: str) -> list[Path]:
    if isinstance(data, str):
        return [Path(data)]
    if not isinstance(data, list):
        raise ValueError(f"{field_name} must be a string or list")
    return [Path(str(item)) for item in data]


def _edit_sort_key(edit: SkillEdit) -> tuple[float, str]:
    return (-edit.score, edit.id)


def _merge_text(first: str, second: str) -> str:
    if not first:
        return second
    if not second or second == first:
        return first
    return f"{first}\n{second}"


def _reject_reason(
    *,
    decision: GateDecision,
    parent_score: float,
    candidate_score: float,
    contaminated: bool,
    rollout_isolation: RolloutIsolation,
) -> str | None:
    if decision != "reject":
        return None
    if contaminated:
        return "contaminated"
    if candidate_score > parent_score and rollout_isolation == "unknown":
        return "unknown_rollout_isolation"
    if candidate_score == parent_score:
        return "tie"
    if candidate_score < parent_score:
        return "regression"
    return "not_strict_improvement"


def _edits_to_dicts(edits: Iterable[SkillEdit]) -> list[dict[str, Any]]:
    return [edit.to_dict() for edit in edits]


def _apply_edit(skill_text: str, edit: SkillEdit) -> tuple[str, AppliedEdit]:
    if edit.op == "add":
        return _apply_add(skill_text, edit)
    if not edit.target:
        return skill_text, AppliedEdit(edit.id, edit.op, "failed", "target is required")
    count = skill_text.count(edit.target)
    if count != 1:
        return skill_text, AppliedEdit(
            edit.id,
            edit.op,
            "failed",
            f"target matched {count} times; expected exactly 1",
        )
    if edit.op == "delete":
        return (
            skill_text.replace(edit.target, "", 1),
            AppliedEdit(edit.id, edit.op, "applied", "deleted target text"),
        )
    return (
        skill_text.replace(edit.target, edit.content, 1),
        AppliedEdit(edit.id, edit.op, "applied", "replaced target text"),
    )


def _apply_add(skill_text: str, edit: SkillEdit) -> tuple[str, AppliedEdit]:
    content = _surround_with_blank_lines(edit.content)
    if edit.position == "end" or not edit.target:
        return (
            skill_text.rstrip() + content,
            AppliedEdit(edit.id, edit.op, "applied", "appended content"),
        )
    count = skill_text.count(edit.target)
    if count != 1:
        return skill_text, AppliedEdit(
            edit.id,
            edit.op,
            "failed",
            f"target matched {count} times; expected exactly 1",
        )
    if edit.position == "before":
        return (
            skill_text.replace(edit.target, content.lstrip("\n") + edit.target, 1),
            AppliedEdit(edit.id, edit.op, "applied", "inserted content before target"),
        )
    return (
        skill_text.replace(edit.target, edit.target + content, 1),
        AppliedEdit(edit.id, edit.op, "applied", "inserted content after target"),
    )


def _surround_with_blank_lines(text: str) -> str:
    return "\n\n" + text.strip() + "\n"


def _validate_selected_edits(skill_text: str, edits: Iterable[SkillEdit]) -> list[AppliedEdit]:
    errors: list[AppliedEdit] = []
    for edit in edits:
        if edit.position != "end" or edit.target:
            count = skill_text.count(edit.target)
            if count != 1:
                errors.append(
                    AppliedEdit(
                        edit.id,
                        edit.op,
                        "failed",
                        f"target matched {count} times; expected exactly 1",
                    )
                )
                continue
        if not edit.section:
            continue
        if edit.position == "end":
            errors.append(
                AppliedEdit(
                    edit.id,
                    edit.op,
                    "failed",
                    "section edit cannot use position=end",
                )
            )
            continue
        bounds = _section_bounds(skill_text, edit.section)
        if bounds is None:
            errors.append(
                AppliedEdit(edit.id, edit.op, "failed", f"section not found: {edit.section}")
            )
            continue
        target_index = skill_text.find(edit.target)
        section_start, section_end = bounds
        if target_index < section_start or target_index >= section_end:
            errors.append(
                AppliedEdit(
                    edit.id,
                    edit.op,
                    "failed",
                    f"target is outside section {edit.section}",
                )
            )
    return errors


def _section_bounds(skill_text: str, heading: str) -> tuple[int, int] | None:
    start = skill_text.find(heading)
    if start < 0:
        return None
    next_heading = re.search(r"(?m)^## ", skill_text[start + len(heading) :])
    if next_heading is None:
        return (start, len(skill_text))
    return (start, start + len(heading) + next_heading.start())


def _copy_artifacts(paths: list[Path], destination: Path) -> list[Path]:
    if not paths:
        return []
    ensure_dir(destination)
    copied: list[Path] = []
    for path in paths:
        output = destination / path.name
        copied.append(_copy_artifact(path, output))
    return copied


def _copy_artifact(source: Path, destination: Path) -> Path:
    ensure_dir(destination.parent)
    if source.resolve() == destination.resolve():
        return destination
    shutil.copy2(source, destination)
    return destination


def _copy_if_exists(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Candidate skill not found: {source}")
    ensure_dir(destination.parent)
    shutil.copy2(source, destination)


def _decision_markdown(record: dict[str, Any]) -> str:
    contamination_reason = record.get("contamination_reason")
    contamination_line = (
        [f"- Contamination reason: {contamination_reason}", ""]
        if contamination_reason
        else []
    )
    test_lines: list[str] = []
    if record.get("baseline_test_score") is not None or record.get("candidate_test_score") is not None:
        test_lines = [
            "## Reporting-Only Test Comparison",
            "",
            f"- Baseline test score: `{_format_score(record.get('baseline_test_score'))}`",
            f"- Candidate test score: `{_format_score(record.get('candidate_test_score'))}`",
            f"- Test delta: `{_format_score(record.get('test_delta'))}`",
            "",
            "This comparison is post-adoption reporting only. Test scores must not "
            "affect the selection gate or later candidate edits.",
            "",
        ]
    return "\n".join(
        [
            "# SkillOpt Gate Decision",
            "",
            f"- Decision: `{record['decision']}`",
            f"- Leakage status: `{record['leakage_status']}`",
            *contamination_line,
            f"- Parent selection score: `{_format_score(record['parent_score'])}`",
            f"- Candidate selection score: `{_format_score(record['candidate_score'])}`",
            f"- Best selection score: `{_format_score(record['best_score'])}`",
            f"- Rollout isolation: `{record.get('rollout_isolation', 'unknown')}`",
            "",
            "Strict improvement is required over the parent/current skill. "
            "`accept_new_best` additionally requires improvement over the recorded best.",
            "",
            *test_lines,
        ]
    )


def _format_score(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}"


def _selection_task_ids(path: Path) -> list[str]:
    return _record_task_ids(path, "Selection")


def _record_task_ids(path: Path, label: str) -> list[str]:
    records = read_jsonl(path)
    if not records:
        raise ValueError(f"{label} records are empty: {path}")
    task_ids: list[str] = []
    for index, record in enumerate(records, start=1):
        task = record.get("task")
        if not isinstance(task, dict) or "id" not in task:
            raise ValueError(f"{label} record {index} is missing task.id: {path}")
        task_ids.append(str(task["id"]))
    return task_ids
