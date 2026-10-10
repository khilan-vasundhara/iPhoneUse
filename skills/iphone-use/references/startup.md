# Startup and Recovery

When READY does not return `ready=true`, continue according to the returned state. Do not treat this result as failure of the whole task, and do not replay business actions that may already have taken effect. User restrictions such as read-only or no start / restart always remain in force.

## Service not started

`recover=true` can recover a stale XCTest channel whose ownership has been verified, but it does not perform a cold start automatically. When READY returns `pua_unreachable`, connection refused, `not_ready`, or an explicit service-not-started result, `initialization_required=true` and the recovery's next_tool / next_arguments point to the next initialization step; this does not mean it has been started automatically:

1. Call `pua_setup(action="status")` to check `configured`, `service`, and `jobs`.
2. If a start / recover job matching the current config / endpoint is queued or running, record its `id` and query that same job with `pua_setup(action="status", job_id=...)`; match the id in the returned `jobs` array and do not reuse an old, unrelated job. Once `recovery_phase="serving"` is reached or the started service reaches `service.ready=true`, call READY again. The long-running Runner may stay running; do not wait for succeeded and do not start again. If a matching fetch / build job is running, reuse and query it first, then continue with the missing steps.
3. When `configured=true`, the service is not ready, and there is no reusable active job, call `pua_setup(action="start")` once to reuse the existing signed build. Record the new job's `job_id` from the actual response, or `job.id` when `already_running=true`, then query that same job. Only when the response explicitly says the source / build is missing or invalid, run fetch / build per `iphone-use-setup`; do not rebuild, re-sign, or reinstall just because the service is not started. If `service.ready=true`, re-verify READY directly without start.
4. When `configured=false`, read `iphone-use-setup` and complete doctor / discover, fetch, configure, build / start according to what is actually missing. Only real USB, Xcode, trust, developer mode, or signing blockers move to the corresponding handling; when the user personally needs to unlock, sign in, or confirm, use the question flow in [authentication takeover](authentication.md).
5. After READY returns `ready=true`, reuse its observation to continue the original task. Report the exact blocker only when something is missing that the user must complete or a real startup failure exists.

While the service is not yet started, the widget may be blank for a while; having it open or blank neither proves READY nor means the whole task failed.

## Channel recovering

- `ready=false, state="recovering"`: query the same job using the recovery's job_id and status parameters. Find that job in the returned `jobs` array, and re-verify READY once recovery_phase=serving. The long-running Runner may stay running; do not wait for succeeded and do not start repeatedly.
- `ready=false, state="recovery_required", reason="recovery_disabled"`: only when the user's instructions allow recovery, call recover=true per next_tool / next_arguments; if restarting is explicitly forbidden, keep the restriction and report the blocker.

Neither state has an error or MCP isError=false, and neither means the phone is operable. For actual recovery refusal, cooldown, lock screen, and similar, handle according to the returned reason; query by job status and the returned retry_after_seconds, not with a fixed long sleep or a fixed number of empty polls.

## Screen preview

The widget shows the latest phone image through a separate USB MJPEG channel; the UI reads the server-side cache at most 4 times per second, does not poll screenshots or XML, and does not take the phone operation lock; the preview keeps refreshing during long phone operations. After the first operation the edge gradient stays on, and it is cleared on authentication pause, disconnect / stream change, and close / reload; the round cursor marks the actual tap position or drag path; neither proves an action succeeded. When the widget is hidden / closed, polling stops and the preview lease expires after 5 seconds; an authentication pause stops capture and clears the image, and resuming must wait for the user's explicit confirmation. After a plugin update, an existing chat may still run the old MCP process and old page; reconnect the chat and reopen the widget to load the new version, and do not rely on repeated READY to refresh a cache. A blank screen with `paused=true` is a takeover pause, and you resume only after the user confirms completion.
