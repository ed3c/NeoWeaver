"""OpenEnv native MCP adapter to ViewEnvEpisode. Optional dependency.

Supply the original owner-fixed EpisodeSpec to the selected private environment
factory. Never publish this callable with private FixedInputs to a public route.
The adapter is a real OpenEnv MCPEnvironment subclass when OpenEnv is installed;
there is no local replacement of OpenEnv transport/tool routing.
"""
import json

from .viewenv import EpisodeSpec, ViewEnvEpisode


def make_environment_class(spec: EpisodeSpec):
    from fastmcp import FastMCP
    from openenv.core.env_server.mcp_environment import MCPEnvironment
    from openenv.core.env_server.types import Action, Observation

    class ViewEnvMCP(MCPEnvironment):
        SUPPORTS_CONCURRENT_SESSIONS = True

        def __init__(self):
            self.domain = ViewEnvEpisode(spec)
            mcp = FastMCP("viewenv")

            @mcp.tool
            def propose_patch(proposal_json: str) -> str:
                """Propose a single bounded Harness change; no execution or reward."""
                observation = self.domain.propose_patch(proposal_json.encode("utf-8"))
                return json.dumps({
                    "status": observation.status,
                    "condition": observation.proposal_condition,
                    "pair_status": observation.pair_status,
                    "reward": None, "authorizes_training": False,
                }, sort_keys=True)

            @mcp.tool
            def inspect_proposal() -> str:
                """Read the current source-bound admission state, without probing."""
                observation = self.domain.inspect()
                return json.dumps({
                    "status": observation.status,
                    "phase": observation.phase,
                    "pair_status": observation.pair_status,
                    "reward": None,
                }, sort_keys=True)

            @mcp.tool
            def terminate() -> str:
                """Finish one episode. Independent verifier and original Owner retain reward."""
                observation = self.domain.terminate()
                return json.dumps({"status": observation.status, "done": True,
                                   "reward": None}, sort_keys=True)

            super().__init__(mcp)

        def reset(self, seed=None, episode_id=None, **kwargs):
            # Each factory instance is one pinned episode. Never silently
            # substitute a new caller-controlled episode or silently reuse state.
            if episode_id is not None and episode_id != spec.episode_ref.reference:
                raise ValueError("foreign_episode_identity")
            self.domain = ViewEnvEpisode(spec)
            return Observation(done=False, reward=None, metadata={
                "status": "READY", "episode_ref": spec.episode_ref.reference,
                "reward_status": "unknown",
            })

        def _step_impl(self, action: Action, timeout_s=None, **kwargs):
            return Observation(done=False, reward=None, metadata={
                "status": "REFUSED", "reason": "unsupported_action",
            })

        def step(self, action: Action, timeout_s=None, **kwargs):
            return self._with_status(super().step(action, timeout_s=timeout_s, **kwargs))

        async def step_async(self, action: Action, timeout_s=None, **kwargs):
            return self._with_status(await super().step_async(action, timeout_s=timeout_s, **kwargs))

        def _with_status(self, observation: Observation):
            current = self.domain.inspect()
            observation.done = current.done
            # OpenEnv must not infer a numeric reward from success/failure.
            observation.reward = None
            observation.metadata = {
                **(observation.metadata or {}),
                "viewenv_status": current.status,
                "pair_status": current.pair_status,
                "reward_status": "unknown",
            }
            return observation

        @property
        def state(self):
            current = self.domain.inspect()
            return {
                "episode_id": spec.episode_ref.reference,
                "step_count": current.action_count,
                "phase": current.phase,
                "done": current.done,
                "reward": None,
            }

    return ViewEnvMCP


def make_private_app(spec: EpisodeSpec):
    """Use only under existing authenticated private Host admission."""
    from openenv.core.env_server.http_server import create_app
    from openenv.core.env_server.mcp_types import CallToolAction, CallToolObservation
    return create_app(make_environment_class(spec), CallToolAction, CallToolObservation,
                      env_name="viewenv", max_concurrent_envs=1)
