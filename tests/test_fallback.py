import contextlib
import fcntl
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from iphone_use import Runtime
from wda_client import WDAError
from wda_controller import PhoneController
from test_controller import FakeWDA

spec = importlib.util.spec_from_file_location("phone_fallback", ROOT / "scripts" / "phone.py")
fallback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback)


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.client = FakeWDA()
        self.closed = False
        self.setup_manager = None

    def make_runtime(self, state_dir, base_url):
        runtime = Runtime(state_dir, base_url)
        runtime.client.close()
        self.client.close = lambda: setattr(self, "closed", True)
        runtime.client = self.client
        runtime.phone = PhoneController(self.client, state_dir)
        if self.setup_manager is not None:
            runtime.setup_manager = self.setup_manager
        return runtime

    def invoke(self, arguments="{}", tool="pua_press_button"):
        output = io.StringIO()
        argv = ["phone.py", tool, arguments, "--state-dir", self.directory.name]
        with patch.object(fallback, "Runtime", side_effect=self.make_runtime) as create, \
                patch.object(sys, "argv", argv), contextlib.redirect_stdout(output):
            status = fallback.main()
        return status, json.loads(output.getvalue()), create.call_count

    def test_fallback_home_defaults_to_one_action_without_foreground_readback(self):
        status, result, _ = self.invoke('{"name":"home"}')
        self.assertEqual(status, 0)
        self.assertTrue(result["action_executed"])
        self.assertFalse(result["foreground_verified"])
        self.assertTrue(result["verification_deferred"])
        self.assertFalse(any(path == "/wda/activeAppInfo" for _, path, _ in self.client.calls))
        self.assertEqual([path for _, path, _ in self.client.actions()], ["/wda/homescreen"])
        self.assertTrue(self.closed)

    def test_fallback_home_explicit_check_uses_same_verified_controller(self):
        status, result, _ = self.invoke('{"name":"home","verify":true}')
        self.assertEqual(status, 0)
        self.assertTrue(result["foreground_verified"])
        self.assertEqual([path for _, path, _ in self.client.actions()], ["/wda/homescreen"])
        self.assertTrue(self.closed)
        lock = Path(self.directory.name) / "operation.lock"
        self.assertEqual(lock.stat().st_mode & 0o777, 0o600)

    def test_cli_catalog_resolves_verified_bundle_without_a_device_or_wda_server(self):
        process = subprocess.run([
            sys.executable, str(ROOT / "scripts" / "phone.py"), "pua_apps",
            '{"query":"China Merchants Bank","source":"catalog"}',
            "--state-dir", self.directory.name, "--url", "http://127.0.0.1:1",
        ], capture_output=True, text=True, encoding="utf-8", timeout=5)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        result = json.loads(process.stdout)
        self.assertTrue(result["ok"])
        self.assertEqual(result["searched_sources"], ["catalog"])
        candidate = result["candidates"][0]
        self.assertEqual(candidate["bundle_id"], "com.cmbchina.MPBBank")
        self.assertEqual(candidate["publisher"], "\u62db\u5546\u94f6\u884c")
        self.assertFalse(candidate["installed_verified"])
        self.assertTrue(candidate["source_url"].startswith("https://itunes.apple.com/lookup?"))

    def test_fallback_cannot_bypass_another_operation_lock(self):
        with (Path(self.directory.name) / "operation.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            status, result, _ = self.invoke('{"name":"home","observe":"none"}')
        self.assertEqual(status, 1)
        self.assertEqual(result["error"]["code"], "device_busy")
        self.assertEqual(self.client.calls, [])
        self.assertTrue(self.closed)

    def test_fallback_cannot_bypass_locked_phone(self):
        self.client.locked = True
        status, result, _ = self.invoke('{"name":"home","observe":"none"}')
        self.assertEqual(status, 1)
        self.assertEqual(result["error"]["code"], "phone_locked")
        self.assertEqual(self.client.actions(), [])
        self.assertTrue(self.closed)

    def test_fallback_does_not_replay_an_uncertain_mutation(self):
        self.client.home_error = WDAError("action_uncertain", "Response lost after Home", uncertain=True)
        status, result, _ = self.invoke('{"name":"home","observe":"none"}')
        self.assertEqual(status, 1)
        self.assertTrue(result["error"]["uncertain"])
        self.assertEqual([path for _, path, _ in self.client.actions()], ["/wda/homescreen"])
        self.assertTrue(self.closed)

    def test_fallback_validates_schema_before_phone_access(self):
        for arguments in ('[]', '{"name":"home","extra":true}'):
            with self.subTest(arguments=arguments):
                status, result, _ = self.invoke(arguments)
                self.assertEqual(status, 1)
                self.assertEqual(result["error"]["code"], "invalid_argument")
                self.assertEqual(self.client.calls, [])
                self.assertTrue(self.closed)

    def test_fallback_rejects_malformed_and_nonfinite_json_before_runtime(self):
        for arguments in ('{broken', '{"x":NaN}', '{"x":Infinity}'):
            with self.subTest(arguments=arguments):
                status, result, creates = self.invoke(arguments)
                self.assertEqual(status, 1)
                self.assertEqual(result["error"]["code"], "invalid_argument")
                self.assertEqual(creates, 0)
                self.assertEqual(self.client.calls, [])

    def test_fallback_ready_diagnostic_state_is_nonzero_without_error_wrapper(self):
        self.client.app = "local.pid.0"
        self.setup_manager = Mock()
        self.setup_manager.pending_recovery.return_value = None
        status, result, _ = self.invoke('{"screenshot":false,"recover":false}', tool="pua_ready")
        self.assertEqual(status, 1)
        self.assertFalse(result["ready"])
        self.assertEqual(result["state"], "recovery_required")
        self.assertEqual(result["reason"], "recovery_disabled")
        self.assertNotIn("error", result)
        self.assertNotIn("proof", result)
        self.setup_manager.recover.assert_not_called()
        self.assertTrue(self.closed)
        self.assertEqual([path for _, path, _ in self.client.actions() if path != "/session"], [])

    def test_fallback_ready_pending_recovery_is_nonzero_without_error_wrapper(self):
        self.client.app = "local.pid.0"
        self.setup_manager = Mock()
        self.setup_manager.pending_recovery.return_value = {"job_id": "existing", "state": "restarting"}
        status, result, _ = self.invoke('{"screenshot":false,"recover":false}', tool="pua_ready")
        self.assertEqual(status, 1)
        self.assertEqual(result["state"], "recovering")
        self.assertEqual(result["recovery"]["next_arguments"], {"screenshot": False, "recover": False})
        self.assertNotIn("error", result)
        self.setup_manager.recover.assert_not_called()
        self.assertTrue(self.closed)

    def test_fallback_healthy_ready_returns_zero_and_proof(self):
        self.setup_manager = Mock()
        self.setup_manager.mirroring_running.return_value = False
        self.setup_manager.pending_recovery.return_value = None
        status, result, _ = self.invoke('{"screenshot":false,"recover":false}', tool="pua_ready")
        self.assertEqual(status, 0)
        self.assertTrue(result["ready"])
        self.assertEqual(result["state"], "ready")
        self.assertTrue(result["proof"]["foreground_resolved"])
        self.setup_manager.recover.assert_not_called()
        self.assertTrue(self.closed)

    def test_fallback_ready_requires_explicit_true(self):
        for data in ({}, {"ready": 1}, {"ready": "true"}):
            with self.subTest(data=data), patch.object(Runtime, "call", return_value=data):
                status, result, _ = self.invoke('{}', tool="pua_ready")
                self.assertEqual(status, 1)
                self.assertEqual(result, data)
                self.assertTrue(self.closed)
                self.assertEqual(self.client.calls, [])


if __name__ == "__main__":
    unittest.main()
