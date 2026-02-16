import unittest

from yagnidrift.drift import compute_yagni_drift
from yagnidrift.git_tools import WorkingChanges
from yagnidrift.specs import YagnidriftSpec


class TestYagniDrift(unittest.TestCase):
    def test_green(self) -> None:
        spec = YagnidriftSpec.from_raw({"schema": 1, "max_new_files": 5, "max_new_dirs": 2})
        changes = WorkingChanges(changed_files=["src/app.py"], new_files=[])
        report = compute_yagni_drift(
            task_id="t1",
            task_title="Task",
            description="",
            spec=spec,
            git_root="/tmp/x",
            changes=changes,
        )
        self.assertEqual("green", report["score"])
        self.assertEqual([], report["findings"])

    def test_flags_complexity_creep(self) -> None:
        spec = YagnidriftSpec.from_raw({"schema": 1, "max_new_files": 1, "max_new_dirs": 0})
        changes = WorkingChanges(
            changed_files=[
                "src/factories/payment_factory.py",
                "src/adapters/http_adapter.py",
            ],
            new_files=[
                "src/factories/payment_factory.py",
                "src/adapters/http_adapter.py",
            ],
        )
        report = compute_yagni_drift(
            task_id="t1",
            task_title="Task",
            description="",
            spec=spec,
            git_root="/tmp/x",
            changes=changes,
        )
        kinds = {f["kind"] for f in report["findings"]}
        self.assertIn("too_many_new_files", kinds)
        self.assertIn("too_many_new_dirs", kinds)
        self.assertIn("speculative_abstraction", kinds)
        self.assertEqual("yellow", report["score"])


if __name__ == "__main__":
    unittest.main()
