"""Parse proposal bytes against Owner-fixed data without reading or changing sources."""
from collections.abc import Mapping
from dataclasses import dataclass
import json
import math


KIND = "neoweaver/patch-proposal/v1"
SURFACES = ("skill_instruction", "context_policy", "mcp_wrapper")


@dataclass(frozen=True, slots=True)
class OwnerRef:
    producer: str
    reference: str


@dataclass(frozen=True, slots=True)
class AllowedTarget:
    surface: str
    target_ref: OwnerRef
    expected_source_ref: OwnerRef


@dataclass(frozen=True, slots=True)
class FixedInputs:
    snapshot_ref: OwnerRef
    failure_ref: OwnerRef
    allowlist_ref: OwnerRef
    acceptance_ref: OwnerRef
    causal_target_ref: OwnerRef
    allowlist: tuple[AllowedTarget, ...]
    protected_target_refs: tuple[OwnerRef, ...]


@dataclass(frozen=True, slots=True)
class Change:
    target_ref: OwnerRef
    expected_source_ref: OwnerRef
    replacement: str


@dataclass(frozen=True, slots=True)
class ParsedProposal:
    raw: bytes
    kind: str
    snapshot_ref: OwnerRef
    failure_ref: OwnerRef
    allowlist_ref: OwnerRef
    acceptance_ref: OwnerRef
    surface: str
    changes: tuple[Change, ...]
    fixed_inputs: FixedInputs


@dataclass(frozen=True, slots=True)
class DiagnosticRefusal:
    raw: bytes | None
    condition: str
    path: str
    fixed_inputs: FixedInputs | None = None


class _Refusal(ValueError):
    def __init__(self, condition, path):
        self.condition = condition
        self.path = path


def _object(value, keys, path, *, fixed=False):
    if not isinstance(value, Mapping) or any(type(key) is not str for key in value):
        raise _Refusal("invalid_fixed_input_type" if fixed else "invalid_type", path)
    missing = sorted(set(keys) - value.keys())
    if missing:
        raise _Refusal("missing_fixed_input" if fixed else "missing_field", path + "." + missing[0])
    extra = sorted(value.keys() - set(keys))
    if extra:
        raise _Refusal("extra_fixed_input" if fixed else "extra_field", path + "." + extra[0])
    return value


def _text(value, path, *, fixed=False):
    if type(value) is not str:
        raise _Refusal("invalid_fixed_input_type" if fixed else "invalid_type", path)
    if not value:
        raise _Refusal("empty_fixed_input" if fixed else "empty_string", path)
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise _Refusal("invalid_unicode_string", path)
    return value


def _ref(value, path, *, fixed=False):
    value = _object(value, ("producer", "reference"), path, fixed=fixed)
    return OwnerRef(*(_text(value[key], path + "." + key, fixed=fixed)
                      for key in ("producer", "reference")))


def _array(value, path, *, fixed=False, nonempty=True):
    if type(value) is not list:
        raise _Refusal("invalid_fixed_input_type" if fixed else "invalid_type", path)
    if nonempty and not value:
        raise _Refusal("empty_fixed_input" if fixed else "empty_changes", path)
    return value


def _surface(value, path, *, fixed=False):
    value = _text(value, path, fixed=fixed)
    if value not in SURFACES:
        raise _Refusal("unsupported_surface", path)
    return value


def _fixed_inputs(value):
    keys = ("snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref",
            "causal_target_ref", "allowlist", "protected_target_refs")
    value = _object(value, keys, "fixed_inputs", fixed=True)
    refs = tuple(_ref(value[key], "fixed_inputs." + key, fixed=True) for key in keys[:5])
    allowed = []
    seen = set()
    for index, item in enumerate(_array(value["allowlist"], "fixed_inputs.allowlist", fixed=True)):
        path = f"fixed_inputs.allowlist[{index}]"
        item = _object(item, ("surface", "target_ref", "expected_source_ref"), path, fixed=True)
        entry = AllowedTarget(_surface(item["surface"], path + ".surface", fixed=True),
                              _ref(item["target_ref"], path + ".target_ref", fixed=True),
                              _ref(item["expected_source_ref"], path + ".expected_source_ref", fixed=True))
        identity = (entry.surface, entry.target_ref)
        if identity in seen:
            raise _Refusal("ambiguous_allowlist", path)
        seen.add(identity)
        allowed.append(entry)
    protected = tuple(_ref(item, f"fixed_inputs.protected_target_refs[{index}]", fixed=True)
                      for index, item in enumerate(_array(value["protected_target_refs"],
                                                         "fixed_inputs.protected_target_refs", fixed=True,
                                                         nonempty=False)))
    return FixedInputs(*refs, tuple(allowed), protected)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _Refusal("duplicate_json_key", key)
        result[key] = value
    return result


def _nonfinite(value):
    raise _Refusal("nonfinite_json_number", "$raw")


def _float(value):
    number = float(value)
    if not math.isfinite(number):
        _nonfinite(value)
    return number


def parse_proposal(raw: bytes, fixed_inputs: Mapping[str, object]) -> ParsedProposal | DiagnosticRefusal:
    """Return immutable data or a named refusal; see docs/parser-contract.md."""
    fixed = None
    original = raw if type(raw) is bytes else None
    try:
        if original is None:
            raise _Refusal("invalid_raw_type", "$raw")
        fixed = _fixed_inputs(fixed_inputs)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise _Refusal("invalid_utf8", "$raw") from None
        try:
            proposal = json.loads(text, object_pairs_hook=_unique,
                                  parse_constant=_nonfinite, parse_float=_float)
        except (json.JSONDecodeError, ValueError, RecursionError) as error:
            if isinstance(error, _Refusal):
                raise
            raise _Refusal("malformed_json", "$raw") from None
        refs = ("snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref")
        proposal = _object(proposal, ("kind", *refs, "surface", "changes"), "proposal")
        if proposal["kind"] != KIND:
            raise _Refusal("unsupported_kind", "proposal.kind")
        for key in refs:
            if _ref(proposal[key], "proposal." + key) != getattr(fixed, key):
                raise _Refusal("fixed_reference_mismatch", "proposal." + key)
        surface = _surface(proposal["surface"], "proposal.surface")
        changes = []
        for index, item in enumerate(_array(proposal["changes"], "proposal.changes")):
            path = f"proposal.changes[{index}]"
            item = _object(item, ("target_ref", "expected_source_ref", "replacement"), path)
            changes.append(Change(_ref(item["target_ref"], path + ".target_ref"),
                                  _ref(item["expected_source_ref"], path + ".expected_source_ref"),
                                  _text(item["replacement"], path + ".replacement")))
        if len({change.target_ref for change in changes}) > 1:
            raise _Refusal("multiple_causal_targets", "proposal.changes")
        target = changes[0].target_ref
        if target == fixed.acceptance_ref or target in fixed.protected_target_refs:
            raise _Refusal("protected_target", "proposal.changes[0].target_ref")
        allowed = next((entry for entry in fixed.allowlist
                        if entry.surface == surface and entry.target_ref == target), None)
        if allowed is None:
            raise _Refusal("target_outside_allowlist", "proposal.changes[0].target_ref")
        if target != fixed.causal_target_ref:
            raise _Refusal("causal_target_mismatch", "proposal.changes[0].target_ref")
        for index, change in enumerate(changes):
            if change.expected_source_ref != allowed.expected_source_ref:
                raise _Refusal("stale_expected_source", f"proposal.changes[{index}].expected_source_ref")
        if len(changes) > 1:
            raise _Refusal("ambiguous_replacement_order", "proposal.changes")
        return ParsedProposal(raw, KIND, fixed.snapshot_ref, fixed.failure_ref, fixed.allowlist_ref,
                              fixed.acceptance_ref, surface, tuple(changes), fixed)
    except _Refusal as error:
        return DiagnosticRefusal(original, error.condition, error.path, fixed)
