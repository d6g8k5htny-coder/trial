# PR98 combined successor adversarial review

Read-only OpenAI re-review of **main PR98 exact head 6e3f774f7ccfb5b760730698b1211dbff55ead13** after F1 was ported onto Cursor's F2-F5 successor. Scientific effect: NONE.

This does not edit PR98. It executes the actual adapter CLI against temporary Git repositories.

The review targets integration edges not covered by the current author tests:
1. crosswalk-owner changes must reverse-propagate to dependents;
2. controlling dependents must be refused after owner changes;
3. malformed *old* crosswalk/authority files must not be swallowed as "absent schema";
4. cross-repository source_bindings must not silently bind same-path local files;
5. strict claims JSON and normal local source binding stay as controls.

A green review harness means these expected adverse observations reproduced in both normal and optimized Python modes. It is not an admission or theorem verdict. If any hypothesis is wrong, the workflow is expected to fail and the raw per-case JSON is retained for correction.

No source-of-truth status, Drive file, Vault99 object, or author branch is modified.
