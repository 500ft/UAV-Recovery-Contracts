/****************************************************************************
 * Differential adapter: drive the REAL PX4 `Failsafe` class from a plain-text sequence file and write what it
 * selects after every update. NOT a reimplementation of the selector: it constructs the class PX4 ships, sets
 * parameters through PX4's own parameter store, and calls update() exactly as commander does.
 *
 * It is a gtest so it links with the same libraries as PX4's own failsafe_test, and it SKIPS when the two
 * environment variables are absent so that `make tests` is unaffected by its presence.
 *
 *   ORACLE_SEQUENCE  path of the sequence file
 *   ORACLE_OUT       path of the CSV to write
 *
 * Sequence grammar, one command per line, '#' starts a comment:
 *   param NAME VALUE     set a parameter BEFORE the class is constructed (int or float, by PX4's own type)
 *   armed 0|1
 *   mode  POSCTL|ALTCTL|AUTO_LOITER|OFFBOARD
 *   flag  NAME 0|1       one of the failsafe_flags fields listed in set_flag()
 *   run   SECONDS DT_MS  advance in DT_MS updates, writing one CSV row per update
 *
 * Commands take effect at the NEXT update, which is how flags reach the framework in a real vehicle.
 * Initial armed directives set the construction state. The first other non-param command constructs the class
 * and gives it one initial update at t = 5 s with
 * no flags, exactly as PX4's own test does, so _last_update is seeded the same way.
 ****************************************************************************/

#include <gtest/gtest.h>

#include "framework.h"
#include "failsafe.h"
#include <uORB/topics/vehicle_status.h>

#include <cmath>
#include <cstdlib>
#include <fstream>
#include <memory>
#include <sstream>
#include <string>

using namespace time_literals;

namespace
{

bool set_param(const std::string &name, double value)
{
	const param_t handle = param_find(name.c_str());

	if (handle == PARAM_INVALID) {
		return false;
	}

	if (param_type(handle) == PARAM_TYPE_INT32) {
		int32_t v = static_cast<int32_t>(std::lround(value));
		return param_set(handle, &v) == 0;
	}

	float v = static_cast<float>(value);
	return param_set(handle, &v) == 0;
}

bool set_flag(failsafe_flags_s &f, const std::string &name, bool v)
{
	if (name == "gcs_connection_lost") { f.gcs_connection_lost = v; }
	else if (name == "geofence_breached") { f.geofence_breached = v; }
	else if (name == "position_accuracy_low") { f.position_accuracy_low = v; }
	else if (name == "manual_control_signal_lost") { f.manual_control_signal_lost = v; }
	else { return false; }

	return true;
}

bool parse_mode(const std::string &name, uint8_t &mode)
{
	if (name == "POSCTL") { mode = vehicle_status_s::NAVIGATION_STATE_POSCTL; }
	else if (name == "ALTCTL") { mode = vehicle_status_s::NAVIGATION_STATE_ALTCTL; }
	else if (name == "AUTO_LOITER") { mode = vehicle_status_s::NAVIGATION_STATE_AUTO_LOITER; }
	else if (name == "OFFBOARD") { mode = vehicle_status_s::NAVIGATION_STATE_OFFBOARD; }
	else { return false; }

	return true;
}

} // namespace

TEST(DifferentialDelay, run_sequence)
{
	const char *seq_path = std::getenv("ORACLE_SEQUENCE");
	const char *out_path = std::getenv("ORACLE_OUT");

	if (seq_path == nullptr || out_path == nullptr) {
		GTEST_SKIP() << "ORACLE_SEQUENCE and ORACLE_OUT not set; this adapter only runs under the differential driver";
	}

	std::ifstream in(seq_path);
	ASSERT_TRUE(in.good()) << "cannot open " << seq_path;
	std::ofstream out(out_path);
	ASSERT_TRUE(out.good()) << "cannot write " << out_path;
	out << "t_us,action_code,action\n";

	param_control_autosave(false);

	std::unique_ptr<Failsafe> failsafe;
	failsafe_flags_s flags{};
	FailsafeBase::State state{};
	state.armed = true;
	state.user_intended_mode = vehicle_status_s::NAVIGATION_STATE_POSCTL;
	state.vehicle_type = vehicle_status_s::VEHICLE_TYPE_ROTARY_WING;
	hrt_abstime time = 5_s;

	auto emit = [&]() {
		const auto action = failsafe->selectedAction();
		out << time << ',' << static_cast<int>(action) << ',' << FailsafeBase::actionStr(action) << '\n';
	};

	auto ensure_constructed = [&]() {
		if (!failsafe) {
			failsafe = std::make_unique<Failsafe>(nullptr);
			failsafe->update(time, state, false, false, flags);
			emit();
		}
	};

	std::string line;
	int line_no = 0;

	while (std::getline(in, line)) {
		++line_no;
		const auto hash = line.find('#');

		if (hash != std::string::npos) { line.erase(hash); }

		std::istringstream ls(line);
		std::string cmd;

		if (!(ls >> cmd)) { continue; }

		if (cmd == "param") {
			std::string name; double value;
			ASSERT_TRUE(ls >> name >> value) << "line " << line_no;
			ASSERT_FALSE(failsafe) << "param after construction is not supported (line " << line_no << ")";
			ASSERT_TRUE(set_param(name, value)) << "unknown or unsettable parameter " << name;
			continue;
		}

		if (cmd == "armed" && !failsafe) {
			int v; ASSERT_TRUE(ls >> v); state.armed = v != 0;
			continue;
		}

		ensure_constructed();

		if (cmd == "armed") {
			int v; ASSERT_TRUE(ls >> v); state.armed = v != 0;

		} else if (cmd == "mode") {
			std::string m; ASSERT_TRUE(ls >> m);
			ASSERT_TRUE(parse_mode(m, state.user_intended_mode)) << "unknown mode " << m;

		} else if (cmd == "flag") {
			std::string n; int v; ASSERT_TRUE(ls >> n >> v);
			ASSERT_TRUE(set_flag(flags, n, v != 0)) << "unsupported flag " << n;

		} else if (cmd == "run") {
			double seconds; int dt_ms; ASSERT_TRUE(ls >> seconds >> dt_ms);
			ASSERT_GT(dt_ms, 0);
			const long steps = std::lround(seconds * 1000.0 / dt_ms);

			for (long i = 0; i < steps; ++i) {
				time += static_cast<hrt_abstime>(dt_ms) * 1000;
				failsafe->update(time, state, false, false, flags);
				emit();
			}

		} else {
			FAIL() << "unknown command '" << cmd << "' on line " << line_no;
		}
	}

	ASSERT_TRUE(static_cast<bool>(failsafe)) << "the sequence never constructed the class";
}
