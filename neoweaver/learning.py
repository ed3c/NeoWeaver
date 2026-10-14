"""A6: pure eligibility screening on declarations from original evidence owners.

No model invocation, gradient update, rights adjudication or reward inference.
A matching declaration is only a candidate for independent source verification.
"""
from dataclasses import dataclass

from .patches import OwnerRef


@dataclass(frozen=True, slots=True)
class GenerationEvidence:
    actor: str  # proposer / open_solver / frozen_codex
    policy_ref: OwnerRef | None
    observation_ref: OwnerRef | None
    action_ref: OwnerRef | None
    generation_ref: OwnerRef | None
    token_ref: OwnerRef | None


@dataclass(frozen=True, slots=True)
class EvaluationEvidence:
    observation_ref: OwnerRef | None
    action_ref: OwnerRef | None
    rollout_ref: OwnerRef | None
    replay_ref: OwnerRef | None
    verifier_ref: OwnerRef | None
    oracle_ref: OwnerRef | None
    reward_ref: OwnerRef | None
    acceptance: str  # pass / fail / unknown
    protected_regressions: str  # pass / fail / unknown
    effect_status: str  # none_observed / unknown


@dataclass(frozen=True, slots=True)
class TrainingCandidate:
    generation: GenerationEvidence
    evaluation: EvaluationEvidence
    partition: str  # train / validation / held_out / unknown
    rights: str  # allowed / denied / unknown
    method: str  # sft / policy_gradient
    rights_ref: OwnerRef | None  # actual Dataset/Rights Owner evidence
    partition_ref: OwnerRef | None  # actual Dataset split provenance


@dataclass(frozen=True, slots=True)
class EligibilityInspection:
    status: str  # REFUSED / BLOCKED / INCONCLUSIVE / STRUCTURALLY_ELIGIBLE
    reasons: tuple[str, ...]
    evidence_ceiling: str = "DECLARED_EVIDENCE_RELATIONS_ONLY"
    eligible_for_training: bool = False
    authorizes_landing: bool = False


def _ref_ok(value):
    return (type(value) is OwnerRef and type(value.producer) is str
            and bool(value.producer.strip()) and type(value.reference) is str
            and bool(value.reference.strip()))


def inspect_training_candidate(candidate: TrainingCandidate) -> EligibilityInspection:
    """Screen declaration shape, hard refusals and absent source evidence.

    The original Dataset/Verifier/Trainer Owners must prove actual lineage,
    immutable oracle, rights and execution before any TrainingBatch update.
    """
    if type(candidate) is not TrainingCandidate or (type(candidate.generation) is not GenerationEvidence
                                                    or type(candidate.evaluation) is not EvaluationEvidence):
        return EligibilityInspection("REFUSED", ("invalid_candidate_type",))
    generation, evaluation = candidate.generation, candidate.evaluation
    allowed = {
        "actor": (generation.actor, ("proposer", "open_solver", "frozen_codex")),
        "method": (candidate.method, ("sft", "policy_gradient")),
        "partition": (candidate.partition, ("train", "validation", "held_out", "unknown")),
        "rights": (candidate.rights, ("allowed", "denied", "unknown")),
        "acceptance": (evaluation.acceptance, ("pass", "fail", "unknown")),
        "protected_regressions": (evaluation.protected_regressions, ("pass", "fail", "unknown")),
        "effect_status": (evaluation.effect_status, ("none_observed", "unknown")),
    }
    for field, (value, possibilities) in allowed.items():
        if type(value) is not str or value not in possibilities:
            return EligibilityInspection("REFUSED", ("invalid_" + field,))
    refs = {"candidate.rights_ref": candidate.rights_ref,
            "candidate.partition_ref": candidate.partition_ref}
    refs.update({"generation." + name: getattr(generation, name) for name in
                 ("policy_ref", "observation_ref", "action_ref", "generation_ref", "token_ref")})
    refs.update({"evaluation." + name: getattr(evaluation, name) for name in
                 ("observation_ref", "action_ref", "rollout_ref", "replay_ref", "verifier_ref", "oracle_ref", "reward_ref")})
    for key, value in refs.items():
        if value is not None and not _ref_ok(value):
            return EligibilityInspection("REFUSED", (key + ".invalid_ref",))
    blocked = []
    if generation.actor == "frozen_codex":
        blocked.append("frozen_codex_not_trainable")
    if candidate.partition in ("validation", "held_out"):
        blocked.append("non_training_partition")
    if candidate.rights == "denied":
        blocked.append("rights_denied")
    if evaluation.acceptance == "fail":
        blocked.append("acceptance_failed")
    if evaluation.protected_regressions == "fail":
        blocked.append("protected_regression_failed")
    if (generation.generation_ref is not None and evaluation.verifier_ref is not None and
            generation.generation_ref.producer == evaluation.verifier_ref.producer):
        blocked.append("self_reported_verifier")
    if (generation.observation_ref is not None and evaluation.observation_ref is not None and
            generation.observation_ref != evaluation.observation_ref):
        blocked.append("observation_lineage_mismatch")
    if (generation.action_ref is not None and evaluation.action_ref is not None and
            generation.action_ref != evaluation.action_ref):
        blocked.append("action_lineage_mismatch")
    if blocked:
        return EligibilityInspection("BLOCKED", tuple(blocked))
    missing = [key + ".missing" for key, value in refs.items() if value is None and
               not (key == "generation.token_ref" and generation.actor == "proposer"
                    and candidate.method == "sft")]
    if candidate.partition == "unknown":
        missing.append("partition_unknown")
    if candidate.rights == "unknown":
        missing.append("rights_unknown")
    if evaluation.acceptance == "unknown":
        missing.append("acceptance_unknown")
    if evaluation.protected_regressions == "unknown":
        missing.append("protected_regressions_unknown")
    if evaluation.effect_status == "unknown":
        missing.append("external_effect_unknown")
    if missing:
        return EligibilityInspection("INCONCLUSIVE", tuple(missing))
    return EligibilityInspection("STRUCTURALLY_ELIGIBLE", ())
