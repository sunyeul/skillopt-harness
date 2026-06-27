from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from skillopt_harness.cli import main
from skillopt_harness.config import load_config
from skillopt_harness.state import read_jsonl


class CliTests(unittest.TestCase):
    def test_load_config_uses_minimal_harness_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "skillopt.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "timeout_seconds: 30",
                        "output_dir: local-runs",
                        "tracks:",
                        "  code_repair:",
                        "    skill: .codex/skills/code-repair/SKILL.md",
                        "    evaluator_command:",
                        "      - pytest",
                        "    splits:",
                        "      train: fixtures/code_repair/train",
                        "      selection: fixtures/code_repair/selection",
                        "      test: fixtures/code_repair/test",
                        "",
                    ]
                )
            )

            config = load_config(config_path)

            self.assertEqual(config.timeout_seconds, 30)
            self.assertEqual(config.output_dir, root / "local-runs")
            track = config.track("code_repair")
            self.assertEqual(track.evaluator_command, ["pytest"])
            self.assertEqual(track.splits["train"], root / "fixtures/code_repair/train")
            self.assertEqual(track.skill, root / ".codex/skills/code-repair/SKILL.md")

    def test_load_config_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "skillopt.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "timeout_seconds: 30",
                        "unknown_key: value",
                        "output_dir: runs",
                        "tracks:",
                        "  code_repair:",
                        "    skill: .codex/skills/code-repair/SKILL.md",
                        "    evaluator_command:",
                        "      - pytest",
                        "    splits:",
                        "      train: fixtures/code_repair/train",
                        "      selection: fixtures/code_repair/selection",
                        "      test: fixtures/code_repair/test",
                        "",
                    ]
                )
            )

            with self.assertRaisesRegex(ValueError, "Unsupported config keys: unknown_key"):
                load_config(config_path)

    def test_list_tasks_prints_split_task_and_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "skillopt.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "timeout_seconds: 30",
                        "output_dir: runs",
                        "tracks:",
                        "  code_repair:",
                        "    skill: .codex/skills/code-repair/SKILL.md",
                        "    evaluator_command:",
                        f"      - {sys.executable}",
                        "      - -m",
                        "      - pytest",
                        "      - -q",
                        "      - tests_visible",
                        "      - tests_hidden",
                        "    splits:",
                        "      train: fixtures/code_repair/train",
                        "      selection: fixtures/code_repair/selection",
                        "      test: fixtures/code_repair/test",
                        "  data_normalization:",
                        "    skill: .codex/skills/data-normalization/SKILL.md",
                        "    evaluator_command:",
                        f"      - {sys.executable}",
                        "      - -m",
                        "      - pytest",
                        "      - -q",
                        "      - tests_visible",
                        "      - tests_hidden",
                        "    splits:",
                        "      train: fixtures/data_normalization/train",
                        "      selection: fixtures/data_normalization/selection",
                        "      test: fixtures/data_normalization/test",
                        "",
                    ]
                )
            )
            _write_task(root / "fixtures/code_repair/train/demo", "train-demo")

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "list-tasks",
                        "--track",
                        "code_repair",
                        "--split",
                        "train",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertEqual(
                stdout.getvalue().strip(), "code_repair\ttrain\ttrain-demo\trepair add"
            )

    def test_prepare_task_copies_fixture_and_writes_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            _write_task(root / "fixtures/code_repair/train/demo", "train-demo")
            workspace = root / "workspaces/train-demo"

            code = main(
                [
                    "--config",
                    str(config_path),
                    "prepare-task",
                    "--track",
                    "code_repair",
                    "--task",
                    "train-demo",
                    "--split",
                    "train",
                    "--output",
                    str(workspace),
                ]
            )

            self.assertEqual(code, 0)
            self.assertTrue((workspace / "calc.py").exists())
            metadata = json.loads((workspace / ".skillopt-task.json").read_text())
            self.assertEqual(metadata["track"], "code_repair")
            self.assertEqual(metadata["id"], "train-demo")
            self.assertEqual(metadata["split"], "train")
            self.assertEqual(metadata["entrypoint"], "calc.py")

    def test_prepare_task_rejects_existing_workspace_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            _write_task(root / "fixtures/code_repair/train/demo", "train-demo")
            workspace = root / "workspace"
            workspace.mkdir()

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "prepare-task",
                        "--track",
                        "code_repair",
                        "--task",
                        "train-demo",
                        "--output",
                        str(workspace),
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("use --force", stderr.getvalue())

    def test_prepare_task_force_replaces_existing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            _write_task(root / "fixtures/code_repair/train/demo", "train-demo")
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "stale.txt").write_text("old")

            code = main(
                [
                    "--config",
                    str(config_path),
                    "prepare-task",
                    "--track",
                    "code_repair",
                    "--task",
                    "train-demo",
                    "--output",
                    str(workspace),
                    "--force",
                ]
            )

            self.assertEqual(code, 0)
            self.assertFalse((workspace / "stale.txt").exists())
            self.assertTrue((workspace / "calc.py").exists())

    def test_grade_task_records_passing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            workspace = root / "workspace"
            _write_task(workspace, "manual-demo", body="def add(a, b):\n    return a + b\n")
            (workspace / ".skillopt-task.json").write_text(
                json.dumps(
                    {
                        "split": "train",
                        "track": "code_repair",
                        "id": "manual-demo",
                        "description": "repair add",
                        "entrypoint": "calc.py",
                        "source_path": "fixture",
                    }
                )
            )
            output = root / "runs/manual.jsonl"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "grade-task",
                        "--track",
                        "code_repair",
                        "--workspace",
                        str(workspace),
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(code, 0)
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["score"], 1.0)
            records = read_jsonl(output)
            self.assertEqual(records[0]["task"]["id"], "manual-demo")
            self.assertEqual(records[0]["score"], 1.0)
            self.assertEqual(records[0]["verifier"]["returncode"], 0)

    def test_grade_task_records_failing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            workspace = root / "workspace"
            _write_task(workspace, "manual-demo")

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "grade-task",
                        "--track",
                        "code_repair",
                        "--workspace",
                        str(workspace),
                    ]
                )

            self.assertEqual(code, 1)
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["score"], 0.0)
            self.assertNotEqual(printed["verifier"]["returncode"], 0)

    def test_grade_task_redact_output_hides_terminal_diagnostics_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            workspace = root / "workspace"
            _write_task(workspace, "manual-demo")
            output = root / "runs/manual.jsonl"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "grade-task",
                        "--track",
                        "code_repair",
                        "--workspace",
                        str(workspace),
                        "--output",
                        str(output),
                        "--redact-output",
                    ]
                )

            self.assertEqual(code, 1)
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["score"], 0.0)
            self.assertEqual(printed["verifier"]["stdout"], "<redacted>")
            self.assertEqual(printed["verifier"]["stderr"], "<redacted>")
            self.assertIn("returncode", printed["verifier"])
            records = read_jsonl(output)
            self.assertNotEqual(records[0]["verifier"]["stdout"], "<redacted>")

    def test_data_normalization_grade_task_uses_pytest_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            task_dir = root / "fixtures/data_normalization/train/demo"
            _write_data_task(task_dir, "data-demo")
            workspace = root / "data-workspace"

            prepare_code = main(
                [
                    "--config",
                    str(config_path),
                    "prepare-task",
                    "--track",
                    "data_normalization",
                    "--task",
                    "data-demo",
                    "--split",
                    "train",
                    "--output",
                    str(workspace),
                ]
            )
            self.assertEqual(prepare_code, 0)
            (workspace / "names.py").write_text(
                "def normalize_names(names):\n"
                "    return [name.strip().title() for name in names]\n"
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "grade-task",
                        "--track",
                        "data_normalization",
                        "--workspace",
                        str(workspace),
                    ]
                )

            self.assertEqual(code, 0)
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["score"], 1.0)
            self.assertEqual(printed["task"]["track"], "data_normalization")

    def test_prepare_data_normalization_task_does_not_copy_hidden_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            task_dir = root / "fixtures/data_normalization/train/demo"
            _write_data_task(task_dir, "data-demo")
            workspace = root / "workspace"

            code = main(
                [
                    "--config",
                    str(config_path),
                    "prepare-task",
                    "--track",
                    "data_normalization",
                    "--task",
                    "data-demo",
                    "--split",
                    "train",
                    "--output",
                    str(workspace),
                ]
            )

            self.assertEqual(code, 0)
            self.assertTrue((workspace / "task.json").exists())
            self.assertTrue((workspace / "tests_visible").is_dir())
            self.assertFalse((workspace / "tests_hidden").exists())

    def test_prepare_code_repair_task_does_not_copy_hidden_tests_but_grade_uses_them(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "skillopt.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "timeout_seconds: 30",
                        "output_dir: runs",
                        "tracks:",
                        "  code_repair:",
                        "    skill: .codex/skills/code-repair/SKILL.md",
                        "    evaluator_command:",
                        f"      - {sys.executable}",
                        "      - -m",
                        "      - pytest",
                        "      - -q",
                        "      - tests_visible",
                        "      - tests_hidden",
                        "    splits:",
                        "      train: fixtures/code_repair/train",
                        "      selection: fixtures/code_repair/selection",
                        "      test: fixtures/code_repair/test",
                        "  data_normalization:",
                        "    skill: .codex/skills/data-normalization/SKILL.md",
                        "    evaluator_command:",
                        f"      - {sys.executable}",
                        "      - -m",
                        "      - pytest",
                        "      - -q",
                        "      - tests_visible",
                        "      - tests_hidden",
                        "    splits:",
                        "      train: fixtures/data_normalization/train",
                        "      selection: fixtures/data_normalization/selection",
                        "      test: fixtures/data_normalization/test",
                        "",
                    ]
                )
            )
            task_dir = root / "fixtures/code_repair/train/demo"
            _write_task(task_dir, "train-demo", body="def add(a, b):\n    return a + b\n")
            visible = task_dir / "tests_visible"
            hidden = task_dir / "tests_hidden"
            visible.mkdir()
            hidden.mkdir()
            (visible / "test_visible.py").write_text(
                "from calc import add\n\n\ndef test_visible():\n    assert add(2, 3) == 5\n"
            )
            (hidden / "test_hidden.py").write_text(
                "from calc import add\n\n\ndef test_hidden():\n    assert add(-2, 5) == 3\n"
            )
            workspace = root / "workspace"

            prepare_code = main(
                [
                    "--config",
                    str(config_path),
                    "prepare-task",
                    "--track",
                    "code_repair",
                    "--task",
                    "train-demo",
                    "--split",
                    "train",
                    "--output",
                    str(workspace),
                ]
            )

            self.assertEqual(prepare_code, 0)
            self.assertTrue((workspace / "tests_visible").is_dir())
            self.assertFalse((workspace / "tests_hidden").exists())

            stdout = StringIO()
            with redirect_stdout(stdout):
                grade_code = main(
                    [
                        "--config",
                        str(config_path),
                        "grade-task",
                        "--track",
                        "code_repair",
                        "--workspace",
                        str(workspace),
                    ]
                )

            self.assertEqual(grade_code, 0)
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["score"], 1.0)

    def test_loop_run_executes_full_manual_loop_and_updates_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n\n- Keep this rule.\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 0.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    {
                        "edits": [
                            {
                                "id": "add-contract-check",
                                "op": "add",
                                "target": "## Rules",
                                "position": "after",
                                "content": "- State the intended contract before editing.",
                                "score": 0.9,
                                "rationale": "Train repairs benefit from generalizing examples.",
                                "evidence": ["train-demo"],
                            }
                        ]
                    }
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0, 1.0])
            _write_score_records(candidate_records, [1.0, 1.0])
            experiment_dir = root / "runs/exp"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--edit-budget",
                        "1",
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "accept_new_best")
            self.assertEqual(
                result["steps"],
                ["baseline", "rollout", "reflect", "aggregate", "select", "update", "gate"],
            )
            self.assertEqual((experiment_dir / "initial-baseline.md").read_text(), initial_skill.read_text())
            current_best = (experiment_dir / "current-best.md").read_text()
            self.assertIn("- State the intended contract before editing.", current_best)
            self.assertEqual((experiment_dir / "best-skill.md").read_text(), current_best)
            parent_snapshot = experiment_dir / "loop-01/parent-skill.md"
            self.assertEqual(parent_snapshot.read_text(), initial_skill.read_text())
            self.assertTrue((experiment_dir / "loop-01/gate-decision.json").exists())
            self.assertTrue((experiment_dir / "loop-01/full-loop-manifest.json").exists())

    def test_loop_run_preserves_existing_initial_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            experiment_dir = root / "runs/exp"
            experiment_dir.mkdir(parents=True)
            (experiment_dir / "initial-baseline.md").write_text("# Original baseline\n")
            (experiment_dir / "current-best.md").write_text("# Current\n\n## Rules\n")
            (experiment_dir / "best-skill.md").write_text("# Best\n")
            new_initial = root / "new-initial.md"
            new_initial.write_text("# New initial should not overwrite\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    [
                        {
                            "id": "add-guidance",
                            "op": "add",
                            "target": "## Rules",
                            "position": "after",
                            "content": "- Keep changes tiny.",
                            "score": 0.8,
                        }
                    ]
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            best_records = root / "best-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])
            _write_score_records(best_records, [1.0])

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-02",
                        "--initial-skill",
                        str(new_initial),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--best-selection-records",
                        str(best_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "accept")
            self.assertEqual((experiment_dir / "initial-baseline.md").read_text(), "# Original baseline\n")
            self.assertIn("- Keep changes tiny.", (experiment_dir / "current-best.md").read_text())
            self.assertEqual((experiment_dir / "best-skill.md").read_text(), "# Best\n")

    def test_loop_run_records_reporting_only_test_comparison_without_gating(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            _write_add_rule_proposal(edit_proposals, "add-guidance", "- Keep changes tiny.")
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            baseline_test_records = root / "baseline-test.jsonl"
            candidate_test_records = root / "candidate-test.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])
            _write_score_records(baseline_test_records, [1.0, 1.0], task_ids=["test-a", "test-b"])
            _write_score_records(candidate_test_records, [0.0, 1.0], task_ids=["test-a", "test-b"])
            experiment_dir = root / "runs/exp"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--baseline-test-records",
                        str(baseline_test_records),
                        "--candidate-test-records",
                        str(candidate_test_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "accept_new_best")
            self.assertEqual(result["baseline_test_score"], 1.0)
            self.assertEqual(result["candidate_test_score"], 0.5)
            self.assertEqual(result["test_delta"], -0.5)
            decision = json.loads((experiment_dir / "loop-01/gate-decision.json").read_text())
            self.assertEqual(decision["baseline_test_score"], 1.0)
            self.assertEqual(decision["candidate_test_score"], 0.5)
            decision_text = (experiment_dir / "loop-01/decision.md").read_text()
            self.assertIn("Reporting-Only Test Comparison", decision_text)
            self.assertIn("must not affect the selection gate", decision_text)

    def test_loop_run_rejects_test_comparison_task_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            _write_add_rule_proposal(edit_proposals, "add-guidance", "- Keep changes tiny.")
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            baseline_test_records = root / "baseline-test.jsonl"
            candidate_test_records = root / "candidate-test.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])
            _write_score_records(baseline_test_records, [1.0], task_ids=["test-a"])
            _write_score_records(candidate_test_records, [1.0], task_ids=["test-b"])

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(root / "runs/exp"),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--baseline-test-records",
                        str(baseline_test_records),
                        "--candidate-test-records",
                        str(candidate_test_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("Baseline and candidate test tasks differ", stderr.getvalue())

    def test_loop_run_recovers_current_best_from_existing_initial_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            experiment_dir = root / "runs/exp"
            experiment_dir.mkdir(parents=True)
            (experiment_dir / "initial-baseline.md").write_text("# Original baseline\n\n## Rules\n")
            new_initial = root / "new-initial.md"
            new_initial.write_text("# New initial should not seed current best\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    [
                        {
                            "id": "add-guidance",
                            "op": "add",
                            "target": "## Rules",
                            "position": "after",
                            "content": "- Recover from the immutable baseline.",
                            "score": 0.8,
                        }
                    ]
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [1.0])
            _write_score_records(candidate_records, [1.0])

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(new_initial),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertEqual((experiment_dir / "current-best.md").read_text(), "# Original baseline\n\n## Rules\n")
            self.assertEqual((experiment_dir / "loop-01/parent-skill.md").read_text(), "# Original baseline\n\n## Rules\n")

    def test_loop_run_contaminated_run_rejects_without_updating_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 0.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    [
                        {
                            "id": "add-guidance",
                            "op": "add",
                            "target": "## Rules",
                            "position": "after",
                            "content": "- This should not be adopted.",
                            "score": 0.8,
                        }
                    ]
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])
            experiment_dir = root / "runs/exp"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--contaminated",
                        "--contamination-reason",
                        "parent selection verifier output was visible before candidate rollout",
                        "--rollout-isolation",
                        "redacted-in-session",
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "reject")
            self.assertEqual(result["leakage_status"], "contaminated")
            self.assertEqual((experiment_dir / "current-best.md").read_text(), initial_skill.read_text())
            decision = json.loads((experiment_dir / "loop-01/gate-decision.json").read_text())
            self.assertEqual(decision["reject_reason"], "contaminated")
            self.assertEqual(
                decision["contamination_reason"],
                "parent selection verifier output was visible before candidate rollout",
            )

    def test_loop_run_contaminated_run_requires_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 0.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    [
                        {
                            "id": "add-guidance",
                            "op": "add",
                            "target": "## Rules",
                            "position": "after",
                            "content": "- This should not be adopted.",
                            "score": 0.8,
                        }
                    ]
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(root / "runs/exp"),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--contaminated",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("--contamination-reason is required", stderr.getvalue())

    def test_loop_run_accepts_selection_records_already_in_loop_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            _write_add_rule_proposal(edit_proposals, "add-guidance", "- Keep changes tiny.")
            experiment_dir = root / "runs/exp"
            loop_dir = experiment_dir / "loop-01"
            loop_dir.mkdir(parents=True)
            parent_records = loop_dir / "parent-selection.jsonl"
            candidate_records = loop_dir / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "accept_new_best")

    def test_loop_run_rejects_selection_task_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            _write_add_rule_proposal(edit_proposals, "add-guidance", "- Keep changes tiny.")
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0], task_ids=["selection-a"])
            _write_score_records(candidate_records, [1.0], task_ids=["selection-b"])

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(root / "runs/exp"),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("Parent and candidate selection tasks differ", stderr.getvalue())

    def test_loop_run_rejects_improvement_with_unknown_rollout_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            _write_add_rule_proposal(edit_proposals, "add-guidance", "- Keep changes tiny.")
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])
            experiment_dir = root / "runs/exp"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "reject")
            self.assertEqual(result["reject_reason"], "unknown_rollout_isolation")
            self.assertEqual(
                json.loads((experiment_dir / "loop-01/gate-decision.json").read_text())[
                    "rollout_isolation"
                ],
                "unknown",
            )
            self.assertEqual((experiment_dir / "current-best.md").read_text(), initial_skill.read_text())

    def test_loop_run_fails_invalid_edit_target_count_before_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n\n- Repeat\n- Repeat\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    [
                        {
                            "id": "bad-target",
                            "op": "add",
                            "target": "- Repeat",
                            "position": "after",
                            "content": "- New guidance.",
                            "score": 1.0,
                        }
                    ]
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])
            experiment_dir = root / "runs/exp"

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("Failed to validate", stderr.getvalue())
            report = json.loads((experiment_dir / "loop-01/update-report.json").read_text())
            self.assertEqual(report["failed_count"], 1)
            self.assertIn("target matched 2 times", report["validation_errors"][0]["message"])
            self.assertEqual((experiment_dir / "current-best.md").read_text(), initial_skill.read_text())

    def test_loop_run_rejects_rules_section_edit_that_would_append_after_final_response(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n\n- Keep this rule.\n\n## Final Response\n")
            rollout_records = root / "train-rollouts.jsonl"
            rollout_records.write_text('{"task": {"id": "train-demo"}, "score": 1.0}\n')
            edit_proposals = root / "edit-proposals.json"
            edit_proposals.write_text(
                json.dumps(
                    [
                        {
                            "id": "bad-rules-append",
                            "op": "add",
                            "target": "",
                            "position": "end",
                            "section": "## Rules",
                            "content": "- This must not append after Final Response.",
                            "score": 1.0,
                        }
                    ]
                )
                + "\n"
            )
            parent_records = root / "parent-selection.jsonl"
            candidate_records = root / "candidate-selection.jsonl"
            _write_score_records(parent_records, [0.0])
            _write_score_records(candidate_records, [1.0])

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(root / "runs/exp"),
                        "--loop-id",
                        "loop-01",
                        "--initial-skill",
                        str(initial_skill),
                        "--rollout-records",
                        str(rollout_records),
                        "--edit-proposals",
                        str(edit_proposals),
                        "--parent-selection-records",
                        str(parent_records),
                        "--candidate-selection-records",
                        str(candidate_records),
                        "--rollout-isolation",
                        "independent",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("section edit cannot use position=end", stderr.getvalue())

    def test_loop_abort_writes_contaminated_reject_artifacts_without_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            experiment_dir = root / "runs/exp"

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "loop-abort",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--loop-id",
                        "loop-02",
                        "--initial-skill",
                        str(initial_skill),
                        "--contamination-reason",
                        "selection evidence was visible before candidate proposal",
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["decision"], "reject")
            self.assertEqual(result["leakage_status"], "contaminated")
            self.assertIsNone(result["candidate_skill"])
            self.assertEqual((experiment_dir / "current-best.md").read_text(), initial_skill.read_text())
            decision = json.loads((experiment_dir / "loop-02/gate-decision.json").read_text())
            self.assertEqual(decision["reject_reason"], "contaminated_before_candidate_proposal")

    def test_epoch_run_records_two_epoch_series_with_slow_and_meta_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n\n- Keep this rule.\n")
            experiment_dir = root / "runs/exp"

            epoch_inputs = []
            for index in (1, 2):
                epoch_dir = root / f"inputs/epoch-{index:02d}"
                epoch_dir.mkdir(parents=True)
                rollout_records = epoch_dir / "train-rollouts.jsonl"
                rollout_records.write_text(
                    json.dumps({"task": {"id": f"train-{index}"}, "score": 1.0}) + "\n"
                )
                edit_proposals = epoch_dir / "edit-proposals.json"
                _write_add_rule_proposal(
                    edit_proposals,
                    f"epoch-{index:02d}-guidance",
                    f"- Epoch {index} guidance.",
                )
                parent_records = epoch_dir / "parent-selection.jsonl"
                candidate_records = epoch_dir / "candidate-selection.jsonl"
                _write_score_records(parent_records, [0.0 if index == 1 else 1.0])
                _write_score_records(candidate_records, [1.0])
                slow_update = epoch_dir / "slow-update.md"
                slow_update.write_text(f"# Slow update {index}\n")
                meta_skill = epoch_dir / "meta-skill.md"
                meta_skill.write_text(f"# Meta skill {index}\n")
                epoch_inputs.append(
                    {
                        "epoch_id": f"epoch-{index:02d}",
                        "rollout_records": [str(rollout_records)],
                        "edit_proposals": str(edit_proposals),
                        "parent_selection_records": str(parent_records),
                        "candidate_selection_records": str(candidate_records),
                        "slow_update": str(slow_update),
                        "meta_skill": str(meta_skill),
                        "rollout_isolation": "independent",
                    }
                )
            epoch_inputs_path = root / "epoch-inputs.json"
            epoch_inputs_path.write_text(json.dumps({"epochs": epoch_inputs}) + "\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "epoch-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(experiment_dir),
                        "--initial-skill",
                        str(initial_skill),
                        "--epoch-inputs",
                        str(epoch_inputs_path),
                    ]
                )

            self.assertEqual(code, 0)
            result = json.loads(stdout.getvalue())
            self.assertEqual(result["epoch_count"], 2)
            self.assertEqual([epoch["epoch_id"] for epoch in result["epochs"]], ["epoch-01", "epoch-02"])
            self.assertEqual(result["epochs"][0]["decision"], "accept_new_best")
            self.assertEqual(result["epochs"][1]["decision"], "reject")
            current_best = (experiment_dir / "current-best.md").read_text()
            self.assertIn("- Epoch 1 guidance.", current_best)
            self.assertNotIn("- Epoch 2 guidance.", current_best)
            self.assertEqual(
                (experiment_dir / "epoch-02/parent-skill.md").read_text(),
                current_best,
            )
            self.assertEqual(
                (experiment_dir / "epoch-01/slow-update.md").read_text(),
                "# Slow update 1\n",
            )
            self.assertEqual(
                (experiment_dir / "epoch-02/meta-skill.md").read_text(),
                "# Meta skill 2\n",
            )
            self.assertTrue((experiment_dir / "multi-epoch-manifest.json").exists())

    def test_epoch_run_requires_two_to_four_epochs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = _write_config(root)
            initial_skill = root / "initial-skill.md"
            initial_skill.write_text("# Skill\n\n## Rules\n")
            epoch_inputs_path = root / "epoch-inputs.json"
            epoch_inputs_path.write_text(json.dumps({"epochs": []}) + "\n")

            stderr = StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "--config",
                        str(config_path),
                        "epoch-run",
                        "--track",
                        "code_repair",
                        "--experiment-dir",
                        str(root / "runs/exp"),
                        "--initial-skill",
                        str(initial_skill),
                        "--epoch-inputs",
                        str(epoch_inputs_path),
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("between 2 and 4 epochs", stderr.getvalue())


def _write_config(root: Path) -> Path:
    config_path = root / "skillopt.yaml"
    config_path.write_text(
        "\n".join(
            [
                "timeout_seconds: 30",
                "output_dir: runs",
                "tracks:",
                "  code_repair:",
                "    skill: .codex/skills/code-repair/SKILL.md",
                "    evaluator_command:",
                f"      - {sys.executable}",
                "      - -c",
                (
                    "      - from calc import add; "
                    "raise SystemExit(0 if add(2, 3) == 5 else 1)"
                ),
                "    splits:",
                "      train: fixtures/code_repair/train",
                "      selection: fixtures/code_repair/selection",
                "      test: fixtures/code_repair/test",
                "  data_normalization:",
                "    skill: .codex/skills/data-normalization/SKILL.md",
                "    evaluator_command:",
                f"      - {sys.executable}",
                "      - -m",
                "      - pytest",
                "      - -q",
                "      - tests_visible",
                "      - tests_hidden",
                "    splits:",
                "      train: fixtures/data_normalization/train",
                "      selection: fixtures/data_normalization/selection",
                "      test: fixtures/data_normalization/test",
                "",
            ]
        )
    )
    return config_path


def _write_task(
    path: Path,
    task_id: str,
    body: str = "def add(a, b):\n    return a - b\n",
) -> None:
    path.mkdir(parents=True)
    (path / "task.json").write_text(
        json.dumps({"id": task_id, "description": "repair add", "entrypoint": "calc.py"}) + "\n"
    )
    (path / "calc.py").write_text(body)


def _write_data_task(
    path: Path,
    task_id: str,
    body: str = "def normalize_names(names):\n    return names\n",
) -> None:
    path.mkdir(parents=True)
    (path / "task.json").write_text(
        json.dumps(
            {
                "id": task_id,
                "description": "normalize names",
                "entrypoint": "names.py",
            }
        )
        + "\n"
    )
    (path / "names.py").write_text(body)
    visible = path / "tests_visible"
    hidden = path / "tests_hidden"
    visible.mkdir()
    hidden.mkdir()
    (visible / "test_names_visible.py").write_text(
        "from names import normalize_names\n\n\n"
        "def test_visible_names():\n"
        "    assert normalize_names([' ada ']) == ['Ada']\n"
    )
    (hidden / "test_names_hidden.py").write_text(
        "from names import normalize_names\n\n\n"
        "def test_hidden_names():\n"
        "    assert normalize_names([' grace hopper ']) == ['Grace Hopper']\n"
    )


def _write_score_records(
    path: Path,
    scores: list[float],
    task_ids: list[str] | None = None,
) -> None:
    if task_ids is None:
        task_ids = [str(index) for index in range(len(scores))]
    if len(task_ids) != len(scores):
        raise ValueError("task_ids length must match scores length")
    path.write_text(
        "".join(
            json.dumps({"score": score, "task": {"id": task_id}}) + "\n"
            for task_id, score in zip(task_ids, scores, strict=True)
        )
    )


def _write_add_rule_proposal(path: Path, edit_id: str, content: str) -> None:
    path.write_text(
        json.dumps(
            {
                "edits": [
                    {
                        "id": edit_id,
                        "op": "add",
                        "target": "## Rules",
                        "position": "after",
                        "content": content,
                        "score": 0.8,
                    }
                ]
            }
        )
        + "\n"
    )


if __name__ == "__main__":
    unittest.main()
