#!/usr/bin/env python3
"""Read-only MCP adapter. All substantive decisions remain with original CLI owners.

Run with Python 3.10+ over newline-delimited JSON-RPC (MCP stdio).
This module performs no writes, approvals, retries or background execution.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

MAX_REQUEST = 1 << 20
MAX_RESULT = 64 * 1024
MAX_RECALL = 8 * 1024
SOURCE_SETTINGS = {
    "soodles": ("HARNESS_SOODLES_ROOT", "HARNESS_SOODLES_HEAD"),
    "factoryweaver": ("HARNESS_FACTORYWEAVER_ROOT", "HARNESS_FACTORYWEAVER_HEAD"),
    "neoweaver": ("HARNESS_NEOWEAVER_ROOT", "HARNESS_NEOWEAVER_HEAD"),
}


class Refusal(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise Refusal("duplicate_json_key")
        out[key] = value
    return out


def strict_json(raw):
    return json.loads(raw, object_pairs_hook=_unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(Refusal("nonfinite_json")))


def _exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise Refusal("invalid_arguments")
    return value


def _sha(value):
    return type(value) is str and re.fullmatch(r"[a-f0-9]{40}", value) is not None


def _source(which):
    root_var, head_var = SOURCE_SETTINGS[which]
    raw_root, expected = os.environ.get(root_var), os.environ.get(head_var)
    if not raw_root or not _sha(expected):
        raise Refusal(which + "_source_not_pinned")
    root = Path(raw_root)
    if not root.is_absolute() or not root.is_dir():
        raise Refusal(which + "_source_unavailable")
    root = root.resolve()
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                              text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Refusal(which + "_git_readback_unavailable") from None
    if proc.returncode != 0 or proc.stdout.strip() != expected:
        raise Refusal(which + "_head_mismatch")
    return root


def _child(root, relative):
    if type(relative) is not str or not relative or Path(relative).is_absolute():
        raise Refusal("invalid_relative_path")
    if ".." in Path(relative).parts or "\\x00" in relative:
        raise Refusal("path_escape")
    selected = (root / relative).resolve()
    if not selected.is_relative_to(root) or not selected.is_file():
        raise Refusal("unavailable_or_foreign_file")
    return selected


def _call_original(root, argv):
    # Executable and argv are exclusively fixed here, never selected by model prose.
    try:
        p = subprocess.run(argv, cwd=root, capture_output=True, timeout=25, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Refusal("original_owner_process_unavailable") from None
    if len(p.stdout) > MAX_RESULT or len(p.stderr) > MAX_RESULT:
        raise Refusal("original_output_exceeds_bound_no_truncated_pass")
    try:
        original = strict_json(p.stdout.decode("utf-8")) if p.stdout else None
    except (ValueError, UnicodeError, Refusal):
        raise Refusal("original_owner_non_json_response") from None
    return {
        "status": "OWNER_RESULT" if p.returncode == 0 else "OWNER_REFUSAL",
        "exit_code": p.returncode,
        "original_owner_result": original,
        "evidence_ceiling": "ORIGINAL_CLI_OUTPUT_ONLY",
        "authorizes_effects": False,
        "authorizes_landing": False,
    }


def _candidate(args):
    _exact(args, ("candidate",))
    facts = args["candidate"]
    _source("neoweaver")
    sys.path.insert(0, str(_source("neoweaver")))
    from neoweaver.learning import TrainingCandidate, inspect_training_candidate
    if type(facts) is not dict or set(facts) != set(TrainingCandidate.__dataclass_fields__):
        raise Refusal("candidate_fields_mismatch")
    result = inspect_training_candidate(TrainingCandidate(**facts))
    return asdict(result)


def _patch(args):
    _exact(args, ("proposal_json", "fixed_inputs"))
    if type(args["proposal_json"]) is not str or type(args["fixed_inputs"]) is not dict:
        raise Refusal("invalid_patch_input")
    _source("neoweaver")
    sys.path.insert(0, str(_source("neoweaver")))
    from neoweaver.patches import DiagnosticRefusal, parse_proposal
    outcome = parse_proposal(args["proposal_json"].encode("utf-8"), args["fixed_inputs"])
    if isinstance(outcome, DiagnosticRefusal):
        return {"status": "REFUSED", "condition": outcome.condition, "path": outcome.path,
                "evidence_ceiling": "CALLER_SUPPLIED_FIXED_INPUTS_ONLY",
                "authorizes_effects": False}
    return {"status": "PARSED_ONLY", "surface": outcome.surface,
            "change_count": len(outcome.changes),
            "evidence_ceiling": "CALLER_SUPPLIED_FIXED_INPUTS_ONLY",
            "authorizes_effects": False}


def _factory(args):
    _exact(args, ("record_path", "operation"))
    if args["operation"] not in ("validate", "project", "route"):
        raise Refusal("unknown_factory_operation")
    root = _source("factoryweaver")
    record = _child(root, args["record_path"])
    return _call_original(root, [sys.executable, str(root / "scripts/factoryweaver.py"),
                                 args["operation"], str(record)])


def _plan(args):
    _exact(args, ())
    root = _source("soodles")
    base = os.environ.get("HARNESS_SOODLES_TEST_BASE_SHA")
    if not _sha(base):
        raise Refusal("original_test_base_not_pinned")
    # Test Manager owns selection. No arbitrary --module, --full or shell entry.
    return _call_original(root, [str(root / "soodles"), "test", "--base", base, "--plan"])


def _soodles_cli_contracts(args):
    """Expose the original read-only CLI inventory; never make a second routing choice."""
    _exact(args, ())
    root = _source("soodles")
    return _call_original(root, [str(root / "soodles"), "schema", "cli-contracts"])


def _soodles_knowledge_inspect(args):
    """Pass the original Host-created FileRef unchanged to the original Knowledge Reader."""
    _exact(args, ("bundle_ref",))
    ref = _exact(args["bundle_ref"], ("path", "sha256"))
    root_dir = os.environ.get("HARNESS_EVIDENCE_ROOT")
    if not root_dir or not Path(root_dir).is_absolute():
        raise Refusal("evidence_root_not_configured")
    path, digest = ref["path"], ref["sha256"]
    if (type(path) is not str or not Path(path).is_absolute() or
            type(digest) is not str or re.fullmatch("[0-9a-f]{64}", digest) is None):
        raise Refusal("invalid_original_file_ref")
    owner_root = Path(root_dir).resolve()
    absolute = Path(path).resolve()
    if not absolute.is_relative_to(owner_root) or not absolute.is_file():
        raise Refusal("evidence_path_outside_root")
    root = _source("soodles")
    # The authoritative Soodles knowledge.inspect validates FileRef bytes/source;
    # this adapter never creates a new FileRef, task, admission or next.
    return _call_original(root, [str(root / "soodles"), "knowledge", "inspect",
                                 str(absolute), digest])


def _evidence(args):
    _exact(args, ("ref", "offset", "max_bytes"))
    ref = _exact(args["ref"], ("path", "sha256"))
    directory = os.environ.get("HARNESS_EVIDENCE_ROOT")
    if not directory or not Path(directory).is_absolute():
        raise Refusal("evidence_root_not_configured")
    root = Path(directory).resolve()
    path = ref["path"]
    digest = ref["sha256"]
    if (type(path) is not str or not Path(path).is_absolute() or
            type(digest) is not str or re.fullmatch("[0-9a-f]{64}", digest) is None):
        raise Refusal("invalid_original_file_ref")
    target = Path(path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise Refusal("evidence_path_outside_root")
    offset, size = args["offset"], args["max_bytes"]
    if type(offset) is not int or offset < 0 or type(size) is not int or not 1 <= size <= MAX_RECALL:
        raise Refusal("invalid_recall_bounds")
    # One descriptor; validate exact original producer's reference before returning bytes.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(target, flags)
        with os.fdopen(fd, "rb") as f:
            h = hashlib.sha256()
            while piece := f.read(65536):
                h.update(piece)
            total = f.tell()
            if h.hexdigest() != digest:
                raise Refusal("original_evidence_hash_mismatch")
            if offset > total:
                raise Refusal("offset_outside_evidence")
            f.seek(offset)
            chunk = f.read(size)
    except OSError:
        raise Refusal("original_evidence_unavailable") from None
    try:
        value = chunk.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        if error.reason != "unexpected end of data" or error.start == 0:
            raise Refusal("not_utf8_aligned_recall") from None
        # Cut a partial trailing code point; next_offset remains a valid UTF-8 boundary.
        chunk = chunk[:error.start]
        value = chunk.decode("utf-8", errors="strict")
    return {"status": "SCOPED_READ", "offset": offset, "next_offset": offset + len(chunk),
            "eof": offset + len(chunk) == total, "total_bytes": total, "text": value,
            "evidence_ceiling": "ORIGINAL_FILE_REF_ONLY", "authorizes_effects": False}


def _capabilities(args):
    _exact(args, ())
    found = {}
    for name in SOURCE_SETTINGS:
        try:
            root = _source(name)
            found[name] = {"status": "PIN_MATCHED", "root": str(root)}
        except Refusal as error:
            found[name] = {"status": "UNAVAILABLE", "reason": error.reason}
    return {"sources": found, "mode": "READ_ONLY", "authorizes_effects": False,
            "codex_native_consumer": "NOT_OBSERVED", "sol_pi_candidate": "NOT_OBSERVED"}


TOOLS = {
    "bridge_capabilities": ("Inspect configured exact-head source availability; no host-capability proof.",
                            {"type": "object", "properties": {}, "additionalProperties": False}, _capabilities),
    "soodles_test_plan": ("Call existing Soodles Test Manager once in --plan mode; never execute tests.",
                          {"type": "object", "properties": {}, "additionalProperties": False}, _plan),
    "soodles_cli_contracts": ("Call original Soodles schema CLI inventory; no tests, mutation or routing.",
                              {"type": "object", "properties": {}, "additionalProperties": False},
                              _soodles_cli_contracts),
    "soodles_knowledge_inspect": ("Consume original Host-bound Soodles FactoryWeaver Scope FileRef, without creating a new admission.",
                                  {"type": "object", "properties": {
                                      "bundle_ref": {"type": "object", "properties": {
                                          "path": {"type": "string"}, "sha256": {"type": "string"}},
                                          "required": ["path", "sha256"], "additionalProperties": False}},
                                   "required": ["bundle_ref"], "additionalProperties": False},
                                  _soodles_knowledge_inspect),
    "factoryweaver_project": ("Call original read-only FactoryWeaver knowledge CLI on a repository-scoped record.",
                              {"type": "object", "properties": {
                                  "record_path": {"type": "string"},
                                  "operation": {"type": "string", "enum": ["validate", "project", "route"]}},
                               "required": ["record_path", "operation"], "additionalProperties": False}, _factory),
    "neoweaver_training_screen": ("Invoke existing A6 typed candidate screen; supplied facts are not authenticated.",
                                  {"type": "object", "properties": {
                                      "candidate": {"type": "object"}},
                                   "required": ["candidate"], "additionalProperties": False}, _candidate),
    "neoweaver_patch_parse": ("Invoke original A6 bounded proposal parser with caller-provided fixed inputs; no effects.",
                              {"type": "object", "properties": {
                                  "proposal_json": {"type": "string"},
                                  "fixed_inputs": {"type": "object"}},
                               "required": ["proposal_json", "fixed_inputs"],
                               "additionalProperties": False}, _patch),
    "owner_evidence_range": ("Exact SHA-256-bound byte-range read inside configured evidence root; no new archive.",
                             {"type": "object", "properties": {
                                 "ref": {"type": "object", "properties": {
                                     "path": {"type": "string"}, "sha256": {"type": "string"}},
                                     "required": ["path", "sha256"], "additionalProperties": False},
                                 "offset": {"type": "integer", "minimum": 0},
                                 "max_bytes": {"type": "integer", "minimum": 1, "maximum": MAX_RECALL}},
                              "required": ["ref", "offset", "max_bytes"],
                              "additionalProperties": False}, _evidence),
}


def _reply(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _dispatch(message):
    if type(message) is not dict or message.get("jsonrpc") != "2.0":
        raise Refusal("invalid_rpc_envelope")
    method = message.get("method")
    if method == "initialize":
        return {"protocolVersion": "2025-06-18", "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "neoweaver-original-owner-bridge", "version": "0.1.0"}}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": [{"name": name, "description": desc, "inputSchema": schema,
                           "annotations": {"readOnlyHint": True, "destructiveHint": False}}
                          for name, (desc, schema, _) in TOOLS.items()]}
    if method == "tools/call":
        p = message.get("params")
        if type(p) is not dict or not set(p).issubset({"name", "arguments", "_meta"}):
            raise Refusal("invalid_tool_call")
        if p.get("name") not in TOOLS:
            raise Refusal("unknown_tool")
        args = p.get("arguments", {})
        if type(args) is not dict:
            raise Refusal("invalid_arguments")
        result = TOOLS[p["name"]][2](args)
        value = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        original_refused = (type(result) is dict and (
            result.get("status") in ("OWNER_REFUSAL", "REFUSED", "BLOCKED") or
            type(result.get("original_owner_result")) is dict and
            result["original_owner_result"].get("status") in ("refused", "invalid")))
        return {"content": [{"type": "text", "text": value}],
                "isError": bool(original_refused)}
    raise Refusal("unsupported_rpc_method")


def serve():
    while True:
        raw = sys.stdin.buffer.readline(MAX_REQUEST + 1)
        if not raw:
            return
        if len(raw) > MAX_REQUEST:
            _reply({"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32600, "message": "request_too_large"}})
            return
        try:
            msg = strict_json(raw.decode("utf-8"))
            if type(msg) is not dict:
                raise Refusal("invalid_rpc_envelope")
            if "id" not in msg:
                # MCP notifications never receive a JSON-RPC response.
                continue
            try:
                result = _dispatch(msg)
            except Refusal as exc:
                value = {"status": "REFUSED", "reason": exc.reason,
                         "authorizes_effects": False}
                result = {"content": [{"type": "text", "text": json.dumps(value)}],
                          "isError": True}
            _reply({"jsonrpc": "2.0", "id": msg["id"], "result": result})
        except (ValueError, UnicodeError, Refusal):
            _reply({"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": "invalid_json_or_envelope"}})


if __name__ == "__main__":
    serve()
