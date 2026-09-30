# Runtime diagnosis and restored RTL response

The missing response in the reproduced Auto Loiter datalink-loss case came from
the runner's integer parameter transport. The real failsafe class consumed a
float's bit pattern as an integer action setting, which fell through PX4's action
mapping to `None`. Correcting the bytewise transport restored Hold then RTL.
The corrected runner also produced RTL on the original uninstrumented binary.

[results.json](results.json) is the canonical home for measured values, counts,
timestamps, mode transitions, binary identities and artifact hashes. Reproduce it:

```sh
python evidence/task-runtime-2026-09-29/analyze.py
```

## Evidence and mechanism

The baseline and initial instrumented runs use the previous transport. Both
completed valid captures without the expected recovery. Internal observations in
`runs.instrumented` show the consumed action setting and selected action; the
reported MAVLink readback still appeared to match the request. That apparent
agreement was the bug, not independent confirmation of configuration.

The pinned receiver copies the PARAM_SET float bytes directly into typed storage,
and explicit reads and broadcasts both call the same bytewise `send_param()`:
[receiver and read dispatch](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_parameters.cpp#L129),
[readback encoding](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_parameters.cpp#L486).
An out-of-range action setting maps to `None` in
[fromNavDllOrRclActParam](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/failsafe/failsafe.cpp#L43).

The old runner sent a numeric float for an integer setting, then interpreted a
numeric-looking reply as the intended value. Its magnitude heuristic concealed
the same encoding error on readback. The repaired runner first obtains the
vehicle's parameter type and uses that type for both encoding and decoding.
It rejects unsupported types and integer values that cannot be transported
without changing their bytes. It no longer chooses a type from a Python literal.

The `corrected-instrumented` capture records the intended effective parameter,
eligible consumed flag, pending Hold, selected RTL and committed navigation mode.
The `corrected-original-binary` capture repeats the response without logging
instrumentation; its binary identity matches `baseline-authorized`.
The complete mode sequence includes landing and disarming after RTL, preserved
in the traces and console logs rather than discarded to make a timeline pass.

## Reproduction and retained attempts

[environment.json](environment.json) records commands, source identities, build
environment and experiment order. Apply
[the observation patch](../../oracle/runtime-observation.patch) to the pinned
clean PX4 tree, build using the recorded command, and execute the run command
with a new output directory. The runner saves the tracked source diff with the
binary identity. The patch changes logging and names the existing update-time
argument; it does not change selection, flags or parameters. Each call's records
are joined in log order at the shared update time, since lockstep can repeat a
clock value across calls.

The first logger format exceeded PX4's log-line limit. Its original patch and
capture remain in the packet; absent fields are unknown. Shorter records in the
final patch preserve the complete tuple. No first-attempt log was overwritten.
The initial sandbox refusal is also retained; it never launched the simulator.
Raw telemetry, native logs and autopilot logs are compressed without modification.
The original cache source and executable were restored after the experiment.

## Scope and remaining work

This executes the closeout plan's runtime diagnostic and closes NP-8 for the
reproduced domain. It establishes a harness configuration defect, not a PX4
selector defect. Other historical cases remain historical observations of a
misconfigured apparatus; they are not silently relabelled as valid conformance
trials. The repair affects all integer overrides together, so the experiment is
not a single-parameter intervention. This is development evidence, not held-out
confirmation or a complete interaction study.

The injection stamp remains a cached lower bound. The native flag-to-selection
interval is directly observed, but it does not calibrate injection latency or
close Q-RESIDUAL. The full parameter snapshot, detector timing investigation,
matched interaction pilot and symbolic checking retain their existing gates.
The old timeline verifier does not model the complete post-landing sequence;
no whole-run conformance pass is claimed here.

The earlier WP1–WP4 work and native differential are already merged. Under the
owner's scope rule this PR carries executed data and the resulting repair; the
unfinished speculative observer/cohort extensions were set aside outside the
repository. Offline checks and CI validate this implementation, with the real
packet exercised by `tests/test_runtime_evidence.py`.
