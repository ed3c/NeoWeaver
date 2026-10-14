"""A6.1: independently read original evidence receipts, never self-issue eligibility."""
from dataclasses import dataclass
from typing import Mapping

from .learning import TrainingCandidate, inspect_training_candidate
from .patches import OwnerRef


@dataclass(frozen=True, slots=True)
class EvidenceReadback:
    status: str
    reasons: tuple[str, ...]
    checked: tuple[str, ...]
    eligible_for_training: bool = False
    authorizes_landing: bool = False


def verify_owner_evidence(candidate: TrainingCandidate, receipts: Mapping[str, object]) -> EvidenceReadback:
    """Require source-owner receipts for every claimed reference.

    The receipts are supplied by a separate reader, never the proposer.
    Matching declarations do not prove producer independence or authenticity.
    """
    screened = inspect_training_candidate(candidate)
    if screened.status != "STRUCTURALLY_ELIGIBLE":
        return EvidenceReadback(screened.status, screened.reasons, ())
    if not isinstance(receipts, Mapping):
        return EvidenceReadback("REFUSED", ("invalid_receipts",), ())
    refs = {
        "rights": candidate.rights_ref,
        "partition": candidate.partition_ref,
        "policy": candidate.generation.policy_ref,
        "observation": candidate.generation.observation_ref,
        "action": candidate.generation.action_ref,
        "generation": candidate.generation.generation_ref,
        "rollout": candidate.evaluation.rollout_ref,
        "replay": candidate.evaluation.replay_ref,
        "verifier": candidate.evaluation.verifier_ref,
        "oracle": candidate.evaluation.oracle_ref,
        "reward": candidate.evaluation.reward_ref,
    }
    if candidate.generation.token_ref is not None:
        refs["tokens"] = candidate.generation.token_ref
    missing, mismatched, checked = [], [], []
    for name, expected in refs.items():
        receipt = receipts.get(name)
        if receipt is None:
            missing.append(name + ".missing")
            continue
        if not isinstance(receipt, Mapping):
            mismatched.append(name + ".invalid_receipt")
            continue
        actual = receipt.get("ref")
        if type(actual) is not OwnerRef or actual != expected:
            mismatched.append(name + ".ref_mismatch")
            continue
        if receipt.get("readback") != "observed":
            missing.append(name + ".not_observed")
            continue
        checked.append(name)
    if mismatched:
        return EvidenceReadback("REFUSED", tuple(mismatched), tuple(checked))
    if missing:
        return EvidenceReadback("INCONCLUSIVE", tuple(missing), tuple(checked))
    return EvidenceReadback("RECEIPTS_MATCH_DECLARATIONS", (), tuple(checked))
