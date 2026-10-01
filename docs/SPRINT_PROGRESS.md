# Progress log

What changed and when, newest first, one line per change that matters. The
plan is in the [roadmap](../ROADMAP.md). The earlier, longer version of this
log is kept at
[commit 236c62b](https://github.com/500ft/uav-failsafe-composition/blob/236c62b0cd796592a38454a19fd87fd3901447f9/docs/SPRINT_PROGRESS.md).

## Week of 2026-09-28

- **09-30** Study A decisions signed off (owner-delegated). D7 and D9 stand
  as replaced on 09-25; five injectable event classes (no RC source); model
  checking deferred. The protocol gained a dated §7b amendment before any
  confirmation run.
- **09-30** One roadmap: the finish line is Study A judged by the D7 coverage
  gate, PX4 only. README rewritten
  ([#41](https://github.com/500ft/uav-failsafe-composition/pull/41)).
- **09-30** SITL failsafes restored. The harness had been sending integer PX4
  parameters as floats, so PX4 read a nonsense action setting and chose "none".
  With the encoding fixed, a datalink loss in Auto Loiter gives Hold, then RTL
  16.4–16.7 s later, also on the unmodified binary
  ([#40](https://github.com/500ft/uav-failsafe-composition/pull/40)).
- **09-29** The Python model and PX4's compiled `Failsafe` class agree on 11 of
  11 input sequences. The first comparison agreed on 7 of 9 and exposed an
  ordering bug in the model
  ([#34](https://github.com/500ft/uav-failsafe-composition/pull/34)).

## Week of 2026-09-21

- **09-26** PX4's own failsafe test binary built and ran all 9 declared cases
  on GitHub Actions, settling where the oracle runs (decision D14). Literature
  intent audit finished ([#32](https://github.com/500ft/uav-failsafe-composition/pull/32)).
- **09-26** Every consequential number given a source, a limit and a check
  ([#31](https://github.com/500ft/uav-failsafe-composition/pull/31)).
  Configuration identities, property contracts and the shared hold-delay logic
  ([#30](https://github.com/500ft/uav-failsafe-composition/pull/30)).
- **09-24 to 09-26** The observation chain was repaired before continuing the
  diagnosis, then four remaining gaps closed
  ([#28](https://github.com/500ft/uav-failsafe-composition/pull/28),
  [#29](https://github.com/500ft/uav-failsafe-composition/pull/29)).
- **09-24** Ruled out Offboard mode as the reason no failsafe fired
  ([#27](https://github.com/500ft/uav-failsafe-composition/pull/27)).
- **09-22** No failsafe action for any hazard tried; the campaign was held
  ([#26](https://github.com/500ft/uav-failsafe-composition/pull/26)). The cause
  turned out to be the parameter encoding fixed in #40.
- **09-22** First injection run: datalink loss produced no failsafe, against
  the prediction ([#20](https://github.com/500ft/uav-failsafe-composition/pull/20)).
  Test runner built, arming fixed and timing jitter measured
  ([#19](https://github.com/500ft/uav-failsafe-composition/pull/19)).
  Reading list organised by research question
  ([#21](https://github.com/500ft/uav-failsafe-composition/pull/21)).
- **09-20** Study A day 1: contracts frozen and the simulator rig recorded
  ([#18](https://github.com/500ft/uav-failsafe-composition/pull/18)).

## Week of 2026-09-14

- **09-16** Formal-composition programme proposed: extract a model of PX4's
  failsafe logic and check it against PX4
  ([#16](https://github.com/500ft/uav-failsafe-composition/pull/16)).
  Repository audit of links and stale entries
  ([#17](https://github.com/500ft/uav-failsafe-composition/pull/17)).
- **09-15 to 09-16** Prior-art closeout. The novelty question stays partly
  open with 17 intake records unread
  ([#14](https://github.com/500ft/uav-failsafe-composition/pull/14),
  [#15](https://github.com/500ft/uav-failsafe-composition/pull/15); plans
  [#12](https://github.com/500ft/uav-failsafe-composition/pull/12),
  [#13](https://github.com/500ft/uav-failsafe-composition/pull/13)).
- **09-14** Scripts and tests simplified
  ([#11](https://github.com/500ft/uav-failsafe-composition/pull/11)).

## Week of 2026-09-07

- **09-13** Reference coverage: the clean database export recovers 3 of 6
  known sources; the record was tightened twice
  ([#8](https://github.com/500ft/uav-failsafe-composition/pull/8),
  [#9](https://github.com/500ft/uav-failsafe-composition/pull/9),
  [#10](https://github.com/500ft/uav-failsafe-composition/pull/10)).
- **09-12 to 09-16** Literature database export re-acquired with a clean query
  log ([#7](https://github.com/500ft/uav-failsafe-composition/pull/7),
  [#6](https://github.com/500ft/uav-failsafe-composition/pull/6)).
- **09-11** README and presentation rewrite
  ([#5](https://github.com/500ft/uav-failsafe-composition/pull/5)).
- **09-09 to 09-10** Search provenance corrected and the recall claim
  withdrawn; the novelty claim narrowed
  ([#3](https://github.com/500ft/uav-failsafe-composition/pull/3),
  [#4](https://github.com/500ft/uav-failsafe-composition/pull/4)). First
  experiment scoped ([#2](https://github.com/500ft/uav-failsafe-composition/pull/2)).
- **09-07** Research question, configuration schema and claim ledger set up
  ([#1](https://github.com/500ft/uav-failsafe-composition/pull/1)).
