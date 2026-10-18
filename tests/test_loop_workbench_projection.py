import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wb", ROOT / "scripts/loop_workbench_projection.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)


def sample():
    return {
        "run_ref":"run", "episode_ref":"ep","task_ref":"task",
        "environment_ref":"env","actor_ref":"owner",
        "harness":{"phase":"probe","baseline_ref":"h0","candidate_ref":"h1"},
        "actions":["action-1"],"observations":["readback-1"],
        "verification":{"status":"INCONCLUSIVE","verifier_ref":None},
        "reward":{"status":"unknown","value":None,"source_ref":None},
        "termination":{"status":"unknown","reason_ref":None}
    }


class EpisodeProjectionTests(unittest.TestCase):
    def test_unknown_stays_unknown(self):
        projected = wb.project_episode(sample())
        self.assertIsNone(projected["reward"]["value"])
        self.assertEqual("INCONCLUSIVE", projected["verification"]["status"])
        self.assertEqual(["readback-1"], projected["observations"])

    def test_refuse_reward_claim_without_verifier(self):
        src = sample()
        src["reward"] = {"status":"observed","value":1,"source_ref":"reward"}
        with self.assertRaisesRegex(wb.ProjectionRefusal, "independent evidence"):
            wb.project_episode(src)

    def test_scoped_negative_original_failure_is_not_success(self):
        src = sample()
        src["verification"] = {"status":"FAIL","verifier_ref":"gate"}
        src["reward"] = {"status":"observed","value":-1.0,"source_ref":"reward"}
        output = wb.project_episode(src)
        self.assertEqual("FAIL", output["verification"]["status"])
        self.assertEqual(-1, output["reward"]["value"])

    def test_refuse_missing_source_and_synthetic_zero(self):
        src = sample()
        src["environment_ref"] = ""
        with self.assertRaises(wb.ProjectionRefusal):
            wb.project_episode(src)
        src = sample()
        src["reward"]["value"] = 0
        with self.assertRaises(wb.ProjectionRefusal):
            wb.project_episode(src)

    def test_refuse_nonfinite_reward(self):
        src = sample()
        src["verification"] = {"status":"PASS","verifier_ref":"actual-review"}
        src["reward"] = {"status":"observed","value":float("nan"),"source_ref":"reward"}
        with self.assertRaises(wb.ProjectionRefusal):
            wb.project_episode(src)


if __name__ == "__main__":
    unittest.main()
