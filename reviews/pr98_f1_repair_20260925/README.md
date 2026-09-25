# PR98 F1 repair candidate — source-status transition enforcement

Author: OpenAI. Scope: F1 of mainPR98 review5839462657, coordinated by claim5839620207. This is an isolated source-bound PATCH CANDIDATE, not an edit to Cursor's branch, deployed admission mechanism, or mathematical acceptance.

## Actual change

The prior adapter attached HOLD/revalidation proposals but returned success even when the SOURCE was newly promoted or remained controlling after a changed dependency. The patch connects real source-status transition violations to `transition_ok=false` and a nonzero CLI exit in compare, compare-refs and event-compare. Explicit consistent demotion permits corrections. Grade/status channels are all checked; a false flag cannot hide a controlling grade, and a second status field cannot be hidden by an `or` expression.

There is deliberately no positive-acceptance import here. All newly controlling objects are refused, including leaves, until an independently specified authenticated acceptance interface exists. An unchanged legacy controlling object is not a new transition; its unresolved holds stay visible and are NOT retrospectively accepted. Thus this is loss-only change enforcement, not a full baseline scientific audit.

## Exact input and output

Subject repository d6g8k5htny-coder/main, immutable source776fdb75eb718293e296937c33eb77c228616a86.
Original adapter blob9b7cf55cfe2fbfe9a6aa6e9983f283a827b523ac, SHA25600a5af6734f6c89dc96253b75e7e0760cd4122eae76568655fed22adfd1281fa.
Patched adapter SHA256053128abfc91cd787963d4b9de95f833c5c0ac84a5d2b2c7ba9db70f3a2c540f.
Unchanged semantic_digest.py SHA256fa10c284c3f745188100d70a9e48c18388a48e4d212ddbf535dc9f2be262d3db.
New suite SHA25632038a994536087a6c60861e4287495adcef4401bc2c61bed296b8dee494d178.

`adapter.patch` applies only to tools/claims_gate_adapter.py (+79/-13). `enforcement_suite.py` is copied into the subject as tests/test_claims_gate_enforcement.py. It intentionally has a non-test filename here so the unrelated trial suite does not try to import a main-repository fixture. No old test is removed or weakened.

## Test-first evidence and reproduction

Before implementation the 21-test suite produced19 expected assertion failures and2 passing controls against the original source. After the patch,21 distinct tests pass in normal and optimized local Python3.13.5. Five semantic mutants are rejected by assertions in both modes. These include deleting the CLI refusal, ignoring affected controlling use, and incorrectly blocking legitimate demotion. Local complete-repository cloning was unavailable because DNS could not resolve github.com; the local fixture contains exact verified subject files, not a claimed complete checkout.

A read-only workflow checks out the actual immutable main repository, verifies base and patched hashes, runs the focused suite/mutations, installs the upstream hash-locked test dependencies, runs existing adapter/schema tests and then the FULL upstream pytest suite. Hosted success is pending until actual run/artifact readback. No full set of non-pytest CI commands is claimed by that workflow. Production source and scientific registers are never pushed or rewritten by the workflow.

To inspect/replay in a full checkout of the exact source:

    git apply --check /path/to/adapter.patch
    git apply /path/to/adapter.patch
    cp /path/to/enforcement_suite.py tests/test_claims_gate_enforcement.py
    python /path/to/run_validation.py --subject-root . --output /tmp/f1-new-evidence
    python -m pytest -q

Use a new output directory. Review exact outputs, not only a green workflow label.

## Remaining boundary

F2-F5 from the prior review are NOT repaired here: incomplete/multiple source-file binding, authority-context changes, mutable commit references, and duplicate/nonfinite JSON parsing. In particular F1 can only refuse an impact detected by the existing graph/source adapter. Missing source-impact detection remains a genuine blocker to main#90 closure. Path mode only checks supplied record semantics; it cannot establish source-file completeness. A reported safe transition is not theorem acceptance or branch-protection enforcement.

Nonauthor reviewer: challenge newly/retained controlling classification, all CLI entry points, grade/status conflicts, transitive edge deletion, demotion controls and untouched-source contracts. Return per-interface ACCEPT/AMEND with the exact patch/test digests. Because OpenAI wrote this correction, OpenAI test success is not the nonauthor acceptance of it. Keep draft pending review and broader regression evidence.

## Reconnaissance — bounded engineering source check, 2026-09-25

Inspected the actual PR98 source and executed review, plus GitHub's official exit-code and workflow documentation: https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes and https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax . The relevant established behavior is that a successful exit is not a failure signal; a diagnostic JSON field does not itself make the CLI fail. This supports wiring actual refusal to the process exit status. It does not establish the mathematical acceptance policy, a deployed required-check rule, or completeness of this adapter. The policy and exact failure case come from the owner campaign and original-constraint regression, not a claim of external novelty.
