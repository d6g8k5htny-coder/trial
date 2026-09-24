# GitHub device-flow login

**Action needed from Dylan:** authorize write access so Path C can land on `d6g8k5htny-coder/main`.

| Field | Value |
|-------|-------|
| Started (UTC) | 2026-09-24T07:16:30Z |
| Checked (UTC) | 2026-09-24T07:19:51Z |
| Verification URL | https://github.com/login/device |
| User code | `F11F-5064` |
| Prior code | `2983-6CCD` (expired) |
| Status | pending (batch 139 renew after expiry) |
| Expires | ~seconds_left≈753 from check |

## Steps

1. Open **https://github.com/login/device**
2. Enter code **F11F-5064**
3. Approve the `gh` / GitHub CLI authorization (repo + workflow scopes)

The agent keeps a device-flow poller alive in tmux session `gh-device-login`. When authorization succeeds, it will attempt Path C land on main using the new user token (isolated `GH_CONFIG_DIR=/tmp/gh-dylan-auth`; existing cloud `gh` auth is untouched). Batch 132+: `when_writable_land.py` also loads `/tmp/gh-dylan-auth/access_token` automatically.

If this Cloud Agent still cannot write after auth, or you prefer not to wait: land Path C locally from the release tarball in **one command** — see `portable/LAND.md` / `scripts/owner_land_path_c.sh --from-bundle`. Scope unblock options: `portable/RELAUNCH_WITH_MAIN_SCOPE.md`. Batch 139+: once trial secret `MAIN_PUSH_TOKEN` exists, `scripts/dispatch_land_path_c.sh --apply` fires `repository_dispatch` type `land-path-c-on-main` (ghs Contents write; no Actions:write needed).

Scientific status / research lemma is **not** flipped by this flow.
