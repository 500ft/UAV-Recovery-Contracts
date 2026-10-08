# Contributing

Contributions should make the research easier to audit, reproduce, or falsify.

## Evidence rules

- Label every artifact as `literature`, `planned`, `simulation`, `HITL`, or `measured`.
- Do not convert a planned threshold into a result.
- Pin firmware versions, parameter files, airframe identity, and test-environment metadata for every trace.
- Keep generated outputs out of the repository until their generator and input provenance are documented.
- Preserve negative results and failed hypotheses.
- Do not use “safe,” “validated,” or “guaranteed” without evidence explicitly supporting that scope.

## Before opening a pull request

```bash
python scripts/check_repo_contract.py
python -m unittest discover -s tests -v
python scripts/acquisition_ledger.py --check
python scripts/reference_coverage.py --check
python evidence/task-2026-09-09/rerun_search.py --audit evidence/task-2026-09-11-public/database-export.json
python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition
python tools/test_presentation.py
git diff --check
```

Physical experiments additionally require approval from the responsible laboratory or facility. A contribution to this repository is not flight authorization.

## Public disclosure boundary

This is a public repository. Before contributing potentially enabling control, hardware, or
configuration detail that may be intended for patent protection, complete
[`XC-02`](https://github.com/500ft/uav-failsafe-composition/blob/cdb7b36d01085527529fde3bead4543c1e038e43/docs/TASKS.md#xc-02--record-the-publication-and-disclosure-path-before-adding-implementation-sensitive-detail)
and obtain appropriate guidance. NYU-affiliated contributors can start with
[Technology Opportunities &amp; Ventures](https://tov.med.nyu.edu/for-innovators/intellectual-property-101/).
This repository does not provide legal advice.
