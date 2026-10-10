#!/usr/bin/env python3
"""Fixed real-device tasks for before/after comparisons of the tool layer.

Everything happens in the Settings app: open it and read the page, read ten pages while
scrolling, collect a list, type a long text into the search field and clear it again,
take one screenshot, return Home. No setting is changed. Only counts, sizes and timings
are printed, never page content.

This measures what the plugin controls: phone time, WDA requests and the bytes each
result puts into the model context. Model latency and the number of model round trips
belong to a real session; read them from pua_metrics there.
"""
import argparse
import importlib
import json
from pathlib import Path
import sys
import time

SETTINGS = "com.apple.Preferences"
IDLE_APPS = ("com.apple.springboard", SETTINGS)
SEARCH = {"type": "SearchField"}
# Mixed scripts and punctuation, the shapes that lose characters when typing is too fast.
PHRASE = "Real-device input benchmark 2026, punctuation: A-b_c/d+e=f; digits 1234567890."


class Benchmark:
    def __init__(self, runtime, module):
        self.runtime, self.module, self.error = runtime, module, module.WDAError
        self.tasks = []

    def call(self, task, tool, arguments, measured=True):
        """Run one tool; charge its time, requests and model-facing bytes to the task."""
        client = self.runtime.client
        before, started = client.metrics(), time.monotonic()
        try:
            data, error = self.runtime.call(tool, arguments), None
        except self.error as exc:
            data, error = {"error": exc.as_dict()}, exc.code
        seconds = time.monotonic() - started
        after = client.metrics()
        if measured:
            content = self.module.result_content(data)["content"]
            task["calls"] += 1
            task["seconds"] = round(task["seconds"] + seconds, 3)
            task["http_requests"] += after["retained_requests"] - before["retained_requests"]
            task["http_seconds"] = round(task["http_seconds"] + after.get("http_seconds", 0) - before.get("http_seconds", 0), 3)
            task["text_bytes"] += len(content[0]["text"].encode())
            task["image_bytes"] += sum(len(item["data"]) for item in content[1:])
            if error:
                task["errors"].append(error)
        return data

    def task(self, name):
        entry = {"task": name, "calls": 0, "seconds": 0.0, "http_requests": 0, "http_seconds": 0.0,
                 "text_bytes": 0, "image_bytes": 0, "errors": []}
        self.tasks.append(entry)
        return entry

    def scroll_back(self, count):
        for _ in range(count):
            self.call(None, "pua_swipe", {"direction": "down"}, measured=False)

    def ready(self):
        task = self.task("ready")
        data = self.call(task, "pua_ready", {"screenshot": False})
        return data.get("ready") is True

    def open_and_read(self):
        task = self.task("open_app_read_page")
        data = self.call(task, "pua_launch_app", {"bundle_id": SETTINGS, "observe": "tree"})
        task["nodes"] = data.get("observation", {}).get("total_nodes")

    def scroll_pages(self, pages):
        task = self.task(f"scroll_{pages}_pages")
        for _ in range(pages):
            self.call(task, "pua_swipe", {"direction": "up", "observe": "tree"})
        self.scroll_back(pages)

    def collect(self, pages):
        task = self.task("collect_list")
        data = self.call(task, "pua_collect_list", {"row_type": "Cell", "max_pages": pages})
        task["rows"] = len(data.get("rows", []))
        self.scroll_back(len(data.get("pages", [])))

    def long_text(self, characters):
        task = self.task(f"type_{characters}_characters")
        text = (PHRASE * (characters // len(PHRASE) + 1))[:characters]
        if not self.call(task, "pua_find", {"selector": SEARCH}).get("matches"):
            # Older layouts reveal the search field only after pulling the list down.
            self.call(task, "pua_swipe", {"direction": "down"})
            if not self.call(task, "pua_find", {"selector": SEARCH}).get("matches"):
                task["skipped"] = "no search field on this page"
                return
        started = time.monotonic()
        data = self.call(task, "pua_type_text", {"selector": SEARCH, "text": text, "verify": True})
        while data.get("input_complete") is False:
            data = self.call(task, "pua_type_text", {"continue_token": data["continue_token"]})
        task["exact_readback"] = data.get("exact_readback", False)
        if "error" in data:
            # A request that timed out leaves the phone typing; let it finish before cleaning up.
            time.sleep(max(0.0, characters / 30 + 3 - (time.monotonic() - started)))
        try:
            path = self.runtime.phone.target(SEARCH, editable=True)
            self.runtime.phone.post(path + "/clear", {})
        except self.error as exc:
            task["cleanup_error"] = exc.code

    def screenshot(self):
        task = self.task("screenshot")
        data = self.call(task, "pua_observe", {"mode": "screenshot"})
        image = data.get("image", {})
        task["image"] = {key: image[key] for key in ("mimeType", "width", "height") if key in image}

    def run(self, pages=10, characters=600, collect_pages=6):
        if not self.ready():
            return self.summary(complete=False)
        self.open_and_read()
        self.scroll_pages(pages)
        self.collect(collect_pages)
        self.long_text(characters)
        self.screenshot()
        self.call(None, "pua_press_button", {"name": "home"}, measured=False)
        return self.summary(complete=True)

    def summary(self, complete):
        totals = {key: round(sum(task[key] for task in self.tasks), 3)
                  for key in ("calls", "seconds", "http_requests", "http_seconds", "text_bytes", "image_bytes")}
        endpoints = {name: {key: value for key, value in entry.items() if key in ("count", "seconds", "bytes")}
                     for name, entry in self.runtime.client.metrics().get("endpoints", {}).items()}
        return {"plugin_version": getattr(self.module, "VERSION", "unknown"), "complete": complete,
                "tasks": self.tasks, "totals": totals, "http_endpoints": endpoints,
                "scope": "Tool layer on one device and page set. Model latency and round trips are not included."}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="Required: this operates the connected iPhone inside Settings.")
    parser.add_argument("--server-dir", default=str(Path(__file__).resolve().parents[1] / "server"),
                        help="server/ directory of the plugin version to measure")
    parser.add_argument("--pages", type=int, default=10)
    parser.add_argument("--characters", type=int, default=600)
    parser.add_argument("--state-dir")
    parser.add_argument("--url")
    args = parser.parse_args()
    if not args.run:
        parser.error("pass --run to operate the phone; without it nothing is done")
    if not 1 <= args.pages <= 20 or not 1 <= args.characters <= 10000:
        parser.error("--pages must be 1..20 and --characters 1..10000")
    sys.path.insert(0, str(Path(args.server_dir).resolve()))
    module = importlib.import_module("iphone_use")
    runtime = module.Runtime(args.state_dir, args.url)
    try:
        try:
            if runtime.client.request("GET", "/wda/locked").get("value") is not False:
                print(json.dumps({"complete": False, "blocked": "phone_locked"}))
                return 1
            foreground = (runtime.client.request("GET", "/wda/activeAppInfo").get("value") or {}).get("bundleId")
        except module.WDAError as exc:
            print(json.dumps({"complete": False, "blocked": exc.code}))
            return 1
        if foreground not in IDLE_APPS:
            # Another app in front may be someone's task in progress; do not take the phone from it.
            print(json.dumps({"complete": False, "blocked": "phone_in_use"}))
            return 1
        result = Benchmark(runtime, module).run(args.pages, args.characters)
    finally:
        runtime.close()
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
