# Roadmap

## Disposition and finish line

This failsafe repository remains paused. Its finish is the owner's explicit
choice to release the scoped benchmark or close the unfinished study, followed
by the corresponding reviewed action. No release, closure or restart is
implied by this cleanup. The [decision record](docs/decision-log.md) records
the adopted software direction and the [history index](history/README.md)
locates the prior study and its unresolved gates.

The successor asks which deployment defects remain after a costed back-to-back
comparison, and which extra checks catch them at what marginal cost. Its
implementation is in local staging `control-code-verification`, with its own
roadmap. Deployment code does not live here; a public name remains pending.

## Verified work and current dependencies

| State | Work | Prerequisites | Completion evidence |
| --- | --- | --- | --- |
| Done, scoped | Preserve Python/native failsafe comparison and runtime observations | Pinned source, declared inputs and retained raw records | [Result index](results/README.md), including corpus exclusions and reproduction commands |
| Done, local successor | Numerical filter qualification | Explicit state/reset/dt semantics, units, types, domain and derived error bounds before comparisons | Successor `spec.json`, `registration.json`, `NUMERICS.md` and `evidence/results.json`; development agreement only |
| Current, owner-blocked | Decide old-study disposition and successor publication | Owner release/closure choice and public-name authorization | Recorded decisions, then a separately authorized release/closure or publication; none has occurred |
| Current, successor-blocked | Review functional branch requirements | Assigned second reviewer and the recorded threshold-uncertainty cases | Reviewed branch-use requirements before an integration wrapper is qualified |

## Conditional successor order

These are dependencies for the local successor, not active failsafe campaigns.
Its roadmap owns the executable tasks and detailed completion criteria.

1. **Setup and generator qualification.** Use the existing local result as the
   starting point. A public remote needs name approval; CI needs a reproducible
   toolchain. Any additional precision path needs its own inspected generated
   types, flags and reference checks. Firmware is selected through actual
   support and replay qualification, rather than inheriting this study's pin.
2. **Reference-qualified controller.** Requires explicit requirements and
   branch decisions. Finish with independent analytic checks, numerical bounds
   and common registered traces across higher-precision intent, float32 and C.
3. **Reviewed wrapper and comparison boundaries.** Requires the core and
   reviewer sign-off. Finish with numerical-step, stateful, message and SITL
   results, independent requirements checks and known-defect detection. Reusing
   this harness first requires checking what it actually implements. Replay
   additionally needs complete topics, initialized state, timestamp semantics,
   controlled publishers and a known-good repeat. It establishes no hardware timing guarantee.
4. **Defect corpus, then pilot.** Requires qualified comparisons and independently
   motivated defect labels. Finish with retained failures, applicability and
   cost records; then paired discordance and module variation sufficient to
   design confirmation. Proposed corpus sizes are targets, not sample-size
   justifications. Generation and verification remain separate factors.
5. **Registered confirmation.** Requires pilot-based design, reviewed requirements
   and frozen code, controller/defect holdouts and final inputs before exposure.
   Finish with classified outcomes and uncertainty at the independent-port level.
   Deterministic repeats and time samples do not increase the sample size.

## If the old study resumes

A restart requires explicit authorization. Missing mechanism inputs and adapters,
the full D25 cell list and a frozen comparison must precede Study A confirmation.
D7 and the signed [protocol](docs/specs/formal-composition/study-a-protocol.md)
still apply. Public-log exclusions and open injection timing remain limitations.
Physical testing, hardware timing guarantees, purchases, funding and publication require
their own evidence and owner decisions.
