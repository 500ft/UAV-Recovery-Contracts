"""Executable model of the PX4 v1.17.0 failsafe framework — the discrete part of Study A.

Every table and rule here is transcribed from the pinned source [B1] (commit d6f12ad1c4f70ad3230afd7d86e971421e02fef4,
src/modules/commander/failsafe/{framework.h,framework.cpp,failsafe.h,failsafe.cpp}); line numbers are given per rule so a
reviewer can diff the model against the code. Continuous inputs (battery warning level, position validity, geofence
breach) enter as boolean/enum flags: this model decides *which action* the framework selects and *when*, not the physics.

No dependency beyond the standard library. `python model/px4_failsafe.py` runs the self-check.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# framework.h L52-70: "Actions further down take precedence"
ACTIONS = ("None", "Warn", "FallbackPosCtrl", "FallbackAltCtrl", "FallbackStab", "Hold", "RTL", "Land", "Descend", "Disarm", "Terminate")
PRECEDENCE = {a: i for i, a in enumerate(ACTIONS)}

# failsafe.cpp L43-84 (NAV_DLL_ACT and NAV_RCL_ACT share fromNavDllOrRclActParam); failsafe.h L113-120
LINK_LOSS_ACTION = {0: "None", 1: "Hold", 2: "RTL", 3: "Land", 5: "Terminate", 6: "Disarm"}
# failsafe.cpp L86-127; failsafe.h L104-111
GF_ACTION = {0: "None", 1: "Warn", 2: "Hold", 3: "RTL", 4: "Terminate", 5: "Land"}
# failsafe.cpp L280-327; failsafe.h L78-87 (COM_OBL_RC_ACT)
OFFBOARD_LOSS_ACTION = {0: "FallbackPosCtrl", 1: "FallbackAltCtrl", 2: "FallbackStab", 3: "RTL", 4: "Land", 5: "Hold", 6: "Terminate", 7: "Disarm"}
# failsafe.cpp L372-413; failsafe.h L151-158 (COM_POS_LOW_ACT)
POS_LOW_ACTION = {0: "None", 1: "Warn", 2: "Hold", 3: "RTL", 4: "Terminate", 5: "Land"}
# failsafe.cpp L190-249 (COM_LOW_BAT_ACT by warning level); failsafe.h L70-76
def battery_action(com_low_bat_act: int, warning: str) -> str:
    if warning == "low":
        return "Warn"
    if warning == "critical":
        return {0: "Warn", 1: "RTL", 2: "Land", 3: "RTL"}[com_low_bat_act]
    if warning == "emergency":
        return {0: "Warn", 1: "RTL", 2: "Land", 3: "Land"}[com_low_bat_act]
    return "None"

# framework.cpp L490-493: actions that can be delayed behind Hold
def can_be_delayed(action: str) -> bool:
    return action not in ("None", "Disarm", "Terminate", "Hold")

# failsafe.cpp L562, L542-544: geofence / wind / flight-time cannot be deferred (irrelevant to delay); the delay applies when
# COM_FAIL_ACT_T > 0.1 s and takeover is Auto (framework.cpp L351-362). Geofence Hold and PosLow use AlwaysModeSwitchOnly.

HAZARD_PARAM = {  # hazard class -> (parameter, map)
    "datalink_loss": ("NAV_DLL_ACT", LINK_LOSS_ACTION),
    "rc_loss": ("NAV_RCL_ACT", LINK_LOSS_ACTION),
    "geofence_breach": ("GF_ACTION", GF_ACTION),
    "offboard_loss": ("COM_OBL_RC_ACT", OFFBOARD_LOSS_ACTION),
    "position_low": ("COM_POS_LOW_ACT", POS_LOW_ACTION),
}


def configured_action(hazard: str, params: dict, battery_warning: str = "critical") -> str:
    """Action the framework will register for `hazard` under `params` (failsafe.cpp checkStateAndMode)."""
    if hazard.startswith("battery"):
        return battery_action(int(params.get("COM_LOW_BAT_ACT", 0)), hazard.split("_", 1)[1] if "_" in hazard else battery_warning)
    p, table = HAZARD_PARAM[hazard]
    return table[int(params.get(p, DEFAULTS[p]))]


DEFAULTS = {"NAV_DLL_ACT": 0, "NAV_RCL_ACT": 2, "GF_ACTION": 2, "COM_OBL_RC_ACT": 0, "COM_POS_LOW_ACT": 3, "COM_LOW_BAT_ACT": 0,
            "COM_FAIL_ACT_T": 5.0, "COM_DL_LOSS_T": 10, "COM_RC_LOSS_T": 0.5, "COM_OF_LOSS_T": 1.0}  # [B10]


@dataclass
class Selector:
    """framework.cpp getSelectedAction (L438-645) restricted to: max over active actions, delayed Hold, terminate latch.
    User takeover and mode-requirement fallbacks are modelled as inputs (`takeover`, `mode_can_run`)."""
    params: dict
    active: dict = field(default_factory=dict)  # hazard -> action
    selected: str = "None"
    delayed: str = "None"
    terminated: bool = False
    # framework.h keeps both delay counters as hrt_abstime, an unsigned integer of MICROseconds. The model does
    # the same. Float seconds made the first RTL land at 5.0 or 5.1 s depending on accumulated rounding, which is
    # a property of the transcription and not of the framework.
    _delay_us: int = 0                     # _current_delay: what is left of the delay now running
    _start_delay_us: int | None = None     # _current_start_delay: the pot the NEXT delay is filled from
    _newly: list = field(default_factory=list)

    def __post_init__(self) -> None:
        # framework.cpp L50 and L146: both the constructor and updateParams seed the pot from COM_FAIL_ACT_T.
        if self._start_delay_us is None:
            self._start_delay_us = self._configured_us()

    def _configured_us(self) -> int:
        # framework.cpp L135: `_param_com_fail_act_t.get() * 1_s`, truncated to an unsigned integer
        return int(float(self.params.get("COM_FAIL_ACT_T", 5.0)) * 1_000_000)

    @property
    def delay_left_s(self) -> float:
        return self._delay_us / 1e6

    @delay_left_s.setter
    def delay_left_s(self, seconds: float) -> None:
        self._delay_us = int(round(seconds * 1e6))

    @property
    def start_delay_s(self) -> float:
        return self._start_delay_us / 1e6

    @start_delay_s.setter
    def start_delay_s(self, seconds: float) -> None:
        self._start_delay_us = int(round(seconds * 1e6))

    def _update_start_delay(self, dt_us: int, delay_active: bool) -> None:
        """framework.cpp updateStartDelay L121-141, in integer microseconds.

        The pot drains while a delayed action is pending and refills at a QUARTER of real time when none is.
        The source comment says why: "Ensure that even with a toggling state the delayed action is executed at
        some point. This is done by increasing the delay slower than reducing it." A hazard that clears and
        re-raises therefore does not get its full delay back. `dt / 4` is INTEGER division, as in the source.
        """
        if delay_active:
            self._start_delay_us = self._start_delay_us - dt_us if dt_us < self._start_delay_us else 0
        else:
            self._start_delay_us = min(self._configured_us(), self._start_delay_us + dt_us // 4)

    def raise_hazard(self, hazard: str, warning: str = "critical") -> None:
        act = configured_action(hazard, self.params, warning)
        if hazard not in self.active:
            self._newly.append((hazard, act))
        self.active[hazard] = act

    def clear_hazard(self, hazard: str, mode_changed_or_disarmed: bool = False) -> None:
        # ClearCondition: link-loss/geofence/offboard actions clear OnModeChangeOrDisarm (failsafe.cpp L54, L102, L108...), position-low clears WhenConditionClears (L388-404)
        if hazard == "position_low" or mode_changed_or_disarmed:
            self.active.pop(hazard, None)

    def step(self, dt_s: float, armed: bool = True, takeover: bool = False, hold_can_run: bool = True) -> str:
        """One FailsafeBase::update(), in the order framework.cpp performs it (L55-107):

            updateDelay -> checkStateAndMode (registration) -> clearDelayIfNeeded -> getSelectedAction
                        -> updateStartDelay, keyed on THIS update's delayed action

        The earlier model updated the pot from the PREVIOUS update's delayed status and seeded a new delay before
        the elapsed time was taken off it. The differential against the real class found the difference: it moved
        the second episode of a clear and re-raise by exactly one update period (evidence/task-differential-*).
        """
        dt_us = round(dt_s * 1_000_000)
        if self.terminated:  # framework.cpp L446-450: Terminate never clears
            self.selected = "Terminate"; return self.selected
        if not armed:
            self.selected = "None"; self._newly.clear(); return self.selected
        # updateDelay L149-157
        self._delay_us = self._delay_us - dt_us if dt_us < self._delay_us else 0
        # checkStateAndMode -> checkFailsafe L351-356: a new delayable action with no delay running fills
        # _current_delay from _current_start_delay, AFTER the elapsed time has been taken off
        for _hazard, act in self._newly:
            if self._configured_us() > 100_000 and act != "Warn" and self._delay_us == 0 and can_be_delayed(act):
                self._delay_us = self._start_delay_us
        self._newly.clear()
        # clearDelayIfNeeded L653-668: no Hold-first delay when already in a failsafe (selected > Hold),
        # when Hold cannot run, or when the user has taken over
        if PRECEDENCE[self.selected] > PRECEDENCE["Hold"] or not hold_can_run or takeover:
            self._delay_us = 0
        best = "None"
        for act in self.active.values():  # L462-481: worst (highest precedence) action wins
            if PRECEDENCE[act] > PRECEDENCE[best]:
                best = act
        self.delayed = "None"
        if self._delay_us > 0 and not takeover and can_be_delayed(best) and hold_can_run:  # L489-500
            self.delayed = best; best = "Hold"
        if takeover and best in ("Hold", "RTL", "Land", "Descend"):  # L502-535, actionAllowsUserTakeover L647-651
            best = "Warn"
        # updateStartDelay L89: uses the delayed action selected in THIS update
        self._update_start_delay(dt_us, self.delayed != "None")
        if best == "Terminate":
            self.terminated = True
        self.selected = best
        return best


def demo() -> None:
    """Self-check: the smallest assertions that fail if a table or rule is transcribed wrongly."""
    assert PRECEDENCE["Terminate"] > PRECEDENCE["Disarm"] > PRECEDENCE["Land"] > PRECEDENCE["RTL"] > PRECEDENCE["Hold"] > PRECEDENCE["Warn"]
    assert configured_action("datalink_loss", DEFAULTS) == "None"          # vendor default disables the datalink failsafe [B10]
    assert configured_action("rc_loss", DEFAULTS) == "RTL"
    assert configured_action("geofence_breach", DEFAULTS) == "Hold"
    assert configured_action("offboard_loss", DEFAULTS) == "FallbackPosCtrl"
    assert battery_action(3, "critical") == "RTL" and battery_action(3, "emergency") == "Land" and battery_action(0, "critical") == "Warn"
    s = Selector(dict(DEFAULTS, NAV_DLL_ACT=2))
    s.raise_hazard("datalink_loss"); assert s.step(0.0) == "Hold" and s.delayed == "RTL"     # Hold first for COM_FAIL_ACT_T [B2]
    assert s.step(4.9) == "Hold" and s.step(0.2) == "RTL"                                    # then the delayed action
    s.raise_hazard("geofence_breach"); assert s.step(0.1) == "RTL"                           # Hold (geofence) < RTL: RTL stays selected
    s2 = Selector(dict(DEFAULTS, NAV_DLL_ACT=2, GF_ACTION=5)); s2.raise_hazard("datalink_loss"); s2.step(0.0); s2.step(6.0); s2.raise_hazard("geofence_breach")  # register, THEN serve the delay
    assert s2.step(0.1) == "Land"                                                            # Land > RTL takes precedence
    s3 = Selector(dict(DEFAULTS, NAV_DLL_ACT=2, COM_FAIL_ACT_T=0.0)); s3.raise_hazard("datalink_loss"); assert s3.step(0.0) == "RTL"  # no delay when COM_FAIL_ACT_T <= 0.1
    s4 = Selector(dict(DEFAULTS, NAV_DLL_ACT=2)); s4.raise_hazard("datalink_loss"); assert s4.step(0.0, takeover=True) == "Warn"       # stick takeover interrupts
    s5 = Selector(dict(DEFAULTS, NAV_DLL_ACT=5)); s5.raise_hazard("datalink_loss"); s5.step(0.0); s5.clear_hazard("datalink_loss", True); assert s5.step(1.0) == "Terminate"  # latch
    print("px4_failsafe model self-check OK")


if __name__ == "__main__":
    demo()
