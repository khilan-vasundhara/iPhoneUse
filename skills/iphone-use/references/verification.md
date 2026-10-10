# Verifying Key Results

Routine actions run optimistically by default; do not insert a dedicated observation just to verify the previous action. When preparing the next step needs page information, reuse that observation to judge progress along the way; adjust or redo only when it clearly did not take effect. A plain `verified=false` only means there was no explicit verification. `expect`, `verify=true`, and final read-backs are for key results that actually matter; they are not required for every tap, page switch, expansion, or scroll.

## Lists and details

`pua_collect_list` is a page collector, not a business model for any app. Confirm the page and filter scope through the list reads the task needs anyway, and keep the first / last page boundaries, the stop reason, the dedup rule, and the missing fields. In the end, reconcile coverage and count against what the user asked for; no progress, a truncated tree, or hitting the page limit does not mean the list is complete.

The same name can correspond to different records; the actual order number, date, status, and amount together can tell records apart. The tool's default dedup may collapse real records that display identically, so state the actual gap in the final conclusion. After opening a detail page, read the needed fields directly; the same read is enough to tell whether you are on the right detail page, so do not add a dedicated page-check turn.

Fixed headers, native overlays, and custom-drawn panels can cover a target that still exists in the tree. An explicit occluded / offscreen error means the target tap was not executed; the error already attaches the current screenshot, so when the target is visible switch to a coordinate tap directly, and when it is covered deal with the cover first. If a screenshot triggers a share sheet, handle the current sheet; do not loop closing it and immediately repeating the screenshot, and do not claim the plugin implements alternative capture or in-app export.

If the target is still not tappable after scrolling, look at the screenshot first and then decide whether to continue; `scroll_find` swipes at most once per call, and stops immediately on occlusion / ambiguity. A screenshot is also attached when explicit scroll verification shows no progress on the first try, the scroll region is blocked, the context changes, or list collection meets a duplicate page. Abnormal results are not limited by the ordinary none/tree output options; reuse an attached image directly. No progress by itself is not proof that the list is at the end or the collection is complete.

## Timeliness and aggregation

For asynchronous refreshes, wait only when the content the task needs has not yet loaded; read the actual fields and record the page's estimate, net value, or trade date. Opening the app today does not mean the data belongs to today.

Record across accounts / currencies separately, and avoid double-adding original-currency details and account totals. "Pending confirmation", "deducted successfully", and "shares confirmed" are different business stages; define success per the user's request in the end. Keep cash, holdings, in-transit, and unknown accounts attributed to their owners, and leave differences that cannot be reconciled as unknown. PUA is not responsible for valuation, currency conversion, or defining net worth.

Before writing to an external database, use that service's connector to check field types and meanings; after writing, one read-back of the key target, body, fields, and duplicate count is enough to verify the final delivery. The plugin provides iPhone UI capability and has no general Notion / document API.

## Input and submission

Type the full content the task needs directly; do not first try a short Chinese / ASCII probe. Normal searching, filtering, or editing needs no step-by-step read-back; when the next step needs to look at the page, judge whether the input and navigation took effect along the way. Use synthetic text only when debugging a confirmed input problem, and never use the user's real assets or account information for testing.

For a key final draft, use `pua_type_text(verify=true)` for an exact read-back, or use the observation you needed anyway before sending to check the recipient and full content. After confirming the content, send once, and finally check content, location, and duplicate count against the message / record / result page. Multi-line editing needs a clearly suitable TextView; allowing newlines does not mean allowing send.

If garbled text, a partial send, a timeout, uncertain, or a partially completed action clearly appears, read the actual field / conversation / submission record first and then perform the unfinished part; do not blindly retype or resend. The tool accepting a request does not prove business success, but normal actions also do not require stopping each time; the final conclusion should have evidence of the key result. Passwords, unlock codes, and verification codes are left for the user to enter on the phone.

When an input read-back does not match or the expected page does not appear, attach the current screenshot, first judge focus, actual text, pop-ups, and the submission result, and then fill in the unfinished part. If the screenshot fails, keep the original error and execution evidence and read once separately when the image is missing; do not continue typing or submitting on your own.

## Timing and traceability

Observation IDs and screenshots can connect the necessary actions and observations; the most recent 100 images are kept by default, and key verification evidence is saved to a local directory specified by the user before cleanup. XML and parameters are not automatically saved as a full trace; metrics only keeps bounded request / tool timings in the current process and does not include typed text or business values. When the user asks for a full trace, save only the necessary evidence locally and exclude it from Git.

Record first-time deployment, feature diagnosis, business tasks, and report generation separately. HTTP latency, the number of UI actions, the number of tool calls, and task wall-clock time are different measures; without the corresponding timing, you cannot attribute all gaps to model thinking. When evaluating optimizations, look at both the actual end-to-end time and the completeness of the final delivery.
