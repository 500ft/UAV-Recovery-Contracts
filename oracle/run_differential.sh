#!/usr/bin/env bash
# Layer A against layer B: drive PX4's REAL Failsafe class and the Python model with the same sequences.
#
#   oracle/run_differential.sh <px4 checkout> <output dir>
#
# The adapter is TEST code added to the pinned tree, not a firmware change, but it does change the tree, so the
# patch and the resulting binary get their own recorded identity, distinct from the upstream test binary.
set -euo pipefail
PX4="${1:?usage: run_differential.sh <px4 checkout> <output dir>}"
OUT="${2:?usage: run_differential.sh <px4 checkout> <output dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
EXPECTED_COMMIT="d6f12ad1c4f70ad3230afd7d86e971421e02fef4"
mkdir -p "$OUT/oracle" "$OUT/model"
fail() { echo "DIFFERENTIAL BLOCKED: $*" >&2; echo "$*" > "$OUT/blocked.txt"; exit 1; }

[ "$(git -C "$PX4" rev-parse HEAD)" = "$EXPECTED_COMMIT" ] || fail "checkout is not the pinned commit"
DIR="$PX4/src/modules/commander/failsafe"
grep -q "differential_delay_test" "$DIR/CMakeLists.txt" && fail "the tree is already patched"

# 1. Patch: the adapter, and one registration line copied from the pattern PX4 uses for its own test.
cp "$HERE/differential/differential_delay_test.cpp" "$DIR/differential_delay_test.cpp"
printf '\npx4_add_functional_gtest(SRC differential_delay_test.cpp\n\tLINKLIBS failsafe mode_util\n)\n' >> "$DIR/CMakeLists.txt"
git -C "$PX4" diff > "$OUT/instrumentation.patch" || true
git -C "$PX4" status --short >> "$OUT/instrumentation.patch"
sha256sum "$HERE/differential/differential_delay_test.cpp" > "$OUT/adapter.sha256"

# 2. Build. A build failure is an ENVIRONMENT result and says nothing about PX4 behaviour.
if ! make -C "$PX4" tests TESTFILTER=differential_delay > "$OUT/build.log" 2>&1; then
  tail -60 "$OUT/build.log" > "$OUT/build_tail.log"
  fail "build failed; see build.log. Environment result, not a PX4 result."
fi
BIN=$(find "$PX4/build/px4_sitl_test" -type f -name "functional-differential_delay_test" -perm -u+x | head -1)
[ -n "$BIN" ] || fail "built, but the adapter executable is missing"
{ echo "px4_commit=$EXPECTED_COMMIT"; echo "binary=$BIN"; echo "binary_sha256=$(sha256sum "$BIN" | cut -d' ' -f1)"
  echo "uname=$(uname -srm)"; echo "cxx=$(${CXX:-c++} --version | head -1)"; echo "recorded_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$OUT/environment.txt"

# 3. One PROCESS per sequence: PX4 warns repeated setup in one process may not clean up.
ran=0; failed=0
for seq in "$HERE"/differential/sequences/*.seq; do
  name=$(basename "$seq" .seq)
  if ORACLE_SEQUENCE="$seq" ORACLE_OUT="$OUT/oracle/$name.oracle.csv" "$BIN" > "$OUT/oracle/$name.gtest.log" 2>&1; then
    ran=$((ran + 1))
  else
    failed=$((failed + 1)); echo "adapter failed on $name" >> "$OUT/adapter_failures.txt"
  fi
  # a run that produced no rows did not run, whatever the exit code said
  [ -s "$OUT/oracle/$name.oracle.csv" ] && [ "$(wc -l < "$OUT/oracle/$name.oracle.csv")" -gt 1 ] \
    || echo "no rows for $name" >> "$OUT/adapter_failures.txt"
  python3 "$HERE/differential/driver.py" model "$seq" "$OUT/model/$name.model.csv"
done
# The report reads <dir>/<name>.model.csv and <name>.oracle.csv, so collect them side by side.
mkdir -p "$OUT/pairs"; cp "$OUT"/model/*.csv "$OUT"/oracle/*.csv "$OUT/pairs/" 2>/dev/null || true
python3 "$HERE/differential/driver.py" report "$OUT/pairs" > "$OUT/report.json"
echo "sequences_run=$ran failed=$failed" > "$OUT/result.txt"
[ ! -s "$OUT/adapter_failures.txt" ] || fail "the adapter failed on at least one sequence; see adapter_failures.txt"
echo "DIFFERENTIAL RAN: $ran sequences through the real class; see $OUT/report.json"
