"""Real temporary Git-object controls for source-only A5 staging."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from neoweaver.snapshot import SnapshotRefusal, materialize_source_pair


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode().strip()


class SourceSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name).resolve()
        self.root = base / "source"
        self.root.mkdir()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.org")
        (self.root / "pkg").mkdir()
        (self.root / "pkg" / "module.py").write_text("MESSAGE = 'pinned'\n")
        (self.root / "README.md").write_text("Test source\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.target = base / "staged"

    def test_actual_git_commit_produces_distinct_byte_equal_source_copies(self):
        result = materialize_source_pair(self.root, self.head, self.target)
        self.assertEqual(result.status, "FILESYSTEM_COPIES_ONLY")
        self.assertEqual(result.commit, self.head)
        self.assertEqual(result.tree, git(self.root, "rev-parse", "HEAD^{tree}"))
        self.assertNotEqual(result.baseline.directory, result.candidate.directory)
        self.assertFalse(result.authorizes_execution)
        self.assertFalse(result.authorizes_landing)
        for entry in result.baseline.manifest.files:
            name, digest = entry.path, entry.sha256
            a = (result.baseline.directory / name).read_bytes()
            b = (result.candidate.directory / name).read_bytes()
            self.assertEqual(a, b)
            self.assertEqual(hashlib.sha256(a).hexdigest(), digest)
        (result.candidate.directory / "README.md").write_text("changed\n")
        self.assertEqual((result.baseline.directory / "README.md").read_text(), "Test source\n")
        self.assertEqual((self.root / "README.md").read_text(), "Test source\n")

    def test_wrong_head_and_invalid_sha_stop_before_destination_write(self):
        for commit, expected in (("abc", "invalid_commit"), ("f" * 40, "stale_source_head")):
            with self.subTest(commit=commit), self.assertRaises(SnapshotRefusal) as err:
                materialize_source_pair(self.root, commit, self.target)
            self.assertEqual(err.exception.condition, expected)
            self.assertFalse(self.target.exists())

    def test_dirty_source_refuses_before_writing(self):
        (self.root / "README.md").write_text("dirty\n")
        with self.assertRaises(SnapshotRefusal) as err:
            materialize_source_pair(self.root, self.head, self.target)
        self.assertEqual(err.exception.condition, "dirty_source")
        self.assertFalse(self.target.exists())

    def test_existing_destination_refuses_without_overwriting(self):
        self.target.mkdir()
        (self.target / "receipt").write_text("owner-data")
        with self.assertRaises(SnapshotRefusal) as err:
            materialize_source_pair(self.root, self.head, self.target)
        self.assertEqual(err.exception.condition, "destination_exists")
        self.assertEqual((self.target / "receipt").read_text(), "owner-data")

    def test_destination_inside_or_above_source_refuses(self):
        for directory in (self.root / "copies", self.root.parent):
            with self.subTest(directory=directory), self.assertRaises(SnapshotRefusal) as err:
                materialize_source_pair(self.root, self.head, directory)
            self.assertEqual(err.exception.condition, "unsafe_destination")

    def test_symlink_in_source_refuses_before_materialization(self):
        (self.root / "unsafe-link").symlink_to("README.md")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "symlink")
        updated = git(self.root, "rev-parse", "HEAD")
        with self.assertRaises(SnapshotRefusal) as err:
            materialize_source_pair(self.root, updated, self.target)
        self.assertEqual(err.exception.condition, "unsupported_git_tree_entry")
        self.assertFalse(self.target.exists())

    def test_export_ignore_does_not_omit_original_git_blobs(self):
        (self.root / ".gitattributes").write_text("README.md export-ignore\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "attribute")
        updated = git(self.root, "rev-parse", "HEAD")
        pair = materialize_source_pair(self.root, updated, self.target)
        self.assertIn("README.md", {entry.path for entry in pair.baseline.manifest.files})
        self.assertEqual((pair.candidate.directory / "README.md").read_text(), "Test source\n")

    def test_export_subst_does_not_mutate_tracked_blobs(self):
        (self.root / ".gitattributes").write_text("README.md export-subst\n")
        (self.root / "README.md").write_text("$Format:%H$\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "attribute")
        updated = git(self.root, "rev-parse", "HEAD")
        pair = materialize_source_pair(self.root, updated, self.target)
        self.assertEqual((pair.baseline.directory / "README.md").read_text(), "$Format:%H$\n")

    def test_nested_git_directory_is_not_accepted_as_source_root(self):
        with self.assertRaises(SnapshotRefusal) as error:
            materialize_source_pair(self.root / "pkg", self.head, self.target)
        self.assertEqual(error.exception.condition, "not_git_root")

    def test_destination_symlink_is_refused_without_writing_target(self):
        hidden = self.root.parent / "hidden"
        self.target.symlink_to(hidden, target_is_directory=True)
        with self.assertRaises(SnapshotRefusal) as error:
            materialize_source_pair(self.root, self.head, self.target)
        self.assertEqual(error.exception.condition, "unsafe_destination")
        self.assertFalse(hidden.exists())

    def test_staged_source_is_not_a_runner_or_native_result(self):
        result = materialize_source_pair(self.root, self.head, self.target)
        self.assertFalse(hasattr(result, "completed"))
        self.assertFalse(hasattr(result, "effect_status"))
        self.assertFalse(hasattr(result, "oracle_pass"))


if __name__ == "__main__":
    unittest.main()
