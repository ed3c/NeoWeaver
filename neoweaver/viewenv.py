"""ViewEnv domain: bounded Proposal action, original readback, no owned effects.

This is a single-episode, per-instance *design* environment.  It never launches
Codex, chooses or runs the Oracle, creates a reward, or grants authorization.
Framework adapters wrap these same transitions instead of reimplementing them.
"""
from dataclasses import dataclass
from typing import Literal

from .patches import (
    DiagnosticRefusal, FixedInputs, OwnerRef, ParsedProposal, parse_proposal,
)
from .native import NativePairReport


class ViewEnvRefusal(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class EpisodeSpec:
    episode_ref: OwnerRef
    task_ref: OwnerRef
    environment_ref: OwnerRef
    fixed_inputs: dict
    max_actions: int = 2  # one candidate submission and one terminal acknowledgement


@dataclass(frozen=True, slots=True)
class StepObservation:
    status: str
    phase: str
    done: bool
    reward: None
    proposal_condition: str | None
    pair_status: str
    action_count: int
    authorizes_training: bool = False
    authorizes_landing: bool = False


def _owner_ref(ref):
    return (type(ref) is OwnerRef and type(ref.producer) is str
            and bool(ref.producer.strip()) and type(ref.reference) is str
            and bool(ref.reference.strip()))


class ViewEnvEpisode:
    """Reset once from owner-fixed input; tools can submit proposal but never Probe."""

    def __init__(self, spec: EpisodeSpec):
        if type(spec) is not EpisodeSpec or not all(_owner_ref(x) for x in
                (spec.episode_ref, spec.task_ref, spec.environment_ref)):
            raise ViewEnvRefusal("invalid_original_owner_identity")
        if type(spec.max_actions) is not int or not 2 <= spec.max_actions <= 8:
            raise ViewEnvRefusal("invalid_episode_action_limit")
        # No invented reference or generated environment ID. This validates the
        # fixed inputs with the original parser on the actual candidate action.
        if type(spec.fixed_inputs) is not dict:
            raise ViewEnvRefusal("invalid_fixed_inputs")
        self.spec = spec
        self._phase = "ready"
        self._actions = 0
        self._candidate: ParsedProposal | None = None
        self._pair: NativePairReport | None = None
        self._diagnostic: str | None = None
        self._done = False

    def observation(self):
        return StepObservation(
            "TERMINATED" if self._done else "PROPOSED" if self._candidate else
            "REFUSED" if self._diagnostic else "READY",
            self._phase, self._done, None, self._diagnostic,
            self._pair.pair.status if self._pair is not None else "NOT_RUN",
            self._actions,
        )

    def propose_patch(self, raw: bytes):
        if self._done or self._candidate is not None or self._actions >= self.spec.max_actions:
            raise ViewEnvRefusal("episode_not_admitting_proposals")
        self._actions += 1
        proposal = parse_proposal(raw, self.spec.fixed_inputs)
        if type(proposal) is DiagnosticRefusal:
            self._diagnostic = proposal.condition
            return self.observation()
        if type(proposal) is not ParsedProposal:
            raise ViewEnvRefusal("unsupported_native_parser_result")
        self._candidate = proposal
        self._diagnostic = None
        self._phase = "awaiting_original_probe"
        return self.observation()

    def inspect(self):
        return self.observation()

    def attach_native_pair(self, pair: NativePairReport):
        """Original owner calls this with an existing, independently inspected pair.

        It does not execute the native capture or classify an unknown effect
        as observed. Self-reported, fixture or foreign result cannot grant reward.
        """
        if self._done or self._candidate is None or self._pair is not None:
            raise ViewEnvRefusal("no_current_candidate_or_pair_already_bound")
        if type(pair) is not NativePairReport:
            raise ViewEnvRefusal("foreign_pair_type")
        if pair.oracle_results[0].capture.conditions.snapshot_ref != self._candidate.snapshot_ref or (
            pair.oracle_results[1].capture.conditions.snapshot_ref != self._candidate.snapshot_ref):
            raise ViewEnvRefusal("foreign_snapshot_pair")
        if pair.authorizes_training or pair.authorizes_landing:
            raise ViewEnvRefusal("unexpected_authority_claim")
        self._pair = pair
        self._phase = "native_pair_reviewed"
        return self.observation()

    def terminate(self):
        if self._done:
            raise ViewEnvRefusal("duplicate_termination")
        if self._actions >= self.spec.max_actions:
            raise ViewEnvRefusal("episode_action_limit")
        self._actions += 1
        self._done = True
        self._phase = "terminated"
        return self.observation()
