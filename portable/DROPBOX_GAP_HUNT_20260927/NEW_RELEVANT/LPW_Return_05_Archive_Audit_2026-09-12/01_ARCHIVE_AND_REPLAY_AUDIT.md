# LPW-05 intake and replay audit

## A. Outer upload and every nested ZIP

`SepOKComputer_Project_Gap_Closure.zip`: 25,269,465 bytes; SHA-256 `07b44ac2537e7288eaa21decfec04bfa924c6181ba6b4179d34cc078ddc3f139`; 909 regular entries; 67,409,396 uncompressed bytes. No duplicate archive paths, unsafe traversal, absolute paths, encrypted members, symlinks, or special-file entries were accepted.

The recursive ledger has 12 archive occurrences (including the outer ZIP), 11 distinct archive hashes. The repeated original Q0 distribution is byte-identical; it was opened and CRC-tested as well. Four older KIMI_EXPORT ZIPs and the nested author-side Return-03/original-Q0 archives were also opened. This is an archive/custody audit, not a claim to have reproved every historical mathematical document.

| Current archive | Bytes | SHA-256 | Regular files including manifest | Manifest payloads |
|---|---:|---|---:|---:|
| KIMI_LPW_REVIEW_BUNDLE_2026-09-13.zip | 97,963 | b7e5cbf33fa883e9789be99b6b965d42ed4ed653a1a9dde257ad1587b5c22f8e | 38 | 37/37 match |
| KIMI_QC_NUMERICAL_PACKAGE.zip | 97,671 | 2f99252ed8acc97ccee468bbcb2419eac214156720bbc78ecdebb3f753e69ea7 | 20 | 19/19 match |
| KIMI_LPW_CONSTANT_PACKAGE.zip | 33,844 | ed9da9b4ffa099270c9a1c3467b78be325f99c3baa37b395a06d33114b6b1a01 | 10 | 9/9 match |
| KIMI_W8_V3_PACKAGE.zip | 58,851 | 6d7b0ed5de12082ad540c6f28a61efde90cc414a01fd780cc5e313377c207410 | 18 | 17/17 match |

The corresponding current files in the larger tree are separately inventoried. A historical K3 root manifest is not a final seal of the newer tree: 247 of its 266 entries match the received tree; 19 differ. Its omissions and other historical manifest residues are enumerated in `receipts/MANIFEST_AUDIT.json`. These old-tree discrepancies do not invalidate the fresh four package manifests. Do not claim that every historical manifest in the outer ZIP passes.

## B. Exact verdict identity and the six-byte extraction discrepancy

The received verdict is 9,219 bytes, whole-file SHA-256:

`04bcbdf2013d83b149a8933a332a078c303af347335ee40f154f37ba195ad448`.

That corrected full-file digest matches exactly.

The README's declared rule is to hash the entire byte prefix before the unique marker line. That marker starts at byte 9,090. The SHA-256 of exactly those 9,090 bytes is:

`17863be2e9fedc4ddc6517562c501a609fa4fa3579f8dad1348fb67f68a9c5bd`.

It is NOT the printed body digest `d399e28378d177f88d08032c81f1573f35c9af2b600b9b775ebfe40f555cbbad`.

The latter DOES match the first 9,084 bytes. The six bytes between offsets 9,084 and 9,090 are exactly `\n---\n\n` (LF, three hyphens, LF, LF). Thus the mismatch is localized: the recorded body digest excludes a separator that the declared exact-prefix rule includes.

**Required repair:** preserve the original verdict; issue an additive custody correction specifying either (a) the 9,090-byte exact-prefix digest above, or (b) an explicit 9,084-byte body rule excluding that precise separator. Do not silently change the rule, rewrite the frozen file, or pretend corruption of the entire delivered archive. Both byte objects and all evidence are present.

Addenda 1–3, the lead fallback analytic review, and the lead constant review match their own exact-prefix declared body hashes. Full details are in `BODY_HASH_AUDIT.json`.

## C. Source-exact program replays

The following seven programs were inspected for dependencies and side effects, then run from isolated copies in ordinary and optimized Python. All 14 top-level runs exited zero; stdout was byte-identical to each delivered reference; stderr was empty.

| Program | Reproduced stdout SHA-256 |
|---|---|
| lpw_constant.py | d0cb92595bad7e1b7266e1a9043a54caff380ed075e8f4e358b0ae04146c573f |
| falsify.py | 34df591195053d940bd50bd5e411f953a1f3443ef95997a2c239f9373d41e746 |
| RB_R2_part1_symbolic.py | ff2da6a065401aedb428bf6f4f38f21c5044e1fadb648385e3ebd215a70ef73f |
| rd_r4r5_verify.py | 45f4d4718d917c1ead7a8a014d6c7e51c8be7f9758b492b64d654bb92731397d |
| rc_r3_numeric.py | ba14804930a7ae7bcee64cdb90c0ada10f0961f2dd290ce88520c51a5b7c15ec |
| rb_r2_part2_spectral_v2.py | 40e370b4cbfc123b9033f5b402214c907461763b408c33407bbf31d52d992677 |
| qc_return03_numeric.py | 3311b40f22a6284fdb9ba14c37174f38c2a4da8385add93d1e6082dc0f1cbdd1 |

The QC output really contains 335 checks and describes itself as numeric evidence, not a proof of the all-r analytic statements. The constant falsifier really runs the four supplied mutations in both modes. These successes are retained even though the independent checks in the next document identify defects that the delivered suite does not test.

RA's report with embedded transcript is present. No original standalone RA script is represented as recovered. The previously erroneous RB rung script is preserved as superseded evidence and was not used as the current numeric route.

## D. W8: conditional evidence, terminal failure, and missing input recovered

The W8 v3 transcript pair is byte-identical at hash `5e19da35a08fb737ce59b3dffb5453d19193931fc7c14803aa243985d54bf113`. It records improved rung stability and an H-B3-conditional limit-object lower value near 0.403716209750. It then ends with `FAIL-CLOSED TRIGGER: used core spacing violates kill condition at floor margin`. The supplied identity stamp records nonzero exits. This is not a fully passing, premise-free or finite-r certificate.

The required file `c027 sweep core40.json` was absent by both filename and SHA-256 from the supplied outer archive and the current W8 subarchive. It was recovered from Drive ID `1cVez6js8qbeigoS8f1BKqlmNKZiKtgfj`: 7,533 bytes, SHA-256 `0003756d4075bbfa881edfeac68d6cca7242c54cee2c551f2814fd57759b4c18`, exactly matching the script's embedded input hash.

An unchanged-source preflight with `SWEEP_JSON_PATH` set to this recovered file passed the input integrity, kernel, archived station comparison, and symmetry portions before a declared 30-second stop at the grid. The complete sweep was not reproduced. A timeout is not a refutation or a PASS. Both the initial missing-input failure and the subsequent recovered-input preflight are preserved.

## E. Independence and authority

These are author-side replays after exposure to Kimi's results. They establish reproduction and allow direct scrutiny; they do not create another independent provider family. No file in the received sources was edited. No Drive write or program-status transition was executed.
