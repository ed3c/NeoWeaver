"""A6: one direct, non-authorizing training decision screen.

Consume supplied task/evaluation facts, not FileRefs or reconstructed Provider
identities. A claimed PASS is NOT an independently observed training receipt.
No model invocation, training update, rights adjudication, or provider effects.
"""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrainingCandidate:
    actor: str                  # proposer / open_solver / frozen_codex
    method: str                 # sft / policy_gradient
    partition: str              # train / validation / held_out / unknown
    rights: str                 # allowed / denied / unknown
    acceptance: str             # pass / fail / unknown
    protected_regressions: str  # pass / fail / unknown
    effect_status: str          # none_observed / unknown
    lineage: str                # matched / mismatched / unknown
    token_provenance: str       # available / missing / unknown
    replay: str                 # observed / failed / unknown
    verifier: str               # independent / self / unknown
    reward: str                 # observed / unknown


@dataclass(frozen=True, slots=True)
class EligibilityInspection:
    status: str  # REFUSED / BLOCKED / INCONCLUSIVE / STRUCTURALLY_ELIGIBLE
    reasons: tuple[str, ...]
    evidence_ceiling: str = "SUPPLIED_FACTS_ONLY"
    eligible_for_training: bool = False
    authorizes_landing: bool = False


_ALLOWED = {
    "actor": ("proposer", "open_solver", "frozen_codex"),
    "method": ("sft", "policy_gradient"),
    "partition": ("train", "validation", "held_out", "unknown"),
    "rights": ("allowed", "denied", "unknown"),
    "acceptance": ("pass", "fail", "unknown"),
    "protected_regressions": ("pass", "fail", "unknown"),
    "effect_status": ("none_observed", "unknown"),
    "lineage": ("matched", "mismatched", "unknown"),
    "token_provenance": ("available", "missing", "unknown"),
    "replay": ("observed", "failed", "unknown"),
    "verifier": ("independent", "self", "unknown"),
    "reward": ("observed", "unknown"),
}


def inspect_training_candidate(candidate: TrainingCandidate) -> EligibilityInspection:
    """Return one typed decision; never request a separate FileRef/auth route.

    Actual Dataset/Runner/Verifier/Trainer owners remain responsible for source
    facts and effects when a real training run exists. The screening output
    never grants permission or implies that its supplied facts were verified.
    """
    if type(candidate) is not TrainingCandidate:
        return EligibilityInspection("REFUSED", ("invalid_candidate_type",))
    for field, choices in _ALLOWED.items():
        value = getattr(candidate, field)
        if type(value) is not str or value not in choices:
            return EligibilityInspection("REFUSED", ("invalid_" + field,))

    blocked = []
    if candidate.actor == "frozen_codex":
        blocked.append("frozen_codex_not_trainable")
    if candidate.partition in ("validation", "held_out"):
        blocked.append("non_training_partition")
    if candidate.rights == "denied":
        blocked.append("rights_denied")
    if candidate.acceptance == "fail":
        blocked.append("acceptance_failed")
    if candidate.protected_regressions == "fail":
        blocked.append("protected_regression_failed")
    if candidate.lineage == "mismatched":
        blocked.append("lineage_mismatch")
    if candidate.verifier == "self":
        blocked.append("self_reported_verifier")
    if candidate.replay == "failed":
        blocked.append("replay_failed")
    if blocked:
        return EligibilityInspection("BLOCKED", tuple(blocked))

    unknown = []
    for field in ("partition", "rights", "acceptance", "protected_regressions",
                  "effect_status", "lineage", "replay", "verifier", "reward"):
        if getattr(candidate, field) == "unknown":
            unknown.append(field + "_unknown")
    if candidate.token_provenance != "available" and (
            candidate.method == "policy_gradient" or candidate.actor == "open_solver"):
        unknown.append("token_provenance_unavailable")
    if unknown:
        return EligibilityInspection("INCONCLUSIVE", tuple(unknown))
    return EligibilityInspection("STRUCTURALLY_ELIGIBLE", ())
