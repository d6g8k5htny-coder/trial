# GitHub device-flow login

**Action needed from Dylan:** authorize write access so Path C can land on `d6g8k5htny-coder/main`.

| Field | Value |
|-------|-------|
| Started (UTC) | 2026-09-24T06:45:53Z |
| Checked (UTC) | 2026-09-24T06:54:00Z |
| Verification URL | https://github.com/login/device |
| User code | `5816-A241` |
| Prior code | `7D13-0E6D` (expired) |
| Status | pending / authorization_pending (batch 137 poll) |
| Expires | ~seconds_left≈420 from check |

## Steps

1. Open **https://github.com/login/device**
2. Enter code **5816-A241**
3. Approve the `gh` / GitHub CLI authorization (repo + workflow scopes)

The agent keeps a device-flow poller alive in tmux session `gh-device-login`. When authorization succeeds, it will attempt Path C land on main using the new user token (isolated `GH_CONFIG_DIR=/tmp/gh-dylan-auth`; existing cloud `gh` auth is untouched). Batch 132+: `when_writable_land.py` also loads `/tmp/gh-dylan-auth/access_token` automatically.

If this Cloud Agent still cannot write after auth, or you prefer not to wait: land Path C locally from the release tarball in **one command** — see `portable/LAND.md` / `scripts/owner_land_path_c.sh --from-bundle`. Scope unblock options: `portable/RELAUNCH_WITH_MAIN_SCOPE.md`.

Scientific status / research lemma is **not** flipped by this flow.
