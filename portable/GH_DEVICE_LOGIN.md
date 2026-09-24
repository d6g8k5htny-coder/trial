# GitHub device-flow login

**Action needed from Dylan:** authorize write access so Path C can land on `d6g8k5htny-coder/main`.

| Field | Value |
|-------|-------|
| Started (UTC) | 2026-09-24T06:24:55Z |
| Checked (UTC) | 2026-09-24T06:24:55Z |
| Verification URL | https://github.com/login/device |
| User code | `7D13-0E6D` |
| Prior code | `91D3-D72C` (expired) |
| Status | pending / authorization_pending (batch 132 renew) |
| Expires | ~seconds_left≈899 from check |

## Steps

1. Open **https://github.com/login/device**
2. Enter code **7D13-0E6D**
3. Approve the `gh` / GitHub CLI authorization (repo + workflow scopes)

The agent keeps a device-flow poller alive in tmux session `gh-device-login`. When authorization succeeds, it will attempt Path C land on main using the new user token (isolated `GH_CONFIG_DIR=/tmp/gh-dylan-auth`; existing cloud `gh` auth is untouched). Batch 132: `when_writable_land.py` also loads `/tmp/gh-dylan-auth/access_token` automatically.

Scientific status / research lemma is **not** flipped by this flow.
