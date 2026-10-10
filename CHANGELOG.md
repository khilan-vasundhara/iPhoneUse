# Changelog

## Unreleased

- Added a separate iPhone-use PostHog organization / project (modeled on Cowart) for anonymous statistics on starts, tool use, READY results, setup actions and preview controls.
- Events are sent in the background with a restricted set of fields, excluding frames, text, device identifiers and high-frequency frame polling. Telemetry can be disabled; a bounded queue and network retries that keep the event UUID never affect phone operations.
- Added 8 usage and stability charts that separate production from validation data, plus analytics documentation, regression tests and release package configuration.

## 0.3.6 - 2026-10-08

- The screen gradient keeps a faint light band at the top and bottom centers that gradually connects with the existing color and dot animations and then softly recedes. Three static masks are generated with the layout and keep reusing the opacity cross-fade.

- Tool names changed from `wda_*` to `pua_*` (PUA stands for Phone Use Agent): 17 model tools and 2 widget-only tools.
- Synced tool descriptions, server instructions, recovery / next-call guidance, both skills and their references, the Chinese and English READMEs, the widget and the command-line entry points; channel error codes are now `pua_*`.
- The underlying WebDriverAgent dependency, internal modules, protocol paths and compatibility environment variables are kept, so existing devices, signing, builds and runtime data are reused.

- Scroll-find performs at most one gesture per call; it stops immediately when the target is covered or ambiguous, and attaches a screenshot when no tappable target is found after scrolling so the model looks at the screen before deciding to continue.
- Explicit scroll verification returns a screenshot on the first no-progress result and no longer runs an automatic fallback gesture; the legacy repeat-count parameter is accepted but no longer swipes blindly.
- Screenshot fallback now covers region occlusion, scroll-context changes, input read-back mismatches and expected pages that did not appear; list collection also attaches a screenshot on a duplicate page. Existing observations and images are reused, the original error and executed actions are preserved, and business operations are not replayed.

## 0.3.4 - 2026-10-08

- `docs/` and `evals/` are now maintained locally and removed from Git and the release package; the necessary screen-operation notes moved into the skill references.
- Source packages and installed packages are now distinct: installs exclude root Python tests, CI and development benchmark / smoke scripts, and keep the widget source, build configuration, dependency lockfile, tests and built page intact.
- The Chinese and English READMEs now state the on-phone WDA prerequisite, add signing / install / start steps and official guidance, and credit Appium / WebDriverAgent.
- The widget background gained a very light static gray dot grid, tiled at 20px with a single CSS radial gradient; no extra DOM nodes, animation or JavaScript drawing loop.

## 0.3.3 - 2026-10-08

- The plugin description is now the English "Let Codex control your iPhone", conveying that Codex operates the user's own iPhone.

## 0.3.2 - 2026-10-08

- The black placeholder screen shows a matching gray-white line icon for connecting, not connected, locked, authentication, paused and screen-unavailable states.
- Only a centered status icon is shown inside the screen; text hints are kept for assistive reading.
- The plugin icon is now a white rounded base with green and blue glass screens, translucent highlights and a soft shadow.
- Refreshing shows the connecting icon and restores the previous hint on failure; phone action buttons stay disabled while paused for authentication.

## 0.3.0 - 2026-10-07

- The project, plugin, skills, MCP registration, screen resources and source entry points are unified as iPhone Use.
- The Chinese README was rewritten for installation, dependencies, one-prompt install, features and technical implementation, and gained an English-document link.
- New installs use a generic runtime directory; upgrades keep reusing existing device configuration and builds, and the original environment variables remain supported.
- After a successful install the old plugin registration is disabled and only MCP entries confirmed to belong to the old install are cleaned up, keeping the caches needed for background work.

## 0.2.7 - 2026-10-07

- After a UI targeting or input focus failure, look at the screenshot first, handle occlusion and tap using pixel-converted coordinates; documented how to forward image blocks so screenshots are not output as base64 text.
- Occlusion errors no longer suggest tapping the coordinates of a background control; focus failures suggest re-picking the point, avoiding blind repeats and premature handback to the user.
- Distinguished lock-screen pauses from app-authentication pauses: after confirming unlock, READY / a user refresh resumes the lock-screen pause, while explicit authentication and legacy unknown pauses still need a completion notice and resume.
- The refresh button reconnects and checks unlock; a user refresh can resume a preview paused by a tap, and a new concurrent pause is not cleared by an older check.
- With no frame at all the iPhone shell is kept, using a black screen-off texture and small "Not connected" text as a placeholder; pauses show their reason and READY returns the paused state.

## 0.2.6 - 2026-10-07

- The plugin icon takes cues from a rounded base with a stacked-phone shape, using a dark gray base, a gray back layer and a translucent white front layer, keeping a slight 3D shadow and highlight.
- The logo and composerIcon share a self-contained SVG, staying crisp as vectors; the local install cache refreshes with each version.

## 0.2.5 - 2026-10-07

- READY and the phone screen tool return a stable widget session identifier so Codex reuses the already-open screen tab in this chat.
- Repeated setup / connection recovery and preview open / pause / resume reuse the same panel; the session identifier is unchanged after an MCP reconnect.
- Updated the setup and usage instructions: continue directly when a panel exists, and call the screen tool only to reopen a closed panel.
- The widget top margin grew from 14px to 28px, and the light background became a very light gray `#f8f8f8`.
- The top status bar and bottom toolbar use a white background, a 0.5px very light gray border and a soft diffuse shadow.
- Dots and gradient were split into independent animation layers: the dot size pulse runs on a 4-second cycle, while gradient alternation and breathing keep an 8-second cycle.

## 0.2.4 - 2026-10-07

- The wave dot grid alternation period was shortened from 12 seconds to 4 seconds for a more visible change.
- Dot radius changed from 6%-23% to 4%-27% of the grid spacing, so large dots are slightly larger and small ones smaller, widening the wave's size variation.
- Fixed CSS precedence between the color and dot layers, disabled animation under reduced-motion, and paused animation while the page is hidden.

## 0.2.3 - 2026-10-07

- The gesture indicator is now neutral gray with a thin outline and a light shadow; the blue fill was removed.
- A tap shows for 1.6 seconds with a slight press shrink, rebound and hold before fading; a drag shows for 1.6-2 seconds, including a press at the start, smooth movement, release rebound and a hold at the end point.
- Consecutive actions are shown independently, and a later action no longer cancels the previous indicator early; authentication pause, stream gaps / switches, hiding and page teardown clear all gestures. Under reduced-motion they stay still but keep the full display time.

## 0.2.2 - 2026-10-07

- The toolbar uses unified round-cap line icons: refresh, home and screenshot share the same 24x24 grid, 18px display size and 1.75 stroke width; the house and camera outlines use soft rounded corners.
- The refresh arrow and arc now join at the same endpoint, fixing the misalignment at the arrow corner; the screenshot icon became a camera outline.
- Upgraded the install cache and widget URI to 0.2.2, including the edge fade and wave dot grid from 0.2.1.

## 0.2.1 - 2026-10-07

- Following the reference image, the center of the top and bottom edges and the middle of the left and right edges fade naturally to transparent while the four corners keep a sky-blue soft glow; the glow, thin bright edge and dot grid share one fade mask.
- The equal-size dot grid became a wave texture with continuously varying size and brightness, and three static textures cross-fade with the color layers; still opacity-only animation, paused while hidden and static under reduced-motion.
- Updated the plugin cache version and widget resource URI; the built self-contained HTML ships with the package.

## 0.2.0 - 2026-10-07

Latency optimization: less data entering the model context each turn, fewer turns to complete a step, and removal of timeouts that stalled tasks. Details and measurements are recorded in local development notes.

- **Compact observations.** Nodes drop the `XCUIElementType` prefix, name / value are not repeated when identical to the text, defaults are omitted, and `rect` is an integer `[x, y, width, height]`; the same 99-node page went from 18,424 to 6,868 bytes. `wda_find`, `scroll_find` and `collect_list` use the same format and no longer return element IDs. This is an output format change; scripts relying on the old fields need adjusting.
- **Screenshots actually reach the model.** Model-facing results return only one compact JSON text block and an image block, without `structuredContent`: Codex drops image blocks when structured content is present. Screenshots are first shrunk with the system `sips` to a JPEG around 722x1568, returning an exact `image.pixel_to_point`, and the original PNG is kept under the same name with a `.png` extension.
- **Label failures switch to coordinates immediately.** When a selector is not found, not unique, judged not tappable or not editable, the error result attaches the current screenshot and coordinate points so the next call acts by coordinates directly; for input, tap the field by coordinates first and then call `wda_type_text` without a selector. Same-name elements stacked at one position, or only one on screen, are resolved to that target automatically; selectors gained `label_contains` and `index`.
- **Long text input.** Text is sent in chunks of about 200 characters with a timeout computed from the length, no longer timing out as "uncertain" at around 450 characters; when a single call's time budget is exceeded it returns a `continue_token` to resume without resending text. Batch also has a time budget and stops between steps when it runs out.
- **Post-action observation waits for transitions to finish.** Before the tree read attached to an action, WDA waits for animations to end (up to 0.8 seconds), avoiding a tree that mixes two pages.
- **Fewer requests.** Element queries return type and position in one call; the page-source root directly provides the foreground app and screen size; coordinate actions reuse a short-lived viewport cache. Warm-path selector taps went from 5 to 3 requests and tree observation from 3 to 1.
- **Preview and responsiveness.** Frame requests and the toolbar are answered directly on the read thread, so long phone operations no longer freeze the preview; the streaming thread caches state by file signature.
- **Phone screen widget redesign.** The top shows the device model and Live status, and the bottom adds three buttons: refresh, home screen and screenshot to clipboard (for user clicks only; the latter two are disabled during an authentication pause). The edge glow was redone: it wraps around the large screen corners with fuller corners, three static sky-blue-dominant gradient layers cross-fade, and a white dot texture sits on top; only opacity is animated, and the soft edge is baked into one mask image rather than a live blur filter. The UI follows the host's light / dark theme.
- **Metrics.** `wda_metrics` adds per-tool returned bytes, per-endpoint bytes and the wait time between two calls, and supports `reset`; added `scripts/benchmark.py` for fixed real-device tasks.
- The model-visible part of tool descriptions dropped from 29,568 to 21,419 bytes; startup and recovery details of the two skills moved into references. The catalog has 19 tools: 17 model tools and 2 app-only.
- The dependency manifest version in `tooling/` no longer changes with the plugin version: its lockfile hash decides whether USB dependencies are reinstalled, and a release with no dependency changes should not make the next cold start run `npm ci` again.

## 0.1.14 — 2026-10-07

- Keep the memory-only last preview frame across hidden-window lease expiry, stream gaps, request failures and bridge reconnects; resume polling on visibility / page-cache return. Authentication pause and teardown still erase all image backups, and delayed pre-pause replies cannot restore them.
- Encode only requested latest JPEGs, skip identical frames, avoid repeated same-size layout, cap frame polling at 4 fps and apply bounded timeouts / retry backoff.
- Remove SDK debug logs containing full frames; keep rounded gradient rings static and animate only composited opacity, pausing while hidden. Drag cursors use transform rather than left/top animation.

## 0.1.13 - 2026-10-07

- Added a top Dynamic Island positioned by the short-side ratio with a subtle camera decoration; in landscape it rotates to the left with the shell.
- The four rectangular light bands became gradient glows that follow the rounded outline, keeping a constant soft glow and honoring reduced-motion.
- The device shrinks 4% within the available area with adaptive top and bottom margins; image ratio and cursor coordinate mapping are unchanged, and capture and operation requests are unchanged.

## 0.1.12 - 2026-10-07

- The plugin description, operation and setup skills state that a new conversation initializes READY first, text tasks use `recover=true, screenshot=false`, and the observation returned by READY is reused to continue the task.
- WDA not started, connection refused or not_ready enter the status / start branch; existing queued / running work, configuration and valid builds are reused, fetch / build run only for what is actually missing, and the task is neither ended nor fully reinstalled.
- Not-started errors keep the exact error code and attach `ready=false`, `initialization_required=true` and the setup status next step, without automatically starting / restarting.
- Distinguished cold start from verified-ownership XCTest auto-recovery; a long-running Runner does not wait for succeeded, and a probeable service still needs READY as proof. User restrictions such as read-only and no start / restart are honored, and real user prerequisites use the "Done, continue" question flow.
- Opening the widget or a temporary blank does not mean READY or task failure; after "open it so I can see", initialization and authorized tasks continue, pausing only when confirmation is explicitly requested.

## 0.1.11 - 2026-10-07

- After the first operation, the screen edge gradient and ripple stay visible instead of flickering off between tool calls; temporary missing frames / hiding keep the state, while authentication pause, disconnect / stream switch and page end clear it.
- Added an adaptive rounded iPhone shell with a thin metal frame, black glass edge and side button decorations; portrait / landscape keep the full screen ratio and cursor coordinates still map to the inner screen.
- The frame takes cues from Apple's official Product Bezels and the community devices.css, drawn in original CSS without covering actual pixels or adding remote resources or dependencies.
- Only UI state and layout changed, with no added WDA read / operation requests or higher frame polling rate; the resource version was updated to load the new widget. The persistent glow does not mean the task is complete.

## 0.1.10 - 2026-10-07

- Password, Face ID or phone unlock handoff must use the host's question feature when available, with the first option fixed as "Done, continue" and the second possibly "Can't do it right now"; added an exact parameter example for Default async questions.
- Preview / phone operation resumes only after the user actually answers; a preselected option, an immediate tool return or elapsed time does not mean completion. Progress is kept and work that does not depend on authentication continues.
- Synced setup, the operation skill, the authentication reference, widget notes and MCP instructions.

## 0.1.9 - 2026-10-07

- Fixed the blank widget on real devices: the socket handed off by usbmux is paused, so reading now resumes after the HTTP parser is attached, and the standalone USB MJPEG channel receives real phone frames.
- The HTTP regression fixture now simulates a real paused socket, so the issue is no longer missed with only a fresh TCP connection; chunked decoding, backpressure and own-connection cleanup are kept.
- Updated UI resources and the install version to refresh caches; WDA is not restarted, no session is created and no phone observation / operation requests are added.

## 0.1.8 - 2026-10-07

- Following the reference image, the thin bright outer ring became a blue-violet soft glow inside the screen, fading inward from the four edges while the center stays clear; ripples are expressed with slow breathing and slight scaling.
- The cursor sits above the glow, keeping a pure-screen interface; reduced-motion keeps working. Frame polling, phone operations and observation counts are unchanged.
- Updated the UI resource version and plugin cache path so the old glow is no longer shown.

## 0.1.7 - 2026-10-07

- Added a phone-screen-only sidebar MCP App; READY association shows the entry by default, and `wda_screen` can reopen, pause and resume it.
- Uses WDA's standalone USB MJPEG channel; the UI fetches the latest cached frame at most 5 times per second without adding XCTest / XML / WDA screenshot requests or taking the operation lock, and images are kept only in memory.
- While the AI operates, an edge ripple gradient glow is shown and the actual tap / drag coordinates show a round cursor; activity display does not prove an action succeeded.
- Before a password or Face ID handoff the preview stops and the picture is cleared, resuming only after the user explicitly says it is done; after the widget is hidden / closed the lease expires within a bound.
- The catalog added `wda_screen` and the app-only `wda_screen_frame`, for 17 model tools, 1 app tool and 2 skills.

## 0.1.6 - 2026-10-07

- On install, iphone_use is registered as a standard MCP under the same name, bypassing Codex's shared plugin-tool instruction budget; skills, server and tool names are kept and no second namespace is created.
- The published batch schema drops duplicate descriptions and extracts selector / observe into $defs; all 8 operations and all parameters are kept, below the host's default 5KB lossy-compression threshold.
- Runtime closed-set parameter validation stays complete; added regressions for schema references / equivalence / byte budget and install registration, verified with real model tool binding and native metrics calls.

## 0.1.5 - 2026-10-07

- Ordinary actions default to observe=none; input, Home, app activation and scrolling default to verify=false. Known batches continue optimistically, an action returns an observation along the way when the next step needs the page, and final key results are verified explicitly.
- Full text is written at once without trying short text first; the editable type check is reused and exact read-back is enabled on demand. Submit / uncertain writes are still not replayed automatically, and authentication is still handed to the user.
- observation_id is optional for coordinates and custom scroll regions; when provided it only checks the same runtime, app and viewport, with no whole-image match, content fingerprint or 30-second expiry.
- Scrolling defaults to one gesture with no XML progress read; explicit verification uses stable control displacement, and a number refresh does not count as progress. scroll_find queries and collect_list pages are reused to reduce repeated reads.
- On first session creation or takeover, waitForIdleTimeout=0 / animationCoolOffTimeout=0 are configured; the setting is applied once and warm actions do not reconfigure.
- GET and known POST element queries are treated as reads, retried once within bounds without resetting the deadline; old element IDs do not cross sessions, and real write operations are not replayed automatically.

## 0.1.4 - 2026-10-07

- Normal startup explicitly uses default recovery; READY not-ready diagnostics / background recovery return a normal status while real rejections remain errors; proving an old service READY is forbidden while it is recovering.
- The three CLIs return a nonzero status for ready=false; the read-only smoke explicitly forbids starting recovery.
- After one activation, the real foreground is polled for up to 5 seconds; on failure the action evidence, requested / actual app and recovery entry are kept.
- Occluded and off-screen targets gained not-executed evidence; custom scroll invalidation gained concrete reasons, a new observation and content / geometry diagnostics.
- Native overlay regions, including stacked sheets / alerts, are constrained before scrolling; the viewport and overlays are checked after each gesture and fallback gestures stop on change, and verify=false still keeps these checks.
- Audited all 11 tool errors and the eval script errors of T01, and added skill handling for self-drawn overlays, dynamic regions, batch stops and transitions; no operation rules specific to a financial app were added.

## 0.1.3 - 2026-10-07

- The operation skill gained a user handoff flow and prompt examples for app passwords, PINs, verification codes and Face ID / Touch ID.
- During handoff, phone actions / reads / screenshots pause and progress is kept; after the user finishes, re-locate and continue, avoiding repeating an already completed submission.
- Distinguished app authentication, phone lock screen and WDA faults; the setup skill and troubleshooting reference point to the same flow.

## 0.1.2 - 2026-10-07

- swipe gained an `observe` output option; turning observation off still verifies progress by default, and a no-progress error attaches the current state, execution evidence and list entry / region diagnostics.
- selector explicitly supports enabled and safely encodes multiline text, quotes, backslashes and Unicode; NUL is rejected before the operation, with regressions covering the real Apple Foundation parser.
- The schema filled in field purposes; unknown parameters and batches return the exact path, allowed fields and not-executed evidence.
- READY retries a stale foreground read only once, and a persistent local.pid / XCTest Code 41 asynchronously recovers the service with verified ownership; persistent dedup, a 120-second cooldown and a bounded PID publish wait avoid restart loops.
- Read failures after tap, input, Home, activation and gestures keep the executed evidence and forbid automatic replay; read tools only offer a recovery entry.
- Added screenshot error attribution and skill recovery and verification rules; the Futu split-pane scope is unchanged.

## 0.1.1 - 2026-10-07

- Home uses WDA's dedicated homescreen endpoint and verifies SpringBoard is in the foreground; both a no-op and a read failure after execution clearly keep state evidence.
- Custom scrolling only verifies the target region and full-page native overlays, so a carousel outside the region no longer invalidates the observation; coordinate taps keep the original strict checks.
- Added `wda_apps`, which queries the actually installed list, 36 Apple-verified common apps and the public Search API, including source, publisher and install status.
- The skill provides a script / Python fallback when MCP fails, reusing the session, operation lock and action protection; added cross-app complete delivery and continue-execution rules.
- Fixed TIME_WAIT of a closed USB forwarding connection being misreported as a port in use; added XCTest Code 41 recovery guidance.
- Recorded the log investigation and attribution boundary for the mid-task final in T01. The Futu account split-pane is not yet changed.

## 0.1.0 - 2026-10-06

First release of the local WDA control plugin with 2 skills, 15 MCP tools and guided install / READY verification.
