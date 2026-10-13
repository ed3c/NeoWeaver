"""A5.2 Docker transport checks, not Docker isolation or native task proof."""
from dataclasses import replace
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from neoweaver.execution import ContainerTask, ExecutionRefusal, run_container_arm
from neoweaver.snapshot import StagedSourcePair


IMAGE = "neoweaver/runtime@sha256:" + "a" * 64


class ContainerExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.source = self.dir / "source"
        self.source.mkdir()
        self.baseline = self.source / "baseline"
        self.candidate = self.source / "candidate"
        for folder in (self.baseline, self.candidate):
            folder.mkdir()
            (folder / "code.txt").write_bytes(b"pinned\n")
        import hashlib
        checksum = hashlib.sha256(b"pinned\n").hexdigest()
        self.pair = StagedSourcePair("a" * 40, "b" * 40, "c" * 64,
                                     (("code.txt", checksum),), self.baseline, self.candidate)
        self.out = self.dir / "capture"
        self.task = ContainerTask(IMAGE, ("/usr/bin/python3", "-B", "task.py"), 30)

    def run_fake_docker(self, arm="baseline", task=None):
        seen = []
        def execute(command, **kwargs):
            seen.append((command, kwargs))
            kwargs["stdout"].write(b"observed stdout")
            kwargs["stderr"].write(b"observed stderr")
            return subprocess.CompletedProcess(command, 0)
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run", side_effect=execute):
            receipt = run_container_arm(self.pair, arm, task or self.task, self.out)
        return receipt, seen

    def test_selected_pinned_command_uses_bounded_docker_flags_and_persists_real_response(self):
        result, seen = self.run_fake_docker()
        argv, opts = seen[0]
        self.assertEqual(result.status, "EXIT_RECORDED")
        self.assertEqual(self.out.stat().st_mode & 0o077, 0)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout_path.read_bytes(), b"observed stdout")
        self.assertEqual(result.stderr_path.read_bytes(), b"observed stderr")
        self.assertFalse(result.isolation_verified)
        self.assertIsNone(result.task_completed)
        self.assertEqual(result.effect_status, "unknown")
        self.assertFalse(result.authorizes_landing)
        for flag in ("--network=none", "--read-only", "--cap-drop=ALL",
                     "--security-opt=no-new-privileges", "--pull=never", "--pids-limit=64"):
            self.assertIn(flag, argv)
        self.assertIn("type=bind,src=" + str(self.baseline.resolve()) + ",dst=/workspace,readonly", argv)
        self.assertEqual(argv[-3:], list(self.task.argv))
        self.assertEqual(opts["timeout"], 40)
        self.assertNotIn("shell", opts)
        self.assertNotIn("capture_output", opts)

    def test_unknown_docker_outcome_preserves_container_name_and_does_not_retry(self):
        def timeout(command, **kwargs):
            kwargs["stdout"].write(b"partial")
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run", side_effect=timeout) as launch:
            output = run_container_arm(self.pair, "candidate", self.task, self.out)
        self.assertEqual(launch.call_count, 1)
        self.assertEqual(output.status, "UNKNOWN_OUTCOME")
        self.assertEqual(output.stdout_path.read_bytes(), b"partial")
        self.assertIsNone(output.exit_code)
        self.assertTrue(output.container_name.startswith("nw-replay-"))
        self.assertIsNone(output.task_completed)

    def test_docker_backend_rejection_is_not_task_failure(self):
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             patch("neoweaver.execution.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 125)):
            result = run_container_arm(self.pair, "baseline", self.task, self.out)
        self.assertEqual(result.status, "BACKEND_REFUSED")
        self.assertIsNone(result.task_completed)

    def test_no_docker_refuses_without_creating_evidence(self):
        with patch("neoweaver.execution.shutil.which", return_value=None), \
             self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(self.pair, "baseline", self.task, self.out)
        self.assertEqual(error.exception.condition, "docker_unavailable")
        self.assertFalse(self.out.exists())

    def test_unpinned_image_invalid_argv_and_timeout_refuse(self):
        tasks = [
            ContainerTask("ubuntu:latest", self.task.argv, 30),
            ContainerTask(IMAGE, ("",), 30),
            ContainerTask(IMAGE, ("python", "bad\0argument"), 30),
            ContainerTask(IMAGE, ("python",), 0),
            ContainerTask(IMAGE, ("python",), 301),
        ]
        for item in tasks:
            with self.subTest(item=item), self.assertRaises(ExecutionRefusal):
                run_container_arm(self.pair, "baseline", item, self.out)
        self.assertFalse(self.out.exists())

    def test_changed_source_rejects_before_container_start(self):
        (self.candidate / "code.txt").write_text("changed\n")
        with patch("neoweaver.execution.subprocess.run") as run, \
             self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(self.pair, "candidate", self.task, self.out)
        self.assertEqual(error.exception.condition, "source_changed")
        run.assert_not_called()

    def test_symlink_and_unexpected_files_refuse(self):
        (self.baseline / "evil").symlink_to("code.txt")
        with self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(self.pair, "baseline", self.task, self.out)
        self.assertEqual(error.exception.condition, "source_symlink")
        (self.baseline / "evil").unlink()
        (self.baseline / "unexpected.txt").write_text("surprise")
        with self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(self.pair, "baseline", self.task, self.out)
        self.assertEqual(error.exception.condition, "unexpected_source_file")

    def test_existing_capture_is_not_overwritten(self):
        self.out.mkdir()
        (self.out / "receipt").write_text("original")
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             self.assertRaises(ExecutionRefusal) as error:
            run_container_arm(self.pair, "baseline", self.task, self.out)
        self.assertEqual(error.exception.condition, "evidence_dir_exists_or_overlaps")
        self.assertEqual((self.out / "receipt").read_text(), "original")

    def test_reused_stage_and_evidence_inside_opposite_stage_refuse(self):
        aliased = replace(self.pair, candidate_dir=self.baseline)
        with self.assertRaises(ExecutionRefusal) as err:
            run_container_arm(aliased, "baseline", self.task, self.out)
        self.assertEqual(err.exception.condition, "reused_source_directory")
        with patch("neoweaver.execution.shutil.which", return_value="/usr/bin/true"), \
             self.assertRaises(ExecutionRefusal) as err:
            run_container_arm(self.pair, "baseline", self.task, self.candidate / "captured")
        self.assertEqual(err.exception.condition, "evidence_dir_exists_or_overlaps")

    def test_neither_completed_exit_nor_fake_docker_qualifies_for_original_pair_verifier(self):
        result, _ = self.run_fake_docker()
        self.assertNotEqual(result.status, "NATIVE_REPLAY_PASS")
        self.assertFalse(hasattr(result, "sandbox_ref"))
        self.assertIsNone(result.task_completed)
        self.assertFalse(result.isolation_verified)


if __name__ == "__main__":
    unittest.main()
