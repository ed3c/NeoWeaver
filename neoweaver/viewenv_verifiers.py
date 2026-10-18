"""Verifiers wrapper for the *same* NeoWeaver ViewEnv domain.

No fabricated `0.0` reward: a real independent rubric and dataset are
required to construct a Trainer-facing ToolEnv. The frozen Codex executor is
never used as a policy-gradient actor.
"""
from .viewenv import EpisodeSpec, ViewEnvEpisode


class ViewEnvToolkit:
    def __init__(self, spec: EpisodeSpec):
        self.spec = spec
        self.domain = None
        self._ever_reset = False

    def reset(self):
        if self._ever_reset:
            raise ValueError('episode_identity_reuse_refused')
        self._ever_reset = True
        self.domain = ViewEnvEpisode(self.spec)

    def propose_patch(self, proposal_json: str) -> str:
        """Submit a bounded candidate; original parser alone can admit its shape."""
        if self.domain is None:
            raise ValueError("episode_reset_required")
        obs = self.domain.propose_patch(proposal_json.encode("utf-8"))
        return obs.status if obs.proposal_condition is None else (
            obs.status + ":" + obs.proposal_condition)

    def inspect(self) -> str:
        """Inspect domain state. The result is not an evaluation verdict."""
        if self.domain is None:
            raise ValueError("episode_reset_required")
        return self.domain.inspect().phase

    def terminate(self) -> str:
        """Close the current episode without claiming a training reward."""
        if self.domain is None:
            raise ValueError("episode_reset_required")
        return self.domain.terminate().status

    @property
    def reward(self):
        return None

    def cleanup(self):
        self.domain = None


def make_tool_env(spec: EpisodeSpec, dataset, independent_rubric):
    """Use the real vf.ToolEnv, never a stand-in grader.

    Caller owns dataset rights and immutable independent rubric. No default
    scorer or hidden test answer is embedded in a model-visible tool.
    """
    if dataset is None or independent_rubric is None:
        raise ValueError("independent_dataset_and_rubric_required")
    import verifiers as vf
    toolkit = ViewEnvToolkit(spec)
    toolkit.reset()

    def propose_patch(proposal_json: str) -> str:
        return toolkit.propose_patch(proposal_json)

    def inspect() -> str:
        return toolkit.inspect()

    def terminate() -> str:
        return toolkit.terminate()

    env = vf.ToolEnv(
        tools=[propose_patch, inspect, terminate],
        rubric=independent_rubric,
        dataset=dataset,
        max_turns=spec.max_actions,
        system_prompt="Propose one bounded change; results require external verification.",
    )
    return env, toolkit
