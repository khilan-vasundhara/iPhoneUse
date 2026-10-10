import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from wda_setup import state_directory
from iphone_use import Runtime


class StateDirectoryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.current = self.home / '.local/share/iphone-use'
        self.previous = self.home / '.local/share/iphone-use-wda'
        for patcher in [patch('wda_setup.Path.home', return_value=self.home),
                        patch.dict(os.environ, {}, clear=True)]:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_fresh_install_uses_new_identity(self):
        self.assertEqual(state_directory(), self.current)

    def test_upgrade_preserves_old_configuration_and_runtime_uses_same_directory(self):
        self.previous.mkdir(parents=True)
        (self.previous / 'config.json').write_text('{"local_port": 19100}')
        self.assertEqual(state_directory(), self.previous)
        runtime = Runtime()
        self.addCleanup(runtime.client.close)
        self.assertEqual(runtime.state_dir, self.previous.resolve())
        self.assertEqual(runtime.base_url, 'http://127.0.0.1:19100')
        self.assertEqual(runtime.setup_manager.state_dir, self.previous.resolve())
        self.assertFalse(self.current.exists())

    def test_current_directory_takes_priority_when_both_exist(self):
        self.previous.mkdir(parents=True)
        (self.previous / 'config.json').write_text('{}')
        self.current.mkdir()
        self.assertEqual(state_directory(), self.current)

    def test_explicit_and_environment_directory_priority(self):
        with patch.dict(os.environ, {'IPHONE_USE_STATE_DIR': '/new', 'WDA_STATE_DIR': '/old'}):
            self.assertEqual(state_directory('/explicit'), Path('/explicit'))
            self.assertEqual(state_directory(), Path('/new'))
        with patch.dict(os.environ, {'WDA_STATE_DIR': '/old'}):
            self.assertEqual(state_directory(), Path('/old'))

    def test_unconfigured_old_directory_is_not_reused(self):
        self.previous.mkdir(parents=True)
        self.assertEqual(state_directory(), self.current)


if __name__ == '__main__':
    unittest.main()
