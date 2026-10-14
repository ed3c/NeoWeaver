"""Original Docker provider configuration readback; no daemon calls in unit test."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from neoweaver.execution import ContainerCapture, ContainerTask, inspect_container_capture
from neoweaver.snapshot import SourceFile, SourceManifest, StagedSource, StagedSourcePair
import hashlib


ID = "a" * 64
IMAGE = "runtime@sha256:" + "b" * 64


class ProviderReadbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.capture = ContainerCapture("baseline", "nw-replay-test", "EXIT_RECORDED", 0,
                                        self.root / "out", self.root / "err", "a" * 64, "b" * 64,
                                        0.1, "c" * 64, ID)
        self.task = ContainerTask(IMAGE, ("/bin/true",), 15)
        self.source = self.root / "source"
        self.source.mkdir()
        self.alternate = self.root / "candidate"
        self.alternate.mkdir()
        for folder in (self.source, self.alternate):
            (folder / "file.txt").write_bytes(b"pinned")
        checksum = hashlib.sha256(b"pinned").hexdigest()
        manifest = SourceManifest((SourceFile("file.txt", checksum, False),),
                                  hashlib.sha256(b"file.txt\0-" + bytes.fromhex(checksum)).hexdigest())
        self.pair = StagedSourcePair("a" * 40, "b" * 40,
                                     StagedSource(self.source, manifest),
                                     StagedSource(self.alternate, manifest))
        (self.root / "container.cid").write_text(ID + "\n")
        self.capture = replace(self.capture,
                               stdout_path=self.root / "stdout.bin", stderr_path=self.root / "stderr.bin",
                               source_manifest_sha256=manifest.sha256,
                               stdout_sha256=hashlib.sha256(b"").hexdigest(),
                               stderr_sha256=hashlib.sha256(b"").hexdigest())
        self.capture.stdout_path.write_bytes(b"")
        self.capture.stderr_path.write_bytes(b"")

    def record(self):
        return {"Id": ID, "Name": "/nw-replay-test", "State": {"Status": "exited", "Running": False, "ExitCode": 0},
                "Config": {"Image": IMAGE, "User": "65534:65534",
                           "Cmd": list(self.task.argv)},
                "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                               "Privileged": False, "AutoRemove": False, "CapDrop": ["ALL"],
                               "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64,
                               "Memory": 512 * 1024 * 1024, "NanoCpus": 1_000_000_000},
                "Mounts": [{"Type": "bind", "Source": str(self.source.resolve()),
                            "Destination": "/workspace", "RW": False}]}

    def inspect(self, obj, exit_code=0):
        def spy(cmd, **kwargs):
            self.assertEqual(cmd[-1], ID)
            self.assertEqual(cmd[1:5], ["inspect", "--type", "container", "--format"])
            return subprocess.CompletedProcess(cmd, exit_code, json.dumps(obj).encode())
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run", side_effect=spy):
            return inspect_container_capture(self.capture, self.task, self.pair)

    def test_exact_provider_exit_and_declared_options_are_metadata_only(self):
        result = self.inspect(self.record())
        self.assertEqual(result.status, "CONFIG_AND_EXIT_MATCH")
        self.assertFalse(result.isolation_verified)
        self.assertIsNone(result.task_completed)
        self.assertFalse(result.authorizes_landing)
        self.assertEqual(result.observed_exit_code, 0)

    def test_each_protective_drift_prevents_config_match(self):
        cases = [
            ("HostConfig", "NetworkMode", "bridge", "network_not_none"),
            ("HostConfig", "ReadonlyRootfs", False, "rootfs_not_readonly"),
            ("HostConfig", "Privileged", True, "privileged_container"),
            ("HostConfig", "AutoRemove", True, "container_autoremoved"),
            ("HostConfig", "CapDrop", [], "capabilities_not_dropped"),
            ("HostConfig", "SecurityOpt", [], "new_privileges_allowed"),
            ("HostConfig", "PidsLimit", 65, "pids_limit_mismatch"),
            ("HostConfig", "Memory", 0, "memory_limit_mismatch"),
            ("HostConfig", "NanoCpus", 0, "cpu_limit_mismatch"),
            ("Config", "Image", "unexpected", "image_mismatch"),
            ("Config", "User", "0:0", "user_mismatch"),
            ("Config", "Cmd", ["/bin/false"], "task_argv_mismatch"),
        ]
        for section, key, value, expected in cases:
            with self.subTest(key=key):
                record = self.record()
                record[section][key] = value
                self.assertIn(expected, self.inspect(record).reasons)

    def test_mount_write_and_identity_drift_refuse(self):
        for field, value in (("RW", True), ("Source", "/other")):
            obj = self.record()
            obj["Mounts"][0][field] = value
            self.assertIn("readonly_source_mount_mismatch", self.inspect(obj).reasons)
        obj = self.record()
        obj["Id"] = "f" * 64
        self.assertEqual(self.inspect(obj).status, "REFUSED")
        self.assertEqual(self.inspect(obj).reasons, ("wrong_provider_identity",))

    def test_nonterminal_and_unknown_engine_id_do_not_claim_results(self):
        obj = self.record()
        obj["State"]["Status"] = "running"
        self.assertEqual(self.inspect(obj).status, "INCONCLUSIVE")
        noid = replace(self.capture, container_id=None)
        with patch("neoweaver.execution.subprocess.run") as spy:
            observed = inspect_container_capture(noid, self.task, self.pair)
        self.assertEqual(observed.status, "INCONCLUSIVE")
        spy.assert_not_called()

    def test_provider_missing_and_cli_conflict_are_inconclusive(self):
        self.assertEqual(self.inspect(self.record(), exit_code=1).status, "INCONCLUSIVE")
        obj = self.record()
        obj["State"]["ExitCode"] = 1
        self.assertIn("exit_code_mismatch", self.inspect(obj).reasons)

    def test_capture_tampering_refuses_before_provider_inspect(self):
        self.capture.stdout_path.write_bytes(b"tampered")
        with patch("neoweaver.execution.subprocess.run") as spy:
            result = inspect_container_capture(self.capture, self.task, self.pair)
        self.assertEqual(result.status, "REFUSED")
        self.assertIn("capture_or_cid_mismatch", result.reasons)
        spy.assert_not_called()

    def test_original_source_and_cid_cannot_be_swapped(self):
        changed = replace(self.pair, baseline=replace(self.pair.baseline,
                          manifest=replace(self.pair.baseline.manifest, sha256="f" * 64)))
        self.assertEqual(inspect_container_capture(self.capture, self.task, changed).status, "REFUSED")
        (self.root / "container.cid").write_text("f" * 64)
        self.assertEqual(inspect_container_capture(self.capture, self.task, self.pair).status, "REFUSED")
        (self.root / "container.cid").write_text(ID)
        (self.source / "file.txt").write_bytes(b"changed")
        result = inspect_container_capture(self.capture, self.task, self.pair)
        self.assertEqual(result.status, "INCONCLUSIVE")
        self.assertIn("source_changed", result.reasons)

    def test_no_automatic_cleanup_or_mutating_provider_action(self):
        record = self.record()
        def spy(cmd, **kwargs):
            self.assertEqual(cmd[1], "inspect")
            self.assertNotIn("rm", cmd)
            return subprocess.CompletedProcess(cmd, 0, json.dumps(record).encode())
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run", side_effect=spy) as process:
            result = inspect_container_capture(self.capture, self.task, self.pair)
        self.assertEqual(result.status, "CONFIG_AND_EXIT_MATCH")
        process.assert_called_once()


if __name__ == "__main__":
    unittest.main()
