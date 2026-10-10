import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
import iphone_use
from wda_controller import PhoneController
from test_controller import FakeWDA, node

spec = importlib.util.spec_from_file_location("phone_benchmark", ROOT / "scripts" / "benchmark.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.runtime = iphone_use.Runtime(self.directory.name)
        self.addCleanup(self.runtime.close)
        self.client = FakeWDA()
        self.client.close = lambda: None
        self.runtime.client = self.client
        self.runtime.phone = PhoneController(self.client, self.directory.name)
        self.client.source_pages = [[node(f"Private row {page}", y=350)] for page in range(40)]
        patcher = patch.object(self.runtime.setup_manager, "mirroring_running", return_value=False)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_fixed_tasks_report_sizes_and_timings_without_page_content(self):
        result = benchmark.Benchmark(self.runtime, iphone_use).run(pages=3, characters=450, collect_pages=2)
        self.assertTrue(result["complete"])
        self.assertEqual(result["plugin_version"], iphone_use.VERSION)
        tasks = {task["task"]: task for task in result["tasks"]}
        self.assertEqual(list(tasks), ["ready", "open_app_read_page", "scroll_3_pages", "collect_list",
                                       "type_450_characters", "screenshot"])
        self.assertEqual(tasks["scroll_3_pages"]["calls"], 3)
        self.assertTrue(tasks["type_450_characters"]["exact_readback"])
        self.assertEqual(tasks["type_450_characters"]["errors"], [])
        self.assertGreater(tasks["screenshot"]["image_bytes"], 0)
        self.assertEqual(result["totals"]["text_bytes"], sum(task["text_bytes"] for task in result["tasks"]))
        self.assertGreater(result["totals"]["http_requests"], 0)
        printed = json.dumps(result, ensure_ascii=False)
        for private in ("Private row", "Target", benchmark.PHRASE[:6], "com.example"):
            self.assertNotIn(private, printed)
        # The search text is cleared and the phone is left on the Home screen.
        self.assertEqual(self.client.elements[0]["value"], "")
        self.assertEqual(self.client.actions()[-1][1], "/wda/homescreen")

    def test_unfinished_long_input_is_continued_inside_the_task(self):
        self.runtime.phone.call_budget = 0
        result = benchmark.Benchmark(self.runtime, iphone_use).run(pages=1, characters=450, collect_pages=1)
        task = next(task for task in result["tasks"] if task["task"] == "type_450_characters")
        self.assertTrue(task["exact_readback"])
        self.assertEqual(task["calls"], 4)

    def test_not_ready_phone_is_left_alone(self):
        self.client.locked = True
        result = benchmark.Benchmark(self.runtime, iphone_use).run()
        self.assertFalse(result["complete"])
        self.assertEqual([task["task"] for task in result["tasks"]], ["ready"])
        self.assertEqual(self.client.actions(), [])

    def test_command_line_does_nothing_without_run(self):
        with patch.object(sys, "argv", ["benchmark.py"]), self.assertRaises(SystemExit) as stopped, \
                patch.object(sys, "stderr"):
            benchmark.main()
        self.assertEqual(stopped.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
