import json
import unittest

from neoweaver.patches import KIND, OwnerRef
from neoweaver.viewenv import EpisodeSpec, ViewEnvEpisode, ViewEnvRefusal
from neoweaver.viewenv_verifiers import ViewEnvToolkit, make_tool_env


def owner(x):
    return {"producer": "owner", "reference": x}


def fixture():
    fixed = {
        "snapshot_ref": owner("snapshot"), "failure_ref": owner("failure"),
        "allowlist_ref": owner("allowlist"), "acceptance_ref": owner("acceptance"),
        "causal_target_ref": owner("skill"), "protected_target_refs": [owner("oracle")],
        "allowlist": [{"surface":"skill_instruction",
                       "target_ref":owner("skill"),
                       "expected_source_ref":owner("source")}],
    }
    proposal = {
        "kind":KIND,
        **{k:fixed[k] for k in
           ("snapshot_ref","failure_ref","allowlist_ref","acceptance_ref")},
        "surface":"skill_instruction",
        "changes":[{"target_ref":owner("skill"),
                    "expected_source_ref":owner("source"),
                    "replacement":"Scoped candidate"}],
    }
    spec = EpisodeSpec(OwnerRef("owner", "ep-1"), OwnerRef("owner", "task"),
                       OwnerRef("owner", "environment"), fixed)
    return spec, json.dumps(proposal).encode()


class ViewEnvDomainTests(unittest.TestCase):
    def test_owner_bound_episode_and_candidate(self):
        spec, raw = fixture()
        env = ViewEnvEpisode(spec)
        self.assertIsNone(env.inspect().reward)
        self.assertEqual("READY", env.inspect().status)
        self.assertEqual("PROPOSED", env.propose_patch(raw).status)
        self.assertEqual("awaiting_original_probe", env.inspect().phase)
        self.assertEqual("NOT_RUN", env.inspect().pair_status)
        self.assertEqual("TERMINATED", env.terminate().status)
        self.assertFalse(env.inspect().authorizes_training)

    def test_proposal_refusal_and_invalid_original_refs(self):
        spec, raw = fixture()
        env = ViewEnvEpisode(spec)
        proposal = json.loads(raw)
        proposal["changes"][0]["target_ref"] = owner("oracle")
        observation = env.propose_patch(json.dumps(proposal).encode())
        self.assertEqual("REFUSED", observation.status)
        self.assertEqual("protected_target", observation.proposal_condition)
        with self.assertRaises(ViewEnvRefusal):
            ViewEnvEpisode(EpisodeSpec(OwnerRef("",""), spec.task_ref,
                                          spec.environment_ref,spec.fixed_inputs))
        self.assertIsNone(env.inspect().reward)

    def test_reject_duplicate_or_foreign_pair(self):
        spec, raw = fixture()
        env = ViewEnvEpisode(spec)
        env.propose_patch(raw)
        with self.assertRaisesRegex(ViewEnvRefusal, "foreign_pair_type"):
            env.attach_native_pair({"pair": {"status":"PASS"}})
        with self.assertRaisesRegex(ViewEnvRefusal, "episode_not_admitting"):
            env.propose_patch(raw)

    def test_verifiers_toolkit_no_fake_reward_or_default_oracle(self):
        spec, raw = fixture()
        toolkit = ViewEnvToolkit(spec)
        with self.assertRaisesRegex(ValueError,"episode_reset_required"):
            toolkit.inspect()
        toolkit.reset()
        self.assertEqual("PROPOSED", toolkit.propose_patch(raw.decode()))
        self.assertIsNone(toolkit.reward)
        toolkit.cleanup()
        with self.assertRaises(ValueError):
            make_tool_env(spec, None, None)


if __name__ == "__main__":
    unittest.main()
