# GitHub device-flow login

**Action needed from Dylan:** authorize write access so Path C can land on `d6g8k5htny-coder/main`.

| Field | Value |
|-------|-------|
| Started (UTC) | 2026-09-24T05:49:16Z |
| Verification URL | https://github.com/login/device |
| User code | `FCD3-6B41` |
| Expires | ~15 minutes from start |

## Steps

1. Open **https://github.com/login/device**
2. Enter code **FCD3-6B41**
3. Approve the `gh` / GitHub CLI authorization (repo + workflow scopes)

The agent keeps a device-flow poller alive in tmux session `gh-device-login`. When authorization succeeds, it will attempt Path C land on main using the new user token (isolated `GH_CONFIG_DIR=/tmp/gh-dylan-auth`; existing cloud `gh` auth is untouched).

Scientific status / research lemma is **not** flipped by this flow.
