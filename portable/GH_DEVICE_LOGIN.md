# GitHub device-flow login

**Action needed from Dylan:** authorize write access so Path C can land on `d6g8k5htny-coder/main`.

| Field | Value |
|-------|-------|
| Started (UTC) | 2026-09-24T07:01:46Z |
| Checked (UTC) | 2026-09-24T07:08:30Z |
| Verification URL | https://github.com/login/device |
| User code | `2983-6CCD` |
| Prior code | `5816-A241` (expired) |
| Status | pending / authorization_pending (batch 138 poll) |
| Expires | ~seconds_left≈495 from check |

## Steps

1. Open **https://github.com/login/device**
2. Enter code **2983-6CCD**
3. Approve the `gh` / GitHub CLI authorization (repo + workflow scopes)

The agent keeps a device-flow poller alive in tmux session `gh-device-login`. When authorization succeeds, it will attempt Path C land on main using the new user token (isolated `GH_CONFIG_DIR=/tmp/gh-dylan-auth`; existing cloud `gh` auth is untouched). Batch 132+: `when_writable_land.py` also loads `/tmp/gh-dylan-auth/access_token` automatically.

If this Cloud Agent still cannot write after auth, or you prefer not to wait: land Path C locally from the release tarball in **one command** — see `portable/LAND.md` / `scripts/owner_land_path_c.sh --from-bundle`. Scope unblock options: `portable/RELAUNCH_WITH_MAIN_SCOPE.md`.

Scientific status / research lemma is **not** flipped by this flow.
