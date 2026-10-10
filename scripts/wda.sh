#!/bin/sh
set -eu
task_plugin_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$task_plugin_root/server/wda_setup.py" "$@"
