from __future__ import annotations

import unittest
from pathlib import Path

from skillopt_harness.state import load_tasks


class FixtureInventoryTests(unittest.TestCase):
    def test_mvp_weak_baselines_exist(self) -> None:
        for path in (
            Path("examples/baselines/code-repair-weak-baseline.md"),
            Path("examples/baselines/data-normalization-weak-baseline.md"),
        ):
            with self.subTest(path=path):
                self.assertTrue(path.is_file())
                self.assertIn("Baseline", path.read_text())

    def test_each_track_split_has_at_least_five_tasks(self) -> None:
        for track in ("code_repair", "data_normalization"):
            for split in ("train", "selection", "test"):
                with self.subTest(track=track, split=split):
                    tasks = load_tasks(Path("fixtures") / track / split)
                    self.assertGreaterEqual(len(tasks), 5)

    def test_pytest_tracks_have_visible_and_hidden_tests(self) -> None:
        for track in ("code_repair", "data_normalization"):
            for split in ("train", "selection", "test"):
                for task in load_tasks(Path("fixtures") / track / split):
                    with self.subTest(track=track, task=task.id):
                        self.assertTrue((task.path / "tests_visible").is_dir())
                        self.assertTrue((task.path / "tests_hidden").is_dir())
                        self.assertTrue(list((task.path / "tests_visible").glob("test_*.py")))
                        self.assertTrue(list((task.path / "tests_hidden").glob("test_*.py")))


if __name__ == "__main__":
    unittest.main()
