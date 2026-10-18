"""Harness² -> original NeoWeaver bounded proposal/paired readback *adapter*.

Harness² Propose-Probe-Compose is a decision policy, not a second Soodles
effect owner. Native runs and independent Oracle are called by their original
owners only. Never invoke upstream unrestricted-network executor here.
"""
from dataclasses import dataclass

from .patches import ParsedProposal, DiagnosticRefusal, parse_proposal
from .native import NativePairReport


class Harness2BridgeRefusal(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Harness2Design:
    source_kind: str
    surface: str
    original_snapshot: object
    failure: object
    target: object
    comparison: str = "H0_H1_PROPOSED"
    k: int = 1
    mode: str = "sequential"
    executes_native_probe: bool = False
    authorizes_landing: bool = False


@dataclass(frozen=True, slots=True)
class Harness2ProbeInspection:
    status: str
    treatment: str
    original_pair_status: str
    oracle_results: tuple[str, str]
    improvement_verified: bool = False
    reward: None = None
    authorizes_training: bool = False
    authorizes_landing: bool = False


def propose_bounded_harness(raw: bytes, fixed_inputs: dict):
    """Reuse original patch parser; never reimplement the mutation gate."""
    result = parse_proposal(raw, fixed_inputs)
    if type(result) is DiagnosticRefusal:
        return result
    if type(result) is not ParsedProposal:
        raise Harness2BridgeRefusal("unexpected_original_proposal_result")
    return Harness2Design(
        source_kind=result.kind, surface=result.surface,
        original_snapshot=result.snapshot_ref,
        failure=result.failure_ref,
        target=result.changes[0].target_ref,
    )


def inspect_original_harness_probe(original: NativePairReport):
    """Represent completed existing native inspection without asserting gain.

    H0/H0 may support transport validity but never Harness improvement.
    H0/H1 that passes only scoped parser oracle still requires independent
    task-outcome evaluation and actual isolation/effect readback.
    """
    if type(original) is not NativePairReport:
        raise Harness2BridgeRefusal("native_original_pair_required")
    results = tuple(r.status for r in original.oracle_results)
    if len(results) != 2 or any(not isinstance(x, str) for x in results):
        raise Harness2BridgeRefusal("invalid_original_pair_results")
    pair_status = original.pair.status
    return Harness2ProbeInspection(
        "INCONCLUSIVE" if pair_status != "REFUSED" else "REFUSED",
        original.treatment, pair_status, results,
    )
