"""Read-only A5 paired-replay readiness on externally produced runner readbacks.

This module never executes a task, dereferences OwnerRef, or certifies isolation.
Original Snapshot Runner and independent Oracle remain separate owners.
"""
from dataclasses import dataclass

from .patches import OwnerRef


@dataclass(frozen=True, slots=True)
class RunReadback:
    """A claim emitted by an external runner, not a trust credential."""

    arm: str
    snapshot_ref: OwnerRef | None
    task_ref: OwnerRef | None
    environment_ref: OwnerRef | None
    solver_ref: OwnerRef | None
    seed_policy_ref: OwnerRef | None
    budget_ref: OwnerRef | None
    oracle_ref: OwnerRef | None
    harness_ref: OwnerRef | None
    run_ref: OwnerRef | None
    sandbox_ref: OwnerRef | None
    capture_ref: OwnerRef | None
    terminal: str  # completed / partial / unknown
    completed: bool | None
    effect_status: str  # none_observed / unknown


@dataclass(frozen=True, slots=True)
class PairInspection:
    status: str  # REFUSED / INCONCLUSIVE / STRUCTURALLY_COMPARABLE
    reasons: tuple[str, ...]
    reported_completion: tuple[bool, bool] | None
    evidence_ceiling: str = "DECLARED_RUNNER_READBACKS_ONLY"
    authorizes_landing: bool = False


_MATCHED = (
    "snapshot_ref", "task_ref", "environment_ref", "solver_ref",
    "seed_policy_ref", "budget_ref", "oracle_ref",
)
_SEPARATE = ("run_ref", "sandbox_ref", "capture_ref")


def _valid_ref(value):
    return (type(value) is OwnerRef and type(value.producer) is str
            and bool(value.producer.strip()) and type(value.reference) is str
            and bool(value.reference.strip()))


def inspect_pair(baseline: RunReadback, candidate: RunReadback) -> PairInspection:
    """Check matching fixed conditions without trusting or executing the producer.

    Missing external captures or unknown effects stay INCONCLUSIVE. A matched
    pair is *eligible for independent evaluation*, never a PASS or reward.
    """
    if type(baseline) is not RunReadback or type(candidate) is not RunReadback:
        return PairInspection("REFUSED", ("invalid_readback_type",), None)
    if (baseline.arm, candidate.arm) != ("baseline", "candidate"):
        return PairInspection("REFUSED", ("wrong_arm_order",), None)
    for arm, run in (("baseline", baseline), ("candidate", candidate)):
        for field in (*_MATCHED, "harness_ref"):
            value = getattr(run, field)
            if value is not None and not _valid_ref(value):
                return PairInspection("REFUSED", (f"{arm}.{field}.invalid_ref",), None)
        for field in _SEPARATE:
            value = getattr(run, field)
            if value is not None and not _valid_ref(value):
                return PairInspection("REFUSED", (f"{arm}.{field}.invalid_ref",), None)
        if run.terminal not in ("completed", "partial", "unknown"):
            return PairInspection("REFUSED", (f"{arm}.invalid_terminal",), None)
        if run.effect_status not in ("none_observed", "unknown"):
            return PairInspection("REFUSED", (f"{arm}.invalid_effect_status",), None)
        if run.completed is not None and type(run.completed) is not bool:
            return PairInspection("REFUSED", (f"{arm}.invalid_completion",), None)
        if run.terminal != "completed" and run.completed is not None:
            return PairInspection("REFUSED", (f"{arm}.nonterminal_completion",), None)

    missing = []
    for arm, run in (("baseline", baseline), ("candidate", candidate)):
        for field in (*_MATCHED, "harness_ref"):
            if getattr(run, field) is None:
                missing.append(f"{arm}.missing_{field}")
    for field in _MATCHED:
        if getattr(baseline, field) != getattr(candidate, field):
            missing.append("unmatched_" + field)
    for field in _SEPARATE:
        b, c = getattr(baseline, field), getattr(candidate, field)
        if b is None or c is None:
            missing.append("missing_" + field)
        elif b == c:
            missing.append("reused_" + field)
    for arm, run in (("baseline", baseline), ("candidate", candidate)):
        if run.terminal != "completed" or run.completed is None:
            missing.append(arm + ".missing_terminal_result")
        if run.effect_status == "unknown":
            missing.append(arm + ".unknown_effect")
    if missing:
        return PairInspection("INCONCLUSIVE", tuple(missing), None)
    return PairInspection("STRUCTURALLY_COMPARABLE", (),
                          (baseline.completed, candidate.completed))
