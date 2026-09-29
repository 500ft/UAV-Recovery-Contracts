# The first differential: model against PX4's real Failsafe class — 2026-09-29

Layer A (`model/px4_failsafe.py`) against layer B (the `Failsafe` class PX4 ships) on identical input sequences.
The adapter constructs the real class, sets parameters through PX4's own parameter store, and calls `update()` as
commander does. It does not reimplement the selector.

**Evidence state: executed, pinned.** Runs on the pinned commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`,
`ubuntu-24.04`, `c++ 13.3.0`. This is not an independent safety oracle: the real class is the implementation
under study.

## Result

| | first run | second run |
|---|---|---|
| model | as it was | corrected |
| sequences | 9 | 11 |
| exact agreement, update for update | 7 | **11** |
| adapter binary sha256 | see `first-run-before-model-fix/` | `5109c84e4f63ec242d6c8613ad1dd8125fb4f0228f08632eceaacd70c889e93a` |
| CSV lines recorded from the real class | 6,261 | 6,365, in `second-run/oracle/` (each file has one header line) |

Both runs are kept. The first is the historical record of how the defect was found and is not tidied away.

## What the first run found

Seven sequences agreed exactly. The two clear-and-re-raise sequences (4 and 4b) disagreed by **exactly one update
period, at both 100 ms and 10 ms**, so the gap scaled with the step. The real class acted later than the model in
the second episode.

I had suspected the cause from reading `FailsafeBase::update()` before the result arrived, and the result
confirmed it:

- The model fed `updateStartDelay` the **previous** update's delayed status. The source passes the **current**
  update's `delayed_action`, computed a few lines earlier in the same call.
- The model seeded a new delay from the pot **before** the elapsed time was taken off it. The source seeds inside
  `checkStateAndMode`, after `updateDelay`.
- The model accumulated float seconds. Whether the first RTL landed at 5.0 or 5.1 s depended on rounding, where
  the source uses integer microseconds and integer `dt / 4`.

The model now runs in the source's order with integer microseconds. Re-comparing the corrected model against the
first run's **already recorded** real output gave 9 of 9 exact before the second CI run was even dispatched, and
the second run then confirmed it on 11. The recorded real output does not depend on the model, so this was not the
model being tuned toward its own answer.

## A claim of mine that this retracts

Beside the model, and in a study guide, I wrote that the discrete stepper "lands one update late" and that the
real framework "has the same dependence on its own update period." It does not. The figures I quoted, 2.600,
2.510 and 2.501 s at three step sizes, were the bug. The corrected model returns exactly 2.5 s at every step size,
and the real class agrees with it.

## What agreement establishes, and what it does not

**Establishes.** On the selected-action timeline, the model reproduces the real class exactly on eleven sequences
covering: a disabled action, a delayed response, a zero delay, both sides of the 0.1 s delay threshold, a partial
refill after a short gap, a capped refill after a long gap, a second hazard arriving during a running delay, and a
latched action persisting after its condition clears. The partial-refill and capped-refill sequences are the ones
a wrong recharge divisor would have broken.

**Does not establish.**

- **The pot's value.** It is private to the class. Only its effect on when the action changes was observed, so an
  error in the drain that is offset by an equal error in the refill would not have shown.
- **The exact 0.1 s boundary.** 0.05 s and 0.15 s were probed. 0.10 s was not.
- **Anything outside the domain the sequences cover.** No mode-requirement fallback, no user takeover, no
  deferral, one vehicle type, all-zero flag structures so Hold can always run. The model takes takeover and
  hold-can-run as inputs and the real class derives them.
- **Anything about the integrated runtime.** That is layer C. The missing recovery in the flown runs is
  unexplained by this result.

## What it does change about the open question

The selector logic, as exercised here, does what the model says, and PX4's own nine unit tests pass. So the
selector is now the **least** likely location of the missing recovery, on this domain. That points at the
integration: whether `checkStateAndMode` runs in the flown autopilot, and whether it consumes the armed state and
flags that are logged. It is an inference about where to look, not a diagnosis, and the supported statement is
unchanged: no expected post-injection recovery-mode transition was observed and no new failsafe announcement was
seen; the internal selected action and its cause remain unresolved.

## Identity of what ran

The adapter is test code added to the pinned tree, not a firmware change, but it does change the tree.
`second-run/instrumentation.patch` is the exact patch, `second-run/adapter.sha256` hashes the adapter source, and
the binary hash above differs from the upstream test binary's
(`682696ce5168d1ad74ceb252b738eb6ba981f5dc4ddd7c3a78fb31172e976991`) because it is a different executable.

## Reproducing

```bash
gh workflow run native-failsafe-oracle      # runs both the upstream tests and the differential job
python -m unittest tests.test_differential  # offline: the model against the recorded real output
```

`tests/test_differential.py` keeps the model matching the recorded real behaviour without needing the C++ build.
`checksums.json` covers every file in this directory.
