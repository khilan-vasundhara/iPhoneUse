# MCP Failures and Code Calls

Prefer calling the wrapped tools, run routine actions optimistically by default, and judge the previous action along the way when the next step needs information. A missing tool binding, a host forwarding error, or a confirmed wrapper problem does not mean PUA is unavailable; you can use the plugin's code entry for the same authorized action. The code fallback keeps the same config, session, operation lock, and explicit exception handling, and adds no per-step verification.

The regular edition provides 17 model tools; first check the tool bindings actually callable this turn (use ALL_TOOLS or tool search when supported), and do not infer from tools/list, docs, or earlier chats alone that they are bound. The 0.1.6 install.sh also registers a standard MCP with the same names, to keep the shared Codex plugin description budget from hiding tools and to preserve the full batch schema. After installing a new version, reconnect the chat; only when a needed tool is actually still missing, continue with the code entry below, and do not by default turn every wrapped operation into a CLI call.

## Tell the error apart first

- Schema / argument error: fix the call once per argument_path, unknown_fields, and allowed_fields. action_executed=false means the action was not sent; if the MCP binding is still unavailable you can use the code entry; do not silently ignore unknown arguments.
- `device_busy`: another operation holds the shared lock; wait for it to finish, and do not create another Runtime config or state directory to bypass the lock.
- `stale_observation`: the provided ID does not belong to the current Runtime, or the app / viewport context has changed. Locate with the fresh information the next step needs; do not add image reads for whole-image hashes, text/number refreshes, or a fixed 30-second expiry; the ID is optional context, not a required permit for every coordinate action.
- UI anomalies always start with the screenshot: selector / focus failure, no tappable target after scrolling, no progress, region blocked, scroll context changed, input mismatch, or the expected page not appearing. First look at the screenshot already attached to the result, take one screenshot only if it is missing, and then choose a visible target, handle the overlay, or decide whether to keep scrolling; do not first re-read the tree, change labels, or retry unchanged. `tap_point` / candidates do not prove the target is unobstructed; for input, first tap a visible input field and then type_text, and if focus still fails, reselect the point. A match stacked at the same position or with only one on screen is determined by the tool itself.
- `input_continuation_expired`: the long-text continuation has expired, and nothing was typed this time. Read the field's actual text and use `replace=false` to add only the missing part.
- `occluded_target` / `offscreen_target`: the target tap was not executed, so you cannot infer that an unexecuted tap opened an overlay. For `occluded_target`, judge by the attached screenshot: if the target is visible tap it by coordinates at `tap_point`, and if truly covered deal with the cover first; for `offscreen_target`, first swipe toward the target. A custom-drawn half-screen panel may have no native Alert / Sheet node; judge by the real screenshot.
- `postcondition_failed` from an explicit verification: the action was accepted but the verification condition was not met; check the actual state and then decide the remaining steps, and do not replay the action automatically because verification failed.
- `action_executed=true, action_complete=false`, `uncertain=true`, or a timeout after an action: at least part of the action may have taken effect. For input, send, submit, delete, and similar, look at the real field / record first, and do not blindly do it again after switching to the code entry.
- Brief query failure: the tool may re-read once within bounds; a POST query endpoint should not be treated as a mutation, and a query failure does not prove the phone action was executed.
- `local.pid.0`, `pua_foreground_unavailable`, or XCTest Code 41: a channel fault; call READY to recover it, and do not handle it by changing selectors or repeating phone buttons. For lock screen, signing, and trust problems follow the setup skill; for app password / Face ID follow the authentication takeover.

When going through `functions.exec`, forward content blocks one by one: use `text(block.text)` for text and `image(block)` for images; do not `text(result)` and turn a screenshot into base64 text. If an image cannot be forwarded, open `image.path` / `error.observation.image.path` with `view_image`. Convert coordinates by `pixel_to_point`.

A plain `verified=false` is not an error, and does not require observe or stopping a batch. HTTP accepted only describes the request boundary; continue on the normal path, and explicitly verify the final key state.

Home uses the phone-side dedicated home-screen endpoint. By default it does not separately wait for SpringBoard; the observation made when preparing the next step shows the actual state. When you need to confirm the home screen, explicitly use `verify=true`, which checks the foreground within bounds; the issue where the generic key endpoint returns HTTP 200 but the UI does not change cannot be used to infer the internal cause in iOS / XCTest.

## Bounded recovery of READY

For normal tasks use `pua_ready(recover=true)` or omit recover. False is used only when the user explicitly forbids restarting or for read-only diagnosis, and that restriction is kept. A temporarily stale foreground only clears the old observations / session and re-reads once; only a persistent fault restarts this plugin's service whose ownership has been verified, reusing the valid build. It does not replay navigation, input, or submission.

`ready=false, state="recovering"` carries recovery.job_id and query parameters. status returns a `jobs` array; find the job whose id equals job_id and check recovery_phase; once it goes from stopping / starting to serving, re-verify READY. The Runner may stay running, so do not wait for succeeded and do not start again. Query by phase, logs, and retry_after_seconds, do not write a fixed 15 seconds x 20 wait loop, and do not read a nonexistent single job while swallowing parsing exceptions.

For `ready=false, state="recovery_required", reason="recovery_disabled"`, call recover=true per next_tool / next_arguments only if the user's instructions allow it; if explicitly forbidden, explain the blocker. A normal not-ready state has no error and MCP isError=false, and phone actions still cannot continue. After reaching `ready=true`, reuse the observation in it directly to prepare the next step, without observing again immediately.

Recovery requires the config, endpoint, worker, and listening-port ownership to match; for unknown ownership, an external PUA, a port conflict, or a missing build, follow the returned steps and do not kill processes by port. The 120-second cooldown is diagnosed per retry_after_seconds, without restarting repeatedly. Trust, unlock, and UI automation confirmation are done by the user on the phone.

## Run the provided script directly

Determine `<PLUGIN_ROOT>` from the current project or the installed plugin; do not copy someone's versioned cache path. Routine Home:

```sh
python3 <PLUGIN_ROOT>/scripts/phone.py pua_press_button '{"name":"home","observe":"none","verify":false}'
```

The script uses the shared session and operation lock under the default `~/.local/share/iphone-use` and returns a structured result. When the next step needs unknown page information, explicitly choose observe on that action; when a key verification is needed, explicitly use verify=true. The command output is JSON only: the screenshot is at `image.path` (a scaled JPEG; the `.png` of the same name is the original screenshot); open it with an available image tool when you need to see it, and multiply pixels by `image.pixel_to_point` to get iPhone points.

Pass a matching --state-dir / --url only when the original channel really uses a non-default directory / URL; do not change directories to avoid busy, and do not control the same phone in parallel.

## Write minimal calling code

When the host cannot call the script, you can import the same Runtime. The example below keeps the default config and structured errors:

```python
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).expanduser().resolve()
sys.path.insert(0, str(root / "server"))
from iphone_use import PUAError, Runtime

runtime = Runtime()
try:
    result = runtime.call("pua_press_button", {"name": "home", "observe": "none", "verify": False})
    print(json.dumps(result, ensure_ascii=False))
except PUAError as error:
    print(json.dumps({"error": error.as_dict()}, ensure_ascii=False))
    raise SystemExit(1)
finally:
    runtime.close()
```

Both entries bypass the MCP binding and still go through the shared implementation. Observation IDs are not shared across processes; if you choose to use an ID, obtain the observation in the same Runtime and pass it to the action. Known coordinates or a region need no ID, and do not read an extra image or tree just to get a permit. Use iPhone point coordinates, not Mac screen coordinates or screenshot pixels. A fault in the shared implementation itself is not fixed by switching entries; adjust to the actual exception, and do not create an external PUA session or blindly repeat a mutation.

## Scrolling and batches

The default swipe is `verify=false, observe="none"`: it performs one gesture, and does not read XML to verify progress or fall back automatically. A known region can be used directly, without forcing a tree, anchor, or ID. When the next step needs to read the list anyway, return the needed observation on that action and judge whether it moved along the way; an unverified default return does not mean it did not move.

Only an explicit `verify=true` checks scroll progress, native overlays, and changed context; when debugging, choose tree / both on that call and reuse the returned observation without reading again separately. Progress is judged by geometric change of the list; a refresh of numbers or carousel text should not by itself be the basis for scroll success / rejection. The verification protection for native overlays cannot recognize every custom-drawn panel; after an explicit cover, pick a region or close the panel according to the real state.

When `verify=true` finds no progress on the first gesture, it attaches a screenshot and stops without automatically switching gestures; the legacy parameter `max_attempts=2` can still be passed but does not cause an automatic retry. `scroll_find` swipes at most once per call, and if it still cannot find a tappable target it returns a screenshot first; occlusion and ambiguity stop before swiping. Actually look at the image first and then judge whether to continue, the region, the direction, and the target, and do not directly raise `max_swipes` and rerun.

`no_scroll_progress` does not prove an empty list or the end; an abnormal result attaches a screenshot even if none/tree was requested, so check the entry points, boundaries, overlays, and custom-drawn content. `scroll_context_changed` means the context changed after the gesture; look at the screenshot first and then handle it, and the part already executed must not be treated as unexecuted and replayed. If reading the screenshot fails, keep the original error and execution evidence and suggest fetching the image separately, and do not continue the action on your own.

A batch can run ordinary unverified navigation and input back to back; only an explicit error, uncertain, or an unverified submit stops it, and you continue the remaining steps per completed_steps / stopped_at. Launch activates only once by default; only an explicit verify=true / expect waits for the foreground / page within bounds. If a key verification fails, look at the actual state first and do not activate again automatically.

A successful code call, Home finishing, one app finishing reading, or one batch finishing are all only interim results; continue the remaining work, and end the whole task only after the final key result and delivery are complete.
