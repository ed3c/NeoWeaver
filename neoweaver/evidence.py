"""A6.1: independently read original evidence receipts, never self-issue eligibility."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
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


def _candidate_refs(candidate: TrainingCandidate):
    """Reuse the one original relation list, including optional SFT tokens."""
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
    return refs


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
    refs = _candidate_refs(candidate)
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


_MAX_RECEIPT_BYTES = 1024 * 1024
_SHA256 = re.compile(r"[0-9a-f]{64}")


def read_pinned_owner_evidence(candidate: TrainingCandidate, file_refs: Mapping[str, object],
                               *, owner_root: Path) -> EvidenceReadback:
    """Read exact original source bytes before using A6.1's relation screen.

    Only a separately configured Host may choose owner_root and the original
    producer's {path, sha256} FileRefs. A caller-composed mapping is NOT an
    authentication credential. This method does not authorize training.
    """
    screened = inspect_training_candidate(candidate)
    if screened.status != "STRUCTURALLY_ELIGIBLE":
        return EvidenceReadback(screened.status, screened.reasons, ())
    if not isinstance(file_refs, Mapping) or not isinstance(owner_root, Path):
        return EvidenceReadback("REFUSED", ("invalid_source_selection",), ())
    try:
        original_root = owner_root.absolute()
        if owner_root.is_symlink() or not original_root.is_dir():
            return EvidenceReadback("REFUSED", ("invalid_owner_root",), ())
        original_root = original_root.resolve(strict=True)
    except (OSError, ValueError):
        return EvidenceReadback("REFUSED", ("invalid_owner_root",), ())
    expected_refs = _candidate_refs(candidate)
    if any(type(key) is not str or key not in expected_refs for key in file_refs):
        return EvidenceReadback("REFUSED", ("foreign_receipt_slot",), ())

    restored, checked, missing, refused, used = {}, [], [], [], set()
    for slot, expected in expected_refs.items():
        record = file_refs.get(slot)
        if record is None:
            missing.append(slot + ".missing")
            continue
        if (type(record) is not dict or set(record) != {"path", "sha256"}
                or type(record["path"]) is not str or type(record["sha256"]) is not str
                or not _SHA256.fullmatch(record["sha256"])):
            refused.append(slot + ".invalid_file_ref")
            continue
        try:
            source = Path(record["path"])
            if (not source.is_absolute() or ".." in source.parts or
                    not source.is_relative_to(original_root)):
                refused.append(slot + ".outside_owner_root")
                continue
            # Refuse symbolic links at any level under the Host-selected root;
            # never interpret opaque OwnerRef.reference as a path.
            relative = source.relative_to(original_root)
            cursor = original_root
            for part in relative.parts:
                cursor = cursor / part
                if cursor.is_symlink():
                    raise ValueError("symlink")
            resolved = source.resolve(strict=True)
            if (resolved == original_root or not resolved.is_relative_to(original_root)
                    or not resolved.is_file()):
                raise ValueError("not_regular")
            if resolved in used:
                refused.append(slot + ".reused_source_file")
                continue
            used.add(resolved)
            # Bound the receipt size. The Host must protect its source root
            # against concurrent unauthorized mutation; digest checks detect
            # changed bytes but do not authenticate the original producer.
            with resolved.open("rb") as stream:
                raw = stream.read(_MAX_RECEIPT_BYTES + 1)
            if len(raw) > _MAX_RECEIPT_BYTES:
                refused.append(slot + ".source_too_large")
                continue
            if hashlib.sha256(raw).hexdigest() != record["sha256"]:
                refused.append(slot + ".digest_mismatch")
                continue

            def unique(pairs):
                obj = {}
                for key, value in pairs:
                    if key in obj:
                        raise ValueError("duplicate_json_key")
                    obj[key] = value
                return obj

            def nonfinite(value):
                raise ValueError("nonfinite_json_number")

            receipt = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                                 parse_constant=nonfinite)
            if (type(receipt) is not dict or set(receipt) != {"ref", "readback"}
                    or type(receipt["ref"]) is not dict
                    or set(receipt["ref"]) != {"producer", "reference"}
                    or any(type(receipt["ref"][key]) is not str for key in ("producer", "reference"))
                    or type(receipt["readback"]) is not str):
                refused.append(slot + ".invalid_source_payload")
                continue
            restored[slot] = {
                "ref": OwnerRef(receipt["ref"]["producer"], receipt["ref"]["reference"]),
                "readback": receipt["readback"],
            }
            checked.append(slot)
        except FileNotFoundError:
            missing.append(slot + ".source_missing")
        except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
            refused.append(slot + ".unreadable_source")
    if refused:
        return EvidenceReadback("REFUSED", tuple(refused), tuple(checked))
    result = verify_owner_evidence(candidate, restored)
    if missing:
        return EvidenceReadback("INCONCLUSIVE", tuple(missing) + result.reasons, tuple(checked))
    if result.status == "RECEIPTS_MATCH_DECLARATIONS":
        # "observed" remains a claim *inside* verified bytes; it is not an
        # independent provider/authentication or model-training receipt.
        return EvidenceReadback("SOURCE_BYTES_MATCH_DECLARATIONS", (), tuple(checked))
    return result
