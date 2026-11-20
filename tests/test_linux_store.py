"""Linux built-in asset update regression tests. Run with python -B tests/test_linux_store.py."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "linux"))
from claudia import store


class ResourceUpdateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        data = root / "data"
        assets = data / "characters"
        override = patch.multiple(
            store, INSTALL=root / "install", DATA=data, CHARACTERS=assets, STATE=data / "state",
        )
        override.start()
        self.addCleanup(override.stop)
        self.source = store.INSTALL / "characters" / "claude"
        self.active = assets / "claude"
        self.work = data / "builtin-resource-sync" / "claude"
        self.source.mkdir(parents=True)
        self.active.mkdir(parents=True)
        (self.source / "new.webp").write_bytes(b"new install")
        (self.active / "old.webp").write_bytes(b"user's previous asset")

    def test_failed_promotion_restores_previous_and_can_retry(self):
        replace = store.os.replace

        def fail_promotion(source, destination):
            if source == self.work / "next":
                raise OSError("injected failure after backing up active assets")
            replace(source, destination)

        with patch.object(store.os, "replace", side_effect=fail_promotion):
            store.sync_resources()
        self.assertEqual((self.active / "old.webp").read_bytes(), b"user's previous asset")
        self.assertFalse((self.work / "previous").exists())

        store.sync_resources()
        self.assertEqual((self.active / "new.webp").read_bytes(), b"new install")
        self.assertFalse((self.active / "old.webp").exists())
        self.assertFalse((self.work / "next").exists())
        self.assertFalse((self.work / "previous").exists())

    def test_interrupted_update_recovers_before_trying_to_copy_again(self):
        self.work.mkdir(parents=True)
        self.active.rename(self.work / "previous")
        (self.work / "next").mkdir()
        (self.work / "next" / "partial.webp").write_bytes(b"incomplete")

        with patch.object(store, "_copy_dir", side_effect=OSError("injected copy failure")):
            store.sync_resources()
        self.assertEqual((self.active / "old.webp").read_bytes(), b"user's previous asset")
        self.assertFalse((self.work / "next").exists())
        self.assertFalse((self.work / "previous").exists())


if __name__ == "__main__":
    unittest.main()
