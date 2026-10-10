# Password and Face ID Authentication Takeover

Ask the user to take over only when the current observation or a tool clearly shows an authentication block. App password pages, unlock codes, verification codes, Face ID / Touch ID confirmation, and login renewal are all completed by the user on the phone. An empty control tree or a black screenshot alone is not enough to prove authentication is in progress; first use the current prompt to tell apart a lock screen, mirroring occupation, custom-drawn content, and a channel fault.

## Tell the blocking layer first

| Current evidence | Handling |
| --- | --- |
| App login / password / biometric prompt | Ask the user to finish authentication inside that app; pause phone calls, then observe the target page again. READY cannot prove the app is logged in. |
| `phone_locked` or an actually locked phone | Ask the user to unlock the iPhone personally and keep it awake; after that, re-verify READY and observe the target app. |
| `local.pid.0` / `pua_foreground_unavailable` / XCTest Code 41 | Recover the PUA channel per the setup skill; do not treat it as a wrong app password. Only ask the user to complete the matching action when the system actually requires trust or authentication. |

## What to say at handoff

When an explicit app authentication block is found, first call `pua_screen(action="pause")` to stop USB preview capture and clear the image, and then give the user the takeover prompt. An explicit app authentication pause is not lifted automatically by READY / open. `phone_locked` has already automatically recorded `device_locked` and paused, so no explicit pause is needed; after the actual unlock notice, a successful READY automatically lifts that one lock-screen pause. The user clicking refresh is also a request to actively resume the preview; once refresh confirms unlock, it can lift the app / unknown pause that existed at click time, and the model cannot click this app-only button on the user's behalf. A new pause that happens during the check is not cleared by the old check. A legacy pause without a reason is kept as unknown. During the takeover, do not poll frames, screenshots, or user input.

You must call the question feature available in the host to prompt the user to take over, not just write "reply to continue when done" in a plain message or the final answer. The question states the actual app, the blocked step, the action the user needs to complete, and the work that continues afterward; the first option is fixed as **"Done, continue"**, and the second can be "Cannot complete right now". The question only asks whether the phone operation is finished; it does not collect passwords, PINs, or verification codes.

In Codex Default mode, prefer calling `AskUserQuestion` (Claude Code) / `functions.request_user_input_async` (Codex); for example, when Face ID is currently shown explicitly:

```json
{
  "questions": [{
    "title": "The current app needs Face ID verification. Please complete authentication on the iPhone and stay on the target page; when done, choose \"Done, continue\" and I will go on reading the remaining details.",
    "options": ["Done, continue", "Cannot complete right now"]
  }]
}
```

Replace the app, authentication method, and follow-up work according to current evidence; for a locked phone, ask the user to unlock it personally and keep it awake. When the host provides another question tool, call it per its actual schema, and keep the first option text as "Done, continue"; do not switch modes just to call the question feature. Only if the current host truly has no callable question feature, use a text prompt and explicitly keep the unfinished state of "waiting for user authentication".

An asynchronous question returns immediately, and this is not a user completion notice. Keep the question pending and wait for the user to actually submit an option or reply clearly; a preselected option, a tool return, elapsed waiting time, and no reply must not be treated as completion. You can keep organizing results already obtained or doing other work that does not depend on phone authentication, but you cannot resume phone calls; when there is no independent work, wait for user input, do not use repeated questions or phone polling to pass the waiting time, and do not mark the whole task complete.

Describe only the authentication method and page actually observed; do not guess passwords or PINs or try to bypass biometrics. Do not ask the user to send a password, unlock code, or verification code in chat, and do not write credentials into `pua_type_text`, batch, logs, scripts, or code fallbacks. Even if a password field appears as an ordinary TextField, the user enters it personally; do not judge only by the SecureTextField type.

Preserve the current app / page, the content already obtained, the steps already executed, the unfinished items, and the action execution boundary, without requiring step-by-step verification to save progress, and do not record authentication credentials. During the takeover, pause operations, observations, and screenshots on that iPhone; you can organize existing results and progress, but you cannot poll for user input. When Face ID fails, asks to switch to a password, or a verification code expires, let the user handle it per the phone's actual prompts, and do not trigger verification repeatedly or restart the app / PUA over and over.

## Continuing after authentication

Continue only after receiving the user's actual choice of "Done, continue" or an explicit statement that authentication is complete: for an app authentication or unknown pause, call `pua_screen(action="resume")`; for a device lock screen, re-verify READY, and on success the matching lock-screen pause is lifted automatically; elapsed waiting time does not equal completion or authorization to resume. Then get one fresh observation, preparing the next step while judging the correct foreground app, the authentication prompt, and the current target page. The user may have switched apps, gone back a level, scrolled, or incidentally completed follow-up operations, so do not reuse the coordinates, observation_id, or element IDs from before the takeover. Find the next semantic target based on the new state; when necessary use a screenshot to read protected page content, and do not log in again or verify separately at every step.

If authentication is still not complete, point out the remaining step and wait, and do not perform the blocked action. If the user chooses "Cannot complete right now" or says they cannot authenticate for now, explain what has been completed and what remains, and keep the takeover checkpoint; if the user cancels, stop further operations. If the phone or channel fails, recover READY per the setup skill and reuse the new observation in it directly to prepare the next step; do not mistake an expired app session for the service needing a restart.

Continue the remaining authorized work based on the new state. Submissions completed during the user's takeover must have their results read back first; do not resend, pay, place an order again, or replay the whole input / batch. Completing authentication does not mean the original task is complete; in the end you must still check all apps, fields, coverage, and output files.
