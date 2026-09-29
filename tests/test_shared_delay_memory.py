"""The six hand-derived cases for the shared delay pot (owner review 2026-09-25, WP3).

Source: framework.cpp at the pinned commit d6f12ad.
  L50, L146   _current_start_delay is seeded from COM_FAIL_ACT_T
  L121-141    updateStartDelay: drains by dt while a delayed action is pending, refills by dt/4 when none is,
              capped at COM_FAIL_ACT_T
  L351-356    a new delayable action with no delay running fills _current_delay from _current_start_delay
  L149-157    updateDelay decrements _current_delay
  L653-668    clearDelayIfNeeded zeroes _current_delay when already past Hold, Hold cannot run, or takeover

These are hand-worked expectations, and this file is a TRANSCRIPTION self-check. It does not establish that the
model matches the pinned C++ class: that needs the native oracle running the same sequences. The three
acceptance levels stay separate, and only the first is reached here.
"""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.px4_failsafe import DEFAULTS, Selector  # noqa: E402

RTL_5S = dict(DEFAULTS, NAV_DLL_ACT=2, COM_FAIL_ACT_T=5.0)


STEP = 0.1          # the action changes on the update AFTER the counter reaches zero, so expect one step late


def advance(sel, seconds, step=STEP, **kw):
    """Run the selector forward, returning the first second at which it left Hold, or None."""
    left_hold_at = None
    t = 0.0
    for _ in range(int(round(seconds / step))):
        action = sel.step(step, **kw)
        t = round(t + step, 3)
        if left_hold_at is None and action not in ("Hold", "None", "Warn"):
            left_hold_at = t
    return left_hold_at


class SharedDelayMemoryTests(unittest.TestCase):

    def test_1_a_disabled_action_stays_disabled(self):
        sel = Selector(dict(DEFAULTS, NAV_DLL_ACT=0))          # 0 = no action configured
        sel.raise_hazard("datalink_loss")
        self.assertEqual(sel.step(0.0), "None")
        self.assertEqual(advance(sel, 30.0), None)

    def test_2_an_enabled_delayed_response_waits_its_delay(self):
        sel = Selector(dict(RTL_5S))
        sel.raise_hazard("datalink_loss")
        self.assertEqual(sel.step(0.0), "Hold", "the delay is served in Hold first")
        self.assertAlmostEqual(advance(sel, 20.0), 5.0, delta=STEP + 1e-6)

    def test_3_zero_delay_removes_the_waiting_behaviour(self):
        sel = Selector(dict(RTL_5S, COM_FAIL_ACT_T=0.0))
        sel.raise_hazard("datalink_loss")
        self.assertEqual(sel.step(0.0), "RTL", "no Hold when the configured delay is off")

    def test_4_a_re_raise_after_a_short_gap_gets_a_shorter_delay(self):
        """The pot drained during the first episode and only refills at a quarter of real time."""
        sel = Selector(dict(RTL_5S))
        sel.raise_hazard("datalink_loss")
        sel.step(0.0)
        advance(sel, 3.0)                                       # burn 3 s of the 5 s pot in Hold
        drained = sel.start_delay_s
        self.assertLess(drained, 5.0)
        sel.clear_hazard("datalink_loss", mode_changed_or_disarmed=True)
        advance(sel, 2.0)                                       # quiet: refills 2.0 / 4 = 0.5 s
        self.assertAlmostEqual(sel.start_delay_s, drained + 0.5, places=3)
        sel.raise_hazard("datalink_loss")
        sel.step(0.0)                                           # the registering update seeds the delay
        self.assertLess(sel.delay_left_s, 5.0, "the second episode does NOT get a fresh full delay")
        self.assertAlmostEqual(sel.delay_left_s, sel.start_delay_s, places=6)

    def test_5_a_long_quiet_gap_restores_the_pot_but_never_past_the_cap(self):
        sel = Selector(dict(RTL_5S))
        sel.raise_hazard("datalink_loss")
        advance(sel, 5.0)
        sel.clear_hazard("datalink_loss", mode_changed_or_disarmed=True)
        sel.delay_left_s, sel.delayed, sel.selected = 0.0, "None", "None"
        advance(sel, 120.0)                                     # far longer than 4 x 5 s
        self.assertAlmostEqual(sel.start_delay_s, 5.0, places=3, msg="refill is capped at COM_FAIL_ACT_T")

    def test_6_a_second_eligible_action_during_a_running_delay_shares_the_state(self):
        """The delay is one counter, not one per hazard. The second hazard does not restart it."""
        sel = Selector(dict(RTL_5S, GF_ACTION=3))
        sel.raise_hazard("datalink_loss")
        advance(sel, 2.0)
        remaining = sel.delay_left_s
        sel.raise_hazard("geofence_breach")
        self.assertAlmostEqual(sel.delay_left_s, remaining, places=6,
                               msg="a second hazard must not refill the single shared delay")
        self.assertAlmostEqual(advance(sel, 20.0), remaining, delta=STEP + 1e-6)

    def test_the_recharge_rate_is_a_quarter_of_real_time(self):
        sel = Selector(dict(RTL_5S))
        sel.start_delay_s = 0.0
        advance(sel, 4.0)
        self.assertAlmostEqual(sel.start_delay_s, 1.0, places=2)

    def test_the_worked_example_is_exact_at_every_step_size(self):
        """burn 3 s of a 5 s pot, stay quiet 2 s: (5 - 3) + 2/4 = 2.5 s, independent of the update period.

        An earlier version of this test asserted convergence and documented that the model 'lands one update
        late', claiming the real framework did too. The differential against PX4's real Failsafe class showed
        that was a defect in the model's update order, not a property of PX4, and it is retracted.
        """
        for step in (0.1, 0.01, 0.001):
            sel = Selector(dict(RTL_5S))
            sel.raise_hazard("datalink_loss"); sel.step(0.0)
            advance(sel, 3.0, step=step)
            sel.clear_hazard("datalink_loss", mode_changed_or_disarmed=True)
            advance(sel, 2.0, step=step)
            sel.raise_hazard("datalink_loss"); sel.step(0.0)
            self.assertAlmostEqual(sel.delay_left_s, 2.5, places=6, msg=f"dt={step}")

    def test_a_full_reset_needs_four_times_the_drained_quiet_time(self):
        sel = Selector(dict(RTL_5S))
        sel.raise_hazard("datalink_loss")
        advance(sel, 3.0)                                       # drain 3 s
        sel.clear_hazard("datalink_loss", mode_changed_or_disarmed=True)
        sel.delay_left_s, sel.delayed, sel.selected = 0.0, "None", "None"
        advance(sel, 11.0)
        self.assertLess(sel.start_delay_s, 5.0, "11 s of quiet is not yet 4 x 3 s")
        advance(sel, 2.0)
        self.assertAlmostEqual(sel.start_delay_s, 5.0, places=3)

    def test_this_file_is_a_transcription_check_not_a_differential_result(self):
        """Guard against the docstring drifting into a claim the fixtures do not support."""
        self.assertIn("does not establish that the model matches the pinned C++", __doc__.replace("\n", " "))


if __name__ == "__main__":
    unittest.main()
