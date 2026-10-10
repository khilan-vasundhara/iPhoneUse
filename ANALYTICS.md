# iPhone Use analytics

PostHog organization: `iPhone-use`. Project: `653022` (US Cloud).
Project time zone: `Asia/Shanghai`.
[Usage and reliability dashboard](https://us.posthog.com/project/653022/dashboard/2185876).

This follows Cowart's server-side delivery approach, with a Python standard-library
client in `server/analytics.py`. The write-only project token in
`server/posthog.json` ships with the plugin; a personal API key is never required
for capture. See the [PostHog capture API](https://posthog.com/docs/api/capture).

## Collection and controls

Analytics is enabled by default. It records a random installation UUID saved
privately in the plugin's state directory, a new random process/session UUID,
plugin version, platform, event timestamp and the bounded fields below. The
installation UUID remains stable through upgrades that reuse the state directory.
It represents an installation, not a known person, phone or chat. There are no
person profiles, automatic frontend capture, phone recordings or GeoIP enrichment.

Phone text, selectors, accessibility trees, screenshots, clipboard data, app
bundle IDs, UDIDs, signing teams, filesystem paths, MCP request IDs and exception
messages are never sent. Only known tools, actions, states and error codes are
accepted; unknown errors become `other`.

Set either environment variable on the MCP server and restart it to disable
analytics completely, including local analytics identity creation:

```sh
IPHONE_USE_ANALYTICS=0
# Or:
DO_NOT_TRACK=1
```

For Codex, add `IPHONE_USE_ANALYTICS = "0"` under
`[mcp_servers.iphone_use.env]` in `~/.codex/config.toml`. For a portable MCP JSON
configuration, add `"env": {"IPHONE_USE_ANALYTICS": "0"}` to the server entry.

`IPHONE_USE_POSTHOG_PROJECT_TOKEN` overrides the bundled token. An explicitly
empty value disables sending. For local development, `server/posthog.local.json`
may contain `{"projectToken":"your-write-only-project-token"}`; this file is
ignored by Git and excluded from both install and source packages. Precedence:
environment override, local config, bundled config. Capture always uses US Cloud.

`IPHONE_USE_ANALYTICS_ENV` accepts `production` (default), `development` or `test`.
The dashboard only counts `production`. `sh scripts/check.sh` disables telemetry
for tests and subprocess package checks; analytics unit tests inject fake senders.
Run standalone test commands with `IPHONE_USE_ANALYTICS=0` as well.

## Events

| Event | When | Bounded properties |
| --- | --- | --- |
| `iphone_use_session_started` | Once per MCP process, on initialize or first tracked Runtime call | Common properties only |
| `iphone_use_tool_called` | After a known tool finishes or raises, for MCP and direct Runtime/CLI calls | `tool_name`, `outcome`, `error_code`, `duration_ms`; `batch_size` for batches |
| `iphone_use_ready_result` | Each READY check | Tool fields plus `ready_state` |
| `iphone_use_setup_result` | Each setup call | Tool fields plus `setup_action`, `setup_state` |
| `iphone_use_screen_action` | Preview open/pause/resume and toolbar actions | Tool fields plus `screen_action` |

`pua_screen_frame` polling is excluded entirely. Dedicated result events are not
additional tool calls: usage and failure charts count only
`iphone_use_tool_called`. Batch substeps are not double-counted.

`success` means the tool returned without an error or an explicit incomplete
result. It does not promise that a user task was completed or independently
verified. READY false, incomplete input/batches and queued/running setup jobs
are `pending`; raised errors and explicit failed results are `error`. Setup
events track submission/status calls, not autonomous worker completion.

Durations are in milliseconds, from Runtime entry through return/error. They
include the phone operation lock and execution, exclude MCP worker queue waiting,
response serialization and analytics delivery. Duration is capped at one hour,
batch size at 20. Arbitrary argument and result objects are never serialized.

## Dashboard definitions

The eight native PostHog trend insights cover daily active installations, MCP
starts, tool usage, READY results, tool failure rate, average/P95 latency, error
categories and setup actions. The exact queries are preserved in
`scripts/posthog-dashboard.json` in the source package.

Active installations are distinct random installation IDs with a successful
task tool or READY call, excluding doctor, setup, metrics and preview controls.
MCP starts count processes, not conversations. Failure rate includes pending
calls in its denominator; a displayed zero on a day with no calls is not evidence
of reliability. The dashboard is empty until production events arrive. Test and
development events remain available in Activity but are excluded from these
charts. These are project-specific definitions, not team-approved Data Catalog
metrics.

## Delivery limits

Capture queues bounded events in memory on a daemon worker, at most 256 waiting
events and 20 events per request. Each event has a random UUID; one retry for a
network failure, HTTP 429 or HTTP 5xx reuses the same payload and UUID. Ordinary
4xx errors are not retried. Requests have a three-second socket timeout, and
shutdown waits at most 1.5 seconds. No events are written to disk for replay.
Queue overflow, extended outages or an immediate process exit can drop events;
this is usage telemetry, not an audit trail. Analytics failures never change
phone results, replay phone operations or write to MCP stdout.
