"""Read-only Codex MCP transport and exact original-owner adapter controls."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "plugins/codex-mcp/server.py"
spec = importlib.util.spec_from_file_location("neoweaver_mcp_bridge_under_test", SERVER)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def ref(s):
    return {"producer": "original-owner", "reference": s}


class OriginalOwnerMcpTests(unittest.TestCase):
    def test_transport_exposes_only_read_only_tools(self):
        output = bridge._dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        names = {t["name"] for t in output["tools"]}
        self.assertEqual(names, {
            "bridge_capabilities", "soodles_test_plan", "factoryweaver_project",
            "neoweaver_training_screen", "neoweaver_patch_parse", "owner_evidence_range",
        })
        self.assertFalse(any("edit" in n or "execute" in n or "merge" in n for n in names))
        with self.assertRaises(bridge.Refusal):
            bridge._dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                              "params": {"name": "arbitrary_shell", "arguments": {}}})

    def test_unconfigured_and_wrong_head_fail_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(bridge.Refusal, "soodles_source_not_pinned"):
                bridge._plan({})
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            with patch.dict(os.environ, {
                "HARNESS_SOODLES_ROOT": str(root),
                "HARNESS_SOODLES_HEAD": "0" * 40,
                "HARNESS_SOODLES_TEST_BASE_SHA": "1" * 40,
            }, clear=True):
                with self.assertRaisesRegex(bridge.Refusal, "soodles_head_mismatch"):
                    bridge._plan({})

    def test_original_test_manager_is_plan_only_and_exact_base(self):
        with patch.object(bridge, "_source", return_value=ROOT) as source:
            with patch.object(bridge, "_call_original", return_value={"status": "OWNER_RESULT"}) as call:
                with patch.dict(os.environ, {"HARNESS_SOODLES_TEST_BASE_SHA": "a" * 40}):
                    value = bridge._plan({})
                self.assertEqual(value["status"], "OWNER_RESULT")
                source.assert_called_once_with("soodles")
                argv = call.call_args.args[1]
                self.assertEqual(argv[1:], ["test", "--base", "a" * 40, "--plan"])
                self.assertNotIn("--full", argv)
        with patch.object(bridge, "_source", return_value=ROOT):
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(bridge.Refusal, "original_test_base_not_pinned"):
                    bridge._plan({})

    def test_factory_command_allowlist_no_arbitrary_shell(self):
        with patch.object(bridge, "_source", return_value=ROOT):
            with self.assertRaisesRegex(bridge.Refusal, "unknown_factory_operation"):
                bridge._factory({"record_path": "README.md", "operation": "execute"})
            with self.assertRaisesRegex(bridge.Refusal, "path_escape"):
                bridge._factory({"record_path": "../secret.json", "operation": "project"})
            with self.assertRaisesRegex(bridge.Refusal, "invalid_relative_path"):
                bridge._factory({"record_path": "/etc/passwd", "operation": "validate"})

    def test_training_screen_consumes_original_A6_eligibility(self):
        facts = {
            "actor": "frozen_codex", "method": "policy_gradient",
            "partition": "held_out", "rights": "unknown",
            "acceptance": "unknown", "protected_regressions": "unknown",
            "effect_status": "unknown", "lineage": "unknown",
            "token_provenance": "missing", "replay": "unknown",
            "verifier": "unknown", "reward": "unknown",
        }
        with patch.object(bridge, "_source", return_value=ROOT):
            result = bridge._candidate({"candidate": facts})
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["eligible_for_training"])
            self.assertIn("frozen_codex_not_trainable", result["reasons"])
            with self.assertRaisesRegex(bridge.Refusal, "candidate_fields_mismatch"):
                bridge._candidate({"candidate": {"actor": "frozen_codex"}})

    def test_original_patch_parser_positive_and_stale_refusal(self):
        fixed = {
            "snapshot_ref": ref("snapshot"), "failure_ref": ref("failure"),
            "allowlist_ref": ref("allowlist"), "acceptance_ref": ref("acceptance"),
            "causal_target_ref": ref("target"),
            "allowlist": [{"surface": "mcp_wrapper", "target_ref": ref("target"),
                           "expected_source_ref": ref("before")}],
            "protected_target_refs": [ref("oracle")],
        }
        candidate = {
            "kind": "neoweaver/patch-proposal/v1",
            "snapshot_ref": ref("snapshot"), "failure_ref": ref("failure"),
            "allowlist_ref": ref("allowlist"), "acceptance_ref": ref("acceptance"),
            "surface": "mcp_wrapper",
            "changes": [{"target_ref": ref("target"),
                         "expected_source_ref": ref("before"), "replacement": "a"}],
        }
        with patch.object(bridge, "_source", return_value=ROOT):
            a = bridge._patch({"proposal_json": json.dumps(candidate), "fixed_inputs": fixed})
            self.assertEqual(a["status"], "PARSED_ONLY")
            self.assertFalse(a["authorizes_effects"])
            candidate["changes"][0]["expected_source_ref"] = ref("stale")
            b = bridge._patch({"proposal_json": json.dumps(candidate), "fixed_inputs": fixed})
            self.assertEqual(b["status"], "REFUSED")
            self.assertEqual(b["condition"], "stale_expected_source")

    def test_original_evidence_range_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = "one\ntwo\n三\n".encode("utf-8")
            file = root / "original.txt"
            file.write_bytes(payload)
            original = {"path": str(file), "sha256": hashlib.sha256(payload).hexdigest()}
            args = {"ref": original, "offset": 0, "max_bytes": len(payload)}
            with patch.dict(os.environ, {"HARNESS_EVIDENCE_ROOT": str(root)}):
                ok = bridge._evidence(args)
                self.assertEqual(ok["text"], payload.decode())
                self.assertTrue(ok["eof"])
                self.assertFalse(ok["authorizes_effects"])
                with self.assertRaisesRegex(bridge.Refusal, "not_utf8_aligned_recall"):
                    bridge._evidence({**args, "offset": len("one\ntwo\n".encode()) + 1,
                                      "max_bytes": 1})
                file.write_text("changed", encoding="utf-8")
                with self.assertRaisesRegex(bridge.Refusal, "original_evidence_hash_mismatch"):
                    bridge._evidence(args)
                with self.assertRaisesRegex(bridge.Refusal, "evidence_path_outside_root"):
                    bridge._evidence({**args, "ref": {"path": "/etc/passwd",
                                                    "sha256": original["sha256"]}})

    def test_original_oversize_result_cannot_be_reported_as_pass(self):
        class Outcome:
            returncode = 0
            stdout = b"x" * (bridge.MAX_RESULT + 1)
            stderr = b""
        with patch.object(bridge.subprocess, "run", return_value=Outcome()):
            with self.assertRaisesRegex(bridge.Refusal, "original_output_exceeds_bound"):
                bridge._call_original(ROOT, ["original", "readonly"])

    def test_actual_stdio_protocol_initialize_tools_and_typed_refusal(self):
        protocol = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "soodles_test_plan", "arguments": {}}},
        ]
        runner = subprocess.run(
            [sys.executable, str(SERVER)],
            input="".join(json.dumps(item) + "\n" for item in protocol),
            text=True, capture_output=True, check=False, timeout=15,
            env={k: v for k, v in os.environ.items() if not k.startswith("HARNESS_")})
        self.assertEqual(runner.returncode, 0, runner.stderr)
        lines = [json.loads(row) for row in runner.stdout.splitlines()]
        self.assertEqual([row["id"] for row in lines], [1, 2, 3])
        self.assertEqual(lines[0]["result"]["serverInfo"]["name"], "neoweaver-original-owner-bridge")
        self.assertTrue(lines[2]["result"]["isError"])
        self.assertIn("soodles_source_not_pinned",
                      lines[2]["result"]["content"][0]["text"])

    def test_portable_plugin_manifest_has_no_untrusted_hooks(self):
        base = ROOT / "plugins/codex-mcp"
        plugin = json.loads((base / "plugin.json").read_text())
        mcp = json.loads((base / "mcp.json").read_text())
        self.assertEqual(plugin["name"], "neoweaver-owner-tools")
        self.assertNotIn("hooks", plugin)
        self.assertEqual(mcp["mcpServers"]["neoweaver-owner-tools"]["type"], "stdio")
        self.assertEqual(mcp["mcpServers"]["neoweaver-owner-tools"]["command"], "python3")


if __name__ == "__main__":
    unittest.main()
