# Final PR98 gate re-review — cc6a578

Read-only OpenAI engineering review of main PR98 exact head `cc6a578b26f14a16025f4c955fe5efdd65890b1f`, adapter SHA256 `2213ca74a3b5fd74fcbbd915c324adc7660ca04a5f9a2e146499a64dff48b85e`.

This successor specifically tests the previously failing integration boundaries after repairs A–E and the precision-upgrade follow-up. It does **not** edit PR98, create positive scientific admission, or review any theorem.

Eleven independent synthetic-Git scenarios are executed against the real CLI in normal and optimized Python modes:
- authority-owner reverse propagation;
- controlling consumer refusal under owner drift;
- malformed historical crosswalk refusal;
- cross-repository binding refusal;
- strict duplicate claims JSON;
- second-binding-only source drift;
- frozen scientific-body extraction with wrapper-only noise;
- scientific-body drift / expected-hash mismatch;
- informational carrier noise excluded from scientific coverage;
- stale freshness fail-closed;
- same-carrier precision upgrade admitted only as a coverage repair.

The actual tip-health command is also executed. A green workflow means these engineering safety properties reproduced on this immutable source; it does not grant scientific acceptance or independently prove organizational lineage.

Known boundary retained even on success: `external_sync_obligation` means GitHub monitors the synchronized repo mirror/scientific object only. It does not watch Google Drive live. Main #90 should be closed only at the engineering obligation scope after exact-head review/CI and whatever integration step its owner requires; no mathematical status follows.
