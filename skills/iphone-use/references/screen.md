# Phone Screen Preview and Recovery

The widget shows the phone screen to the user; the model only uses the observations the tools actually return. Live, a cached frame, the glow effect, or a gesture indicator does not replace READY and does not prove the task is complete. Open, pause, resume, and reconnect all reuse the same panel in this chat. If a panel already exists, just continue; if it was closed, call `pua_screen()` once. Do not repeat READY or open a new panel just to refresh.

## No image or shown as paused

- Before the first frame arrives, `frame_available=false` does not prove the connection failed. The preview uses a separate USB MJPEG channel, independent of the PUA control channel. When control tools work but the preview has no frames, do not repeatedly restart PUA, create new sessions, or loop on screenshots.
- With no valid image, keep the iPhone frame and a black screen, with only the icon in the center for connecting, locked, authentication, paused, or image unavailable. A brief stream interruption keeps the last frame; a cached frame is not evidence of the current phone state.
- When `preview.paused=true`, check `pause_reason` first. `device_locked` means waiting for the user to unlock; a successful READY only resumes that same lock-screen pause. `authentication` or the legacy `unknown` follows [authentication takeover](authentication.md): wait for the user to actually finish, then resume explicitly.
- The user can click the refresh button at the bottom to reconnect the preview and check unlock; on success it restores the pause that existed at click time, and any new pause that occurred during the check is kept. Refresh does not restart PUA, create a control session, or send phone gestures. The model cannot call the app-only button tools on the user's behalf.
- After a plugin update, an old chat may still be connected to the old process or UI assets. Reconnect the chat, close the old screen page, and call `pua_screen()` once to load the new assets; there is no need to reinstall or restart PUA just to update the image.

When a control tool itself returns a connection failure, handle it per [startup and recovery](startup.md); when UI targeting fails, continue with the screenshot and coordinate flow in the main skill.

## Authentication and tool boundaries

When an app asks for a password, PIN, verification code, or Face ID / Touch ID, follow [authentication takeover](authentication.md): pause the preview, ask the user to finish on the phone, and pause phone actions, reads, and screenshots. Opening the widget or a successful READY does not mean authentication is complete; after the actual completion notice, get a fresh observation before continuing, and do not reuse old coordinates or replay business operations that may have already taken effect.

`pua_screen_frame` and `pua_screen_action` are for the app only; they are not observation or control tools for the model. The refresh, home screen, and screenshot buttons at the bottom are clicked by the user; home screen and screenshot are unavailable while authentication is paused. Hiding or closing the page stops frame polling, and an authentication pause immediately stops capture and clears the actual image.

## Widget shipped with the plugin

The plugin includes the self-contained `assets/phone-screen.html` page, plus the full `ui/` source, styles, dependency lockfile, build config, and widget tests. Installation and normal use load the built page directly; to rebuild, run this in the plugin directory:

```sh
npm ci --prefix ui --no-audit --no-fund
npm run build --prefix ui
python3 scripts/check_screen_ui.py
```

The UI does not depend on a CDN or remote fonts; the USB stream script the server-side preview relies on and the `tooling/` dependency manifest also ship with the plugin. `docs/` and `evals/` are local development material, not runtime dependencies.
