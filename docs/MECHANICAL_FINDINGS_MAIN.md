# Mechanical findings from local clone of `d6g8k5htny-coder/main`

Clone tip audited: `cursor/inventable-jetmod-probes-4488` @ `ae94270d5f48d4c171f134efcea5058997966d71`
Host: CPython 3.11.16 (uv) + pytest 9.1.1
**Scientific effect: NONE.**

## Green

| Check | Result |
|-------|--------|
| `python tools/math_status_check.py` | `problems=0` disposition `OPEN_HOLD`; `lemma_closed=false` |
| `tests/test_math_status.py` + inventable probes | 18 passed |
| claims / registers / provenance / ci_pins / math_status slice | 152 passed |
| bridge + operations + workflows + run_checks (partial) | 891 passed, 1 error |

## Environment flake (not a research defect)

`tests/test_run_checks.py::test_any_input_mutation_prevents_pass[tests/test_tiny.py]` errored in fixture setup when `git commit` hit a **10s timeout** on this VM (`subprocess.TimeoutExpired`). Re-run locally on a normal disk before treating as a product bug. No portable patch filed.

## Not bugs (do not “fix”)

- `OBL-H5-JETMOD` OPEN / inventable REFUSED+EMPTY+ABSENT receipts — correct fail-closed behavior.
- `D3-LEMMA-RN-UNIF` OPEN — correct.
- Default-branch complexity-physics face — product misalignment; portable Option-B pack is under `portable/main-default-branch/`.

## Write access

This agent still cannot push to `main` (`cursor[bot]` 403). Engineering patches that belong on the research tree must wait for a write-enabled environment on that repo.
