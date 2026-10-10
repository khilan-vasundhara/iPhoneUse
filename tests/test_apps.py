import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import urllib.parse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
import wda_apps


class FakeSetup:
    config = {}


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.setup = FakeSetup()
        self.setup.config = {}
        self.catalog = wda_apps.AppCatalog(Path(self.temp.name), self.setup)

    @staticmethod
    def apple():
        return {"results": [
            {"kind": "software", "bundleId": "com.cmbchina.MPBBank", "trackId": 392899425,
             "trackName": "China Merchants Bank", "artistName": "China Merchants Bank"},
            {"kind": "software", "bundleId": "com.cmbchina.cmblife", "trackId": 398453262,
             "trackName": "Palm Life - CMB Credit Card", "artistName": "China Merchants Bank"}]}

    def test_catalog_exact_alias_and_case_preserving_bundle(self):
        with patch.object(wda_apps, "fetch_apple", side_effect=AssertionError("must stay offline")), patch.object(wda_apps.subprocess, "run", side_effect=AssertionError("must stay offline")):
            result = self.catalog.lookup("cmb", source="catalog", limit=1)
        self.assertTrue(result["ok"])
        self.assertEqual(result["candidates"][0]["bundle_id"], "com.cmbchina.MPBBank")
        self.assertFalse(result["candidates"][0]["installed_verified"])
        self.assertFalse(result["candidates"][0]["installation_checked"])

    def test_catalog_limits_deduplicates_and_never_guesses(self):
        rows = self.catalog.lookup("Bank", source="catalog", limit=2)
        self.assertEqual(len(rows["candidates"]), 2)
        self.assertGreater(rows["total_matches"], 2)
        self.assertEqual(self.catalog.lookup("unknown app 999", source="catalog")["candidates"], [])

    def test_catalog_has_evidence_for_every_reviewed_app(self):
        doc = json.loads(wda_apps.CATALOG_PATH.read_text())
        bundles = [row["bundleId"] for row in doc["apps"]]
        self.assertEqual(len(bundles), len(set(bundles)))
        self.assertGreaterEqual(len(bundles), 25)
        for row in doc["apps"]:
            self.assertTrue(wda_apps._valid_bundle(row["bundleId"]))
            self.assertTrue(wda_apps._api_url(row["sourceUrl"]))
            self.assertTrue(row["verifiedAt"])
            self.assertTrue(row["publisher"])
            self.assertTrue(row["aliases"])

    def test_parse_device_formats_and_invalid_entries(self):
        rows = wda_apps.AppCatalog.parse_installed({"result": {"apps": [
            {"name": "China Merchants Bank", "bundleIdentifier": "com.cmbchina.MPBBank"},
            {"displayName": "Palm Life", "bundleId": "com.cmbchina.cmblife"},
            {"name": "duplicate", "bundleID": "com.cmbchina.MPBBank"},
            {"name": "malformed", "bundleIdentifier": "../not-a-bundle"}, None]}})
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["installed_verified"] for row in rows))
        self.assertEqual(wda_apps.AppCatalog.parse_installed({"result": {"installedApps": {
            "com.example.app": {"displayName": "Example"}}}})[0]["bundle_id"], "com.example.app")
        self.assertEqual(wda_apps.AppCatalog.parse_installed({}), [])

    def _run_device(self, argv, **kwargs):
        self.assertIsInstance(argv, list)
        self.assertIn("--include-all-apps", argv)
        self.assertNotIn("shell", kwargs)
        path = Path(argv[argv.index("--json-output") + 1])
        path.write_text(json.dumps({"result": {"apps": [
            {"name": "China Merchants Bank", "bundleIdentifier": "com.cmbchina.MPBBank"},
            {"name": "Private unrelated app", "bundleIdentifier": "com.private.secret"}]}}))
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    def test_auto_prioritises_installed_and_caches_privately(self):
        self.setup.config = {"udid": "00008150-ABCDEF0123456789"}
        with patch.object(wda_apps.subprocess, "run", side_effect=self._run_device) as run, patch.object(wda_apps, "fetch_apple", side_effect=AssertionError("metadata already found")):
            result = self.catalog.lookup("CMB")
            again = self.catalog.lookup("CMB")
        self.assertEqual(run.call_count, 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["origin"], "installed")
        self.assertTrue(candidate["installed_verified"])
        self.assertEqual(candidate["track_id"], 392899425)
        self.assertEqual(candidate["publisher"], "\u62db\u5546\u94f6\u884c")
        self.assertEqual(len(result["candidates"]), 1)
        self.assertNotIn("com.private.secret", json.dumps(result))
        self.assertEqual(again["candidates"][0]["bundle_id"], candidate["bundle_id"])
        self.assertEqual(os.stat(Path(self.temp.name) / "apps-installed-cache.json").st_mode & 0o777, 0o600)

    def test_cache_expiry_and_device_change_refresh_inventory(self):
        self.setup.config = {"udid": "00008150-ABCDEF0123456789"}
        with patch.object(wda_apps.subprocess, "run", side_effect=self._run_device) as run:
            self.catalog.lookup("China Merchants Bank", source="installed")
            cache_path = Path(self.temp.name) / "apps-installed-cache.json"
            cache = json.loads(cache_path.read_text())
            cache["fetched_at"] = time.time() - 301
            cache_path.write_text(json.dumps(cache))
            self.catalog.lookup("China Merchants Bank", source="installed")
            self.setup.config = {"udid": "00008150-ABCDEF9876543210"}
            self.catalog.lookup("China Merchants Bank", source="installed")
        self.assertEqual(run.call_count, 3)

    def test_missing_device_and_invalid_udid_are_actionable_without_commands(self):
        with patch.object(wda_apps.subprocess, "run", side_effect=AssertionError("must not run")):
            result = self.catalog.lookup("China Merchants Bank", source="installed")
            self.setup.config = {"udid": "$(touch /tmp/unsafe)"}
            invalid = self.catalog.lookup("China Merchants Bank", source="installed")
        self.assertFalse(result["ok"])
        self.assertIn("pua_setup", result["warnings"][0])
        self.assertFalse(invalid["ok"])

    def test_failed_installed_probe_does_not_claim_catalog_app_installed(self):
        self.setup.config = {"udid": "00008150-ABCDEF0123456789"}
        with patch.object(wda_apps.subprocess, "run", side_effect=OSError("missing xcrun")):
            result = self.catalog.lookup("China Merchants Bank")
        self.assertTrue(result["ok"])
        self.assertFalse(result["candidates"][0]["installation_checked"])
        self.assertFalse(result["candidates"][0]["installed_verified"])
        self.assertTrue(result["warnings"])

    def test_apple_parsing_deduplicates_and_excludes_invalid_metadata(self):
        doc = self.apple()
        doc["results"].extend([doc["results"][0], None, {"bundleId": "com.fake.app", "trackId": True, "trackName": "Fake"},
                               {"kind": "song", "bundleId": "com.fake.song", "trackId": 1, "trackName": "Song"}])
        rows = wda_apps.parse_apple(doc, "cn", "https://itunes.apple.com/lookup?id=392899425")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["bundle_id"], "com.cmbchina.MPBBank")
        self.assertEqual(rows[0]["publisher"], "China Merchants Bank")

    def test_apple_query_escaping_cache_and_no_device_metadata_transmission(self):
        query = "Hiring & country=us $(anything)"
        with patch.object(wda_apps, "fetch_apple", return_value=self.apple()) as fetch:
            result = self.catalog.lookup(query, source="apple", limit=3)
            self.catalog.lookup(query, source="apple", limit=3)
        self.assertEqual(fetch.call_count, 1)
        params = urllib.parse.parse_qs(urllib.parse.urlsplit(fetch.call_args.args[0]).query)
        self.assertEqual(params["term"], [query])
        self.assertEqual(params["country"], ["cn"])
        self.assertEqual(set(params), {"term", "country", "media", "entity", "limit"})
        self.assertFalse(result["candidates"][0]["installed_verified"])
        self.assertEqual(os.stat(Path(self.temp.name) / "apps-apple-cache.json").st_mode & 0o777, 0o600)

    def test_auto_unknown_app_uses_apple_once(self):
        with patch.object(wda_apps, "fetch_apple", return_value=self.apple()) as fetch:
            result = self.catalog.lookup("Unknown Name")
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(result["searched_sources"], ["installed", "catalog", "apple"])

    def test_apple_rate_limit_does_not_make_another_request(self):
        (Path(self.temp.name) / "apps-apple-request-times.json").write_text(json.dumps([time.time()] * 18))
        with patch.object(wda_apps, "fetch_apple", side_effect=AssertionError("must not request")):
            result = self.catalog.lookup("China Merchants Bank", source="apple")
        self.assertFalse(result["ok"])
        self.assertIn("budget", result["warnings"][0])

    def test_failed_explicit_lookup_is_mcp_error_but_empty_success_is_not(self):
        from iphone_use import result_content
        missing = self.catalog.lookup("China Merchants Bank", source="installed")
        self.assertFalse(missing["ok"])
        self.assertTrue(result_content(missing)["isError"])
        self.assertEqual(missing["error"]["code"], "app_lookup_unavailable")
        with patch.object(wda_apps, "fetch_apple", side_effect=OSError("offline")):
            failed = self.catalog.lookup("A missing app", source="apple")
        self.assertTrue(result_content(failed)["isError"])
        self.assertFalse(failed["error"]["uncertain"])
        with patch.object(wda_apps, "fetch_apple", return_value={"results": []}):
            empty = self.catalog.lookup("Different absent app", source="apple")
        self.assertTrue(empty["ok"])
        self.assertFalse(result_content(empty)["isError"])
        self.assertEqual(empty["candidates"], [])
        with patch.object(wda_apps, "fetch_apple", return_value={"results": []}):
            auto_empty = self.catalog.lookup("Auto absent app", source="auto")
        self.assertTrue(auto_empty["ok"])
        self.assertFalse(result_content(auto_empty)["isError"])
        self.assertTrue(auto_empty["warnings"])
        self.assertEqual(auto_empty["candidates"], [])

    def test_unsafe_network_destinations_and_redirects_rejected(self):
        for url in ("http://itunes.apple.com/search", "https://example.com/search", "https://itunes.apple.com.evil.test/search",
                    "https://user:password@itunes.apple.com/search", "https://itunes.apple.com/search#fragment"):
            with self.assertRaises(ValueError):
                wda_apps.fetch_apple(url)
        with self.assertRaises(ValueError):
            wda_apps._AppleRedirects().redirect_request(None, None, 302, "", {}, "https://example.com/search")

    def test_input_bounds(self):
        for kwargs in ({"query": ""}, {"query": "x" * 101}, {"query": "x", "country": "china"},
                       {"query": "x", "source": "shell"}, {"query": "x", "limit": True}, {"query": "x", "limit": 31}):
            self.assertFalse(self.catalog.lookup(**kwargs)["ok"])

    def test_state_inside_git_rejected(self):
        root = Path(self.temp.name) / "repo"
        root.mkdir()
        (root / ".git").mkdir()
        with self.assertRaises(ValueError):
            wda_apps.AppCatalog(root / "state", self.setup)


if __name__ == "__main__":
    unittest.main()
