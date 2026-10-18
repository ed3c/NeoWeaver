"""Native OpenEnv dependency smoke, not a model rollout or independent Oracle."""
import unittest

from neoweaver.viewenv_openenv import make_environment_class
from test_viewenv import fixture


class NativeOpenEnvSmoke(unittest.TestCase):
    def test_real_openenv_environment_and_reset(self):
        from openenv.core.env_server.mcp_environment import MCPEnvironment
        spec, _ = fixture()
        env_class = make_environment_class(spec)
        self.assertTrue(issubclass(env_class, MCPEnvironment))
        env = env_class()
        first = env.reset(episode_id="ep-1")
        self.assertFalse(first.done)
        self.assertIsNone(first.reward)
        self.assertEqual("unknown", first.metadata["reward_status"])
        self.assertEqual("READY", env.domain.inspect().status)
        self.assertIsNone(env.state["reward"])
        with self.assertRaises(ValueError):
            env.reset(episode_id="foreign-episode")
        with self.assertRaisesRegex(ValueError,"already_consumed"):
            env.reset(episode_id="ep-1")

if __name__ == "__main__":
    unittest.main()
