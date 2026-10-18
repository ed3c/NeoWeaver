"""Native OpenEnv dependency smoke, not a model rollout or independent Oracle."""
import unittest
import importlib.util

from neoweaver.viewenv_openenv import make_environment_class
from test_viewenv import fixture


class NativeOpenEnvSmoke(unittest.TestCase):
    def test_real_openenv_environment_and_reset(self):
        if importlib.util.find_spec("openenv") is None:
            self.skipTest("optional native OpenEnv SDK is not installed in this workflow")
        from openenv.core.env_server.mcp_environment import MCPEnvironment
        spec, proposal = fixture()
        env_class = make_environment_class(spec)
        self.assertTrue(issubclass(env_class, MCPEnvironment))
        env = env_class()
        first = env.reset(episode_id="ep-1")
        self.assertFalse(first.done)
        self.assertIsNone(first.reward)
        self.assertEqual("unknown", first.metadata["reward_status"])
        self.assertEqual("READY", env.domain.inspect().status)
        self.assertIsNone(env.state["reward"])
        from openenv.core.env_server.mcp_types import CallToolAction
        original = env.step(CallToolAction(
            tool_name="propose_patch", arguments={"proposal_json": proposal.decode()}))
        self.assertFalse(original.done)
        self.assertIsNone(original.reward)
        self.assertEqual("PROPOSED", env.domain.inspect().status)
        terminated = env.step(CallToolAction(tool_name="terminate", arguments={}))
        self.assertTrue(terminated.done)
        self.assertIsNone(terminated.reward)
        with self.assertRaises(ValueError):
            env.reset(episode_id="foreign-episode")
        with self.assertRaisesRegex(ValueError,"already_consumed"):
            env.reset(episode_id="ep-1")

if __name__ == "__main__":
    unittest.main()
