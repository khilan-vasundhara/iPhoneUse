# iPhone Use for Claude Code

Let Claude Code test apps on a **real iPhone** over USB. Ask in plain English: open apps, tap, scroll, type, read the screen, and check results.

It uses [WebDriverAgent](https://github.com/appium/WebDriverAgent) (WDA) on the phone and a local MCP server on your Mac.

## Requirements

- macOS with full **Xcode** (Command Line Tools alone are not enough)
- An iPhone connected by USB: trusted, unlocked, Developer Mode on
- An Apple account / development team in Xcode (to sign WDA)
- Python 3.9+ and Node.js 20.19+

## Install

Option A: Claude Code plugin

```sh
claude plugin marketplace add khilan-vasundhara/iPhoneUse
claude plugin install iphone-use@iphone-use
```

Option B: clone and run the script

```sh
git clone https://github.com/khilan-vasundhara/iPhoneUse.git ~/iPhoneUse
sh ~/iPhoneUse/scripts/install-claude.sh
```

Restart Claude Code, then check that `iphone_use` shows as connected:

```sh
claude mcp list
```

## First-time phone setup

Ask Claude Code:

> Use iphone-use-setup to configure my iPhone.

It finds your phone, signs and builds WDA with your own Apple team, and starts it. You will need to approve trust, Developer Mode or unlock prompts on the phone. Tests can start once `pua_ready` returns `ready=true`.

## Use it

Just ask, for example:

> Open Settings and tell me the iOS version.
>
> Open my app, log in with the test account, and check that the home screen loads.

Passwords, verification codes and Face ID are always completed by you on the phone. Claude will pause and wait.

## Watch the phone live

Claude Code has no side panel, so use the browser mirror (local to your Mac):

```sh
python3 ~/iPhoneUse/scripts/mirror.py     # opens http://127.0.0.1:8765
```

- **Terminal:** run it in a second tab, or type `/iphone-use:mirror` in Claude Code. Put the browser next to the terminal.
- **VS Code:** run the task **iPhone Mirror** (from `.vscode/tasks.json`), then Cmd+Shift+P → **Simple Browser: Show** → `http://127.0.0.1:8765`, and drag the tab beside Claude Code.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `iphone_use` not connected | Restart Claude Code, run `claude mcp list`, re-run the install step |
| `pua_ready` is not ready | Unlock the phone, reconnect USB, then ask Claude to run `pua_setup` status / restart WDA |
| Signing or build error | Check your Apple team and a unique bundle ID in Xcode |
| Mirror is blank | Make sure `pua_ready` is `ready=true` first |

## Privacy

Anonymous usage statistics are on by default. They never include screenshots, typed text or device IDs. Disable with:

```sh
export IPHONE_USE_ANALYTICS=0
```

## Credits

Based on [zhongerxin/iPhone-use](https://github.com/zhongerxin/iPhone-use) (MIT) and Appium's WebDriverAgent. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Codex users can still install with `sh scripts/install.sh`.
