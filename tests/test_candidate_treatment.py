from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from neoweaver.execution import (
    ContainerTask, ExecutionRefusal, inspect_container_capture, run_container_arm,
)
from neoweaver.patches import DiagnosticRefusal, OwnerRef, ParsedProposal, parse_proposal
from neoweaver.snapshot import (
    SnapshotRefusal, TargetBinding, apply_candidate_treatment, materialize_source_pair,
)


IMAGE = "fixture/runtime@sha256:" + "a" * 64
CID = "b" * 64


def ref(name):
    return {"producer": "synthetic-owner", "reference": name}


class CandidateTreatmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "git"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.org")
        (self.root / "skills").mkdir()
        (self.root / "skills/guide.txt").write_bytes(b"H0\n")
        (self.root / "other.txt").write_bytes(b"other fixed bytes\n")
        (self.root / "oracle.txt").write_bytes(b"protected oracle\n")
        self.git("add", ".")
        self.git("commit", "-qm", "synthetic source control")
        self.head = self.git("rev-parse", "HEAD")
        self.fixed = {key: ref(key) for key in
                      ("snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref")}
        self.fixed.update(
            causal_target_ref=ref("opaque:../../not-a-path"),
            allowlist=[{"surface": "skill_instruction",
                        "target_ref": ref("opaque:../../not-a-path"),
                        "expected_source_ref": ref("opaque-source-v1")}],
            protected_target_refs=[ref("protected-oracle")],
        )
        self.raw = json.dumps({
            "kind": "neoweaver/patch-proposal/v1",
            **{key: self.fixed[key] for key in
               ("snapshot_ref", "failure_ref", "allowlist_ref", "acceptance_ref")},
            "surface": "skill_instruction",
            "changes": [{"target_ref": self.fixed["causal_target_ref"],
                         "expected_source_ref": ref("opaque-source-v1"),
                         "replacement": "H1\n"}],
        }).encode()
        self.proposal = parse_proposal(self.raw, self.fixed)
        self.assertIs(type(self.proposal), ParsedProposal)
        change = self.proposal.changes[0]
        self.binding = TargetBinding(
            source_commit=self.head, snapshot_ref=self.proposal.snapshot_ref,
            target_ref=change.target_ref, expected_source_ref=change.expected_source_ref,
            relative_path="skills/guide.txt", expected_source=b"H0\n",
            protected_paths=("oracle.txt",),
        )
        self.task = ContainerTask(IMAGE, ("/bin/cat", "/workspace/skills/guide.txt"), 10)
        self.sequence = 0

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.root), *args], stderr=subprocess.PIPE,
        ).decode().strip()

    def stage(self):
        self.sequence += 1
        return materialize_source_pair(self.root, self.head, self.base / f"pair-{self.sequence}")

    def treat(self, pair=None):
        return apply_candidate_treatment(pair or self.stage(), self.proposal, self.binding)

    def transport(self, pair, arm):
        expected = b"H0\n" if arm == "baseline" else b"H1\n"
        source = pair.baseline.directory if arm == "baseline" else pair.candidate.directory

        def docker(command, **kwargs):
            self.assertEqual(command[1], "run")
            self.assertIn(f"type=bind,src={source},dst=/workspace,readonly", command)
            self.assertEqual((source / "skills/guide.txt").read_bytes(), expected)
            self.assertEqual((source / "other.txt").read_bytes(), b"other fixed bytes\n")
            self.assertEqual((source / "oracle.txt").read_bytes(), b"protected oracle\n")
            Path(command[command.index("--cidfile") + 1]).write_text(CID + "\n")
            kwargs["stdout"].write(expected)
            return subprocess.CompletedProcess(command, 0)

        destination = self.base / f"capture-{self.sequence}-{arm}"
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run", side_effect=docker) as process:
            capture = run_container_arm(pair, arm, self.task, destination)
        process.assert_called_once()
        self.assertEqual(capture.status, "EXIT_RECORDED")
        self.assertEqual(capture.stdout_path.read_bytes(), expected)
        self.assertEqual(capture.stderr_path.read_bytes(), b"")
        self.assertEqual(capture.effect_status, "unknown")
        self.assertFalse(capture.isolation_verified)
        self.assertIsNone(capture.task_completed)
        self.assertFalse(capture.authorizes_landing)
        return capture

    def inspect(self, pair, capture):
        source = pair.baseline.directory if capture.arm == "baseline" else pair.candidate.directory
        record = {
            "Id": CID, "Name": "/" + capture.container_name,
            "State": {"Status": "exited", "Running": False, "ExitCode": 0},
            "Config": {"Image": IMAGE, "User": "65534:65534", "Cmd": list(self.task.argv)},
            "HostConfig": {"NetworkMode": "none", "ReadonlyRootfs": True,
                           "Privileged": False, "AutoRemove": False, "CapDrop": ["ALL"],
                           "SecurityOpt": ["no-new-privileges"], "PidsLimit": 64,
                           "Memory": 512 * 1024 * 1024, "NanoCpus": 1_000_000_000},
            "Mounts": [{"Type": "bind", "Source": str(source),
                        "Destination": "/workspace", "RW": False}],
        }
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 0, json.dumps(record).encode())) as process:
            result = inspect_container_capture(capture, self.task, pair)
        process.assert_called_once()
        self.assertEqual(result.status, "CONFIG_AND_EXIT_MATCH")
        self.assertFalse(result.isolation_verified)
        self.assertIsNone(result.task_completed)
        self.assertFalse(result.authorizes_landing)
        return result

    def test_parsed_h1_reaches_transport_instead_of_source_changed_h0_stays_fixed(self):
        original = self.stage()
        treated = self.treat(original)
        self.assertEqual((treated.candidate.directory / "skills/guide.txt").read_bytes(), b"H1\n")
        self.assertEqual((treated.baseline.directory / "skills/guide.txt").read_bytes(), b"H0\n")
        self.assertEqual((self.root / "skills/guide.txt").read_bytes(), b"H0\n")
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(treated.baseline.manifest, original.baseline.manifest)
        self.assertNotEqual(treated.candidate.manifest.sha256, treated.baseline.manifest.sha256)
        for arm in ("baseline", "candidate"):
            capture = self.transport(treated, arm)
            self.assertEqual(capture.source_manifest_sha256, getattr(treated, arm).manifest.sha256)
            self.inspect(treated, capture)

    def test_manual_h1_without_application_remains_source_changed_zero_docker(self):
        pair = self.stage()
        (pair.candidate.directory / "skills/guide.txt").write_bytes(b"H1\n")
        with patch("neoweaver.execution.subprocess.run") as process, \
             self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(pair, "candidate", self.task, self.base / "refused")
        self.assertEqual(error.exception.condition, "source_changed")
        process.assert_not_called()
        self.assertFalse((self.base / "refused").exists())

    def test_wrong_binding_or_stale_expected_bytes_refuses_before_replacement(self):
        wrong = OwnerRef("synthetic-owner", "different")
        cases = [
            (replace(self.binding, source_commit="f" * 40), "source_binding_mismatch"),
            (replace(self.binding, snapshot_ref=wrong), "source_binding_mismatch"),
            (replace(self.binding, target_ref=wrong), "source_binding_mismatch"),
            (replace(self.binding, expected_source_ref=wrong), "source_binding_mismatch"),
            (replace(self.binding, expected_source=b"stale\n"), "stale_expected_source"),
            (replace(self.binding, relative_path="other.txt"), "stale_expected_source"),
        ]
        for binding, condition in cases:
            with self.subTest(binding=binding):
                pair = self.stage()
                with self.assertRaises(SnapshotRefusal) as error:
                    apply_candidate_treatment(pair, self.proposal, binding)
                self.assertEqual(error.exception.condition, condition)
                self.assertEqual((pair.candidate.directory / "skills/guide.txt").read_bytes(), b"H0\n")
                self.assertEqual((pair.candidate.directory / "other.txt").read_bytes(), b"other fixed bytes\n")

    def test_escape_noncanonical_and_untracked_bindings_refuse(self):
        for name in ("../outside", "/tmp/outside", "skills/../other.txt", "./other.txt",
                     "skills//guide.txt", "skills\\guide.txt", "", "bad\0path", "untracked.txt"):
            with self.subTest(name=name):
                pair = self.stage()
                with self.assertRaises(SnapshotRefusal):
                    apply_candidate_treatment(pair, self.proposal, replace(self.binding, relative_path=name))
                self.assertEqual((pair.candidate.directory / "skills/guide.txt").read_bytes(), b"H0\n")

    def test_original_protected_path_binding_prevents_reference_alias(self):
        pair = self.stage()
        binding = replace(self.binding, relative_path="oracle.txt", expected_source=b"protected oracle\n")
        with self.assertRaises(SnapshotRefusal) as error:
            apply_candidate_treatment(pair, self.proposal, binding)
        self.assertEqual(error.exception.condition, "protected_target")
        self.assertEqual((pair.candidate.directory / "oracle.txt").read_bytes(), b"protected oracle\n")

    def test_parser_refusal_cannot_be_applied(self):
        raw = json.loads(self.raw)
        raw["changes"][0]["target_ref"] = ref("protected-oracle")
        refusal = parse_proposal(json.dumps(raw).encode(), self.fixed)
        self.assertIs(type(refusal), DiagnosticRefusal)
        self.assertEqual(refusal.condition, "protected_target")
        pair = self.stage()
        with self.assertRaises(SnapshotRefusal):
            apply_candidate_treatment(pair, refusal, self.binding)
        self.assertEqual((pair.candidate.directory / "skills/guide.txt").read_bytes(), b"H0\n")

    def test_preexisting_drift_in_either_arm_is_not_healed_by_application(self):
        for arm in ("baseline", "candidate"):
            for target in ("skills/guide.txt", "other.txt"):
                with self.subTest(arm=arm, target=target):
                    pair = self.stage()
                    (getattr(pair, arm).directory / target).write_bytes(b"unauthorized\n")
                    with self.assertRaises(SnapshotRefusal) as error:
                        self.treat(pair)
                    self.assertEqual(error.exception.condition, "source_changed")
                    self.assertEqual((getattr(pair, arm).directory / target).read_bytes(), b"unauthorized\n")

    def test_target_and_parent_symlinks_refuse_before_application(self):
        for parent in (False, True):
            with self.subTest(parent=parent):
                pair = self.stage()
                location = pair.candidate.directory / ("skills" if parent else "skills/guide.txt")
                if parent:
                    location.rename(pair.candidate.directory / "moved")
                    location.symlink_to("moved", target_is_directory=True)
                else:
                    location.unlink()
                    location.symlink_to(pair.baseline.directory / "skills/guide.txt")
                with self.assertRaises(SnapshotRefusal):
                    self.treat(pair)
                self.assertEqual((pair.baseline.directory / "skills/guide.txt").read_bytes(), b"H0\n")

    def test_second_application_refuses_even_with_same_replacement(self):
        pair = self.treat()
        with self.assertRaises(SnapshotRefusal) as error:
            self.treat(pair)
        self.assertEqual(error.exception.condition, "treatment_already_applied")
        self.assertEqual((pair.candidate.directory / "skills/guide.txt").read_bytes(), b"H1\n")

    def test_hardlinked_target_refuses_before_writing_original_or_baseline(self):
        for original_arm in ("git", "baseline"):
            with self.subTest(original_arm=original_arm):
                pair = self.stage()
                original = self.root if original_arm == "git" else pair.baseline.directory
                target = pair.candidate.directory / "skills/guide.txt"
                target.unlink()
                os.link(original / "skills/guide.txt", target)
                with self.assertRaises(SnapshotRefusal) as error:
                    self.treat(pair)
                self.assertEqual(error.exception.condition, "target_hardlink")
                self.assertEqual(target.read_bytes(), b"H0\n")
                self.assertEqual((original / "skills/guide.txt").read_bytes(), b"H0\n")
                self.assertEqual(self.git("status", "--porcelain"), "")

    def test_later_target_non_target_or_baseline_drift_refuses_run_and_inspection(self):
        for arm in ("baseline", "candidate"):
            for target in ("skills/guide.txt", "other.txt"):
                with self.subTest(arm=arm, target=target):
                    pair = self.treat()
                    capture = self.transport(pair, "candidate")
                    (getattr(pair, arm).directory / target).write_bytes(b"later drift\n")
                    with patch("neoweaver.execution.subprocess.run") as process:
                        with self.assertRaises(ExecutionRefusal) as error:
                            run_container_arm(pair, "candidate", self.task, self.base / "refused")
                        self.assertEqual(error.exception.condition, "source_changed")
                        result = inspect_container_capture(capture, self.task, pair)
                    self.assertEqual(result.status, "INCONCLUSIVE")
                    self.assertEqual(result.reasons, ("source_changed",))
                    process.assert_not_called()

    def test_after_treatment_executable_mode_drift_refuses(self):
        pair = self.treat()
        (pair.candidate.directory / "skills/guide.txt").chmod(0o755)
        with patch("neoweaver.execution.subprocess.run") as process, \
             self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(pair, "candidate", self.task, self.base / "refused")
        self.assertEqual(error.exception.condition, "source_changed")
        process.assert_not_called()

    def test_capture_arm_manifest_and_log_substitution_refuse_before_inspect(self):
        pair = self.treat()
        capture = self.transport(pair, "candidate")
        for changed in (replace(capture, arm="baseline"),
                        replace(capture, source_manifest_sha256=pair.baseline.manifest.sha256),
                        replace(capture, arm="other")):
            with self.subTest(capture=changed), patch("neoweaver.execution.subprocess.run") as process:
                result = inspect_container_capture(changed, self.task, pair)
                self.assertEqual(result.status, "REFUSED")
                process.assert_not_called()
        capture.stdout_path.write_bytes(b"substituted capture\n")
        with patch("neoweaver.execution.subprocess.run") as process:
            result = inspect_container_capture(capture, self.task, pair)
        self.assertEqual(result.status, "REFUSED")
        self.assertEqual(result.reasons, ("capture_or_cid_mismatch",))
        process.assert_not_called()


if __name__ == "__main__":
    unittest.main()
