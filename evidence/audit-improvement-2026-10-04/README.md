# Audit of the 495/1,500 to 1,000/1,000 improvement

The declared-domain campaign ([record](../task-domain-2026-10-03/README.md), PR #45)
passes every check that can be run from the repository and the raw archive. One
gap: the record holds the final before-and-after pass, not the individual fix
iterations, so it shows that the fixes hold but not how they were found.

Run: `python scripts/audit_domain_campaign.py` (the time-order and archive checks
need the raw archive named in `archive.json`; without it they are skipped).

| Check | Result |
| --- | --- |
| Corpus regenerates from its seeds to the registered manifest hash | Pass (`f8eb48ab…`) |
| Committed model and driver match the verification-freeze hashes | Pass (`3b85428d…`, `a726eebc…`), unchanged on main since PR #45 |
| Disagreement index holds every development failure | Pass: 506 rows = 11 directed + 495 random; all resolved |
| Development and reserved inputs are disjoint | Pass: 0 duplicates |
| Reserved agreement | Pass: 1,000/1,000, 0 excluded |
| Raw archive hash | Pass (`cdc750e1…`) |
| Reserved outputs written at or after the freeze | Pass: 3,002 files, 20:50:56–20:52:11Z; freeze recorded 20:50:56.24Z. File times have one-second resolution, so the first files share the freeze's second |

## Timeline from the archive (UTC, 2026-10-03)

| Time | Event |
| --- | --- |
| 20:42:32 | All 2,536 inputs generated: 36 directed, 1,500 development, 1,000 reserved |
| 20:43:18 | Registration: generator, config and corpus manifest hashes recorded |
| 20:43–20:48 | Directed and development runs, baseline and fixed model replays |
| 20:50:56 | Freeze: model, driver, native adapter and source-diff hashes recorded |
| 20:50:56–20:52:11 | Reserved set executed, fresh native process per sequence |

## What the record shows

Of 506 development disagreements, 346 came from the test adapter, 126 from the
model and 34 from both. The fixes were mode-eligibility handling in the adapter
and four model rules (position-accuracy gating by mode, delay seeding by takeover
option, action clearing, and shared-delay seeding), each traced to `failsafe.cpp`
or `framework.cpp`.

## Gap

The archive holds one consolidated pass: baseline and fixed outputs are both
produced within about five minutes of registration. The fix attempts that came
before are not recorded. Future campaigns should log each iteration (change,
failures cleared, failures introduced). The reusable process, including this
step, is the `reference-differential-improvement` skill in the owner's shared
skills folder.
