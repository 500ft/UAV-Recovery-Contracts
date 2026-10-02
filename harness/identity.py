"""Three identities, kept apart, because they answer three different questions (owner review 2026-09-25, WP1).

    scenario_id    what was ASKED FOR. Computable before launch, from the case alone.
    execution_id   what a particular attempt ACTUALLY DID. Needs the vehicle, so it exists only after a run.
    analysis_id    how a set of raw bytes was INTERPRETED. Changes when the normaliser or the contract changes,
                   while the execution and the raw bytes it describes stay exactly as they were.

The earlier `parameters_sha256` tried to be the first and the second at once, which cannot work: a case cannot
be selected by the hash of a readback that does not exist until the vehicle is up. Splitting them also fixes a
quieter problem. The override hash covers only explicitly set parameters. It is named
`overrides_readback_sha256` and remains incomplete. Full parameter captures, when available,
have separate file hashes and completeness records in `parameter_snapshots`.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

SCENARIO_SCHEMA = "scenario/2026-09-25"
EXECUTION_SCHEMA = "execution/2026-09-25"
ANALYSIS_SCHEMA = "analysis/2026-09-25"
# Bumped whenever the normaliser changes how it reads the same bytes, so a re-derivation is distinguishable.
NORMALISER_REVISION = "2026-09-25-open-upper-bound"
UNKNOWN = "unknown"


def _ms(seconds) -> int | None:
    """Times are hashed as whole milliseconds. 40.0 and 40.000000001 are the same schedule; float text is not."""
    return None if seconds is None else int(round(float(seconds) * 1000))


def digest(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scenario(case: dict, *, intended_mode: str, restore_after_s: float = 0.0,
             applied_overrides: dict | None = None) -> dict:
    """The canonical description of what was requested. Key order never matters; every value is typed."""
    overrides = applied_overrides if applied_overrides is not None else case.get("parameters", {})
    body = dict(
        schema=SCENARIO_SCHEMA,
        firmware=dict(commit=case["firmware_commit"], tag=case["firmware_tag"]),
        vehicle=dict(airframe=case["airframe"], simulator="sihsim", lockstep=True),
        configuration_id=case["configuration_id"],
        intended_mode=intended_mode,
        schedule=dict(
            event=case["event"],
            # A seed label is not a schedule. The offset it stands for is what actually varies.
            seed=int(case["seed"]),
            inject_at_vehicle_ms=_ms(case["inject_at_vehicle_s"]),
            restore_after_ms=_ms(restore_after_s),
            horizon_ms=_ms(case["horizon_s"]),
            time_origin="vehicle clock, the runner's held telemetry stamp (D6, D23)"),
        requested_overrides={k: float(v) for k, v in sorted(overrides.items())})
    return dict(body, scenario_id=digest(body))


def execution(scenario_id: str, *, repeat: str, executable_sha256: str | None,
              build: dict | None, overrides_readback: dict | None,
              realized_events: dict | None, raw_artifacts: dict | None,
              parameter_snapshots: dict | None = None) -> dict:
    """What one attempt did. Every component that was not captured is `unknown`, never defaulted or invented."""
    readback = None if overrides_readback is None else {k: float(v) for k, v in sorted(overrides_readback.items())}
    body = dict(
        schema=EXECUTION_SCHEMA,
        scenario_id=scenario_id,
        # A scenario has many repeats and none of them overwrites another.
        repeat=repeat,
        executable_sha256=executable_sha256 or UNKNOWN,
        build=build or UNKNOWN,
        # NOT the vehicle's configuration: only the parameters this run explicitly set and read back.
        overrides_readback_sha256=UNKNOWN if readback is None else digest(readback),
        overrides_readback_complete=False,
        overrides_readback_scope="parameters explicitly set by this run; the rest of the vehicle is unrecorded",
        realized_events_ms={k: _ms(v) for k, v in sorted((realized_events or {}).items())} or UNKNOWN,
        raw_artifacts=raw_artifacts or UNKNOWN)
    if parameter_snapshots:
        body['parameter_snapshots'] = parameter_snapshots
        body['overrides_readback_scope'] = 'parameters explicitly set by this run; full table reads are in parameter_snapshots'
    return dict(body, execution_id=digest(body))


def analysis(execution_id: str, *, inputs: dict, protocol_version: str, verdict_config: dict) -> dict:
    """How those bytes were read. Re-analysis changes this and nothing else."""
    body = dict(schema=ANALYSIS_SCHEMA, execution_id=execution_id,
                normaliser_revision=NORMALISER_REVISION, inputs=dict(sorted(inputs.items())),
                protocol_version=protocol_version, verdict_config=dict(sorted(verdict_config.items())))
    return dict(body, analysis_id=digest(body))


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
