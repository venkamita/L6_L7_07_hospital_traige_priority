"""
Branch Coverage Test File
Target: hospital_triage_priority.py
Goal: Achieve >= 90% BRANCH coverage

Each test comment documents WHICH branch is being exercised.

Author: Student
"""

import pytest
from hospital_triage_priority import process_triage_wards, monitor_oxygen_manifolds


# ===========================================================================
# process_triage_wards  — branch coverage
# ===========================================================================
#
# Branch map (condition → T/F branches):
#   B1 : not isinstance(wards, list)   → T → raise
#   B2 : default_acuity_score < 0      → T → raise   (else falls through)
#   B3 : ward.get("is_accepting")      → F → continue,  T → process ward
#   B4 : spo2 <= 0 or heart_rate <= 0  → T → flag+continue, F → proceed
#   B5 : is_unconscious                → T → unconscious block, F → elif
#   B6 : ward_tier == "outpatient"     → T → reset+break, F → add 100
#   B7 : spo2 < 90 or heart_rate > 120 → T → add 60, F → default acuity
#   B8 : ward.get("icu_standby")       → T → +25, F → skip
#   B9 : flagged_entries > 4           → T → WARD_ALERT
#   B10: total_acuity == 0             → T → NO_URGENT_CASES, F → TRIAGE_STABLE
# ===========================================================================


# --- B1 T: wards is not a list -------------------------------------------------
def test_b1_wards_not_list_raises():
    """B1=True: isinstance check fails → ValueError"""
    with pytest.raises(ValueError):
        process_triage_wards({"a": 1}, 10)


# --- B1 F, B2 T: list but negative score ---------------------------------------
def test_b2_negative_score_raises():
    """B1=False, B2=True: negative acuity score → ValueError"""
    with pytest.raises(ValueError):
        process_triage_wards([], -5)


# --- B1 F, B2 F, B3 F: ward not accepting → skipped ---------------------------
def test_b3_ward_not_accepting_skipped():
    """B3=False: ward is_accepting=False → continue (ward is ignored)"""
    wards = [
        {
            "is_accepting": False,
            "tier": "general",
            "icu_standby": True,    # standby bonus NOT added since ward skipped
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


# --- B3 T: ward IS accepting ---------------------------------------------------
def test_b3_ward_accepting_processed():
    """B3=True: ward is processed"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


# --- B4 T: spo2 <= 0 -----------------------------------------------------------
def test_b4_spo2_zero_flagged():
    """B4=True (spo2=0): patient flagged and skipped"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 0, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


# --- B4 T: heart_rate <= 0 -----------------------------------------------------
def test_b4_heart_rate_zero_flagged():
    """B4=True (hr=0): patient flagged and skipped"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": -1, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


# --- B4 F: valid vitals --------------------------------------------------------
def test_b4_valid_vitals_processed():
    """B4=False: valid vitals → patient is scored"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 20)
    assert result["acuity_score"] == 20


# --- B5 T + B6 T: unconscious in outpatient → reset & break --------------------
def test_b5_b6_unconscious_in_outpatient_resets():
    """B5=True, B6=True: outpatient unconscious resets acuity to 0 and breaks"""
    wards = [
        {
            "is_accepting": True,
            "tier": "outpatient",
            "icu_standby": False,
            "patients": [
                {"spo2": 98, "hr": 72, "unconscious": False},  # adds 10
                {"spo2": 98, "hr": 72, "unconscious": True},   # resets → 0, break
                {"spo2": 98, "hr": 72, "unconscious": False},  # never reached
            ],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


# --- B5 T + B6 F: unconscious in non-outpatient → add 100 ---------------------
def test_b5_b6_unconscious_in_general_adds_100():
    """B5=True, B6=False: non-outpatient unconscious adds 100"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": True}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 100


# --- B5 F, B7 T: conscious, low spo2 ------------------------------------------
def test_b7_low_spo2_adds_60():
    """B5=False, B7=True (spo2<90): +60 points"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 89, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


# --- B5 F, B7 T: conscious, high heart rate ------------------------------------
def test_b7_high_hr_adds_60():
    """B5=False, B7=True (hr>120): +60 points"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 121, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


# --- B5 F, B7 F: normal patient → default acuity ------------------------------
def test_b7_normal_patient_default_acuity():
    """B5=False, B7=False: stable patient → default_acuity_score added"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 90, "hr": 120, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 30)
    assert result["acuity_score"] == 30


# --- B8 T: icu_standby adds 25 -------------------------------------------------
def test_b8_icu_standby_true():
    """B8=True: icu_standby adds 25 to acuity"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": True,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 35  # 10 + 25


# --- B8 F: icu_standby false ---------------------------------------------------
def test_b8_icu_standby_false():
    """B8=False: no bonus"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


# --- B9 T: > 4 flagged entries → WARD_ALERT ------------------------------------
def test_b9_ward_alert_more_than_4_flagged():
    """B9=True: more than 4 flagged patients → WARD_ALERT"""
    bad_patients = [{"spo2": 0, "hr": 0, "unconscious": False}] * 5
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": bad_patients,
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"


# --- B9 F, B10 T: exactly 0 acuity → NO_URGENT_CASES --------------------------
def test_b10_no_urgent_cases():
    """B9=False, B10=True: total_acuity==0 → NO_URGENT_CASES"""
    result = process_triage_wards([], 10)
    assert result["status"] == "NO_URGENT_CASES"
    assert result["acuity_score"] == 0


# --- B9 F, B10 F: positive acuity → TRIAGE_STABLE -----------------------------
def test_b10_triage_stable():
    """B9=False, B10=False: acuity>0 → TRIAGE_STABLE"""
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "TRIAGE_STABLE"


# --- B4 T + B9 T: exactly 5 flagged entries (boundary check) ------------------
def test_exactly_5_flagged_is_alert():
    """Exactly 5 flagged entries: flagged_entries > 4 is True → WARD_ALERT"""
    bad_patients = [{"spo2": 0, "hr": 0, "unconscious": False}] * 5
    wards = [{"is_accepting": True, "tier": "general", "icu_standby": False, "patients": bad_patients}]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"


# --- Exactly 4 flagged entries (just below alert threshold) --------------------
def test_exactly_4_flagged_not_alert():
    """4 flagged entries: flagged_entries > 4 is False → not WARD_ALERT"""
    bad_patients = [{"spo2": 0, "hr": 0, "unconscious": False}] * 4
    good_patient = {"spo2": 98, "hr": 72, "unconscious": False}
    wards = [{"is_accepting": True, "tier": "general", "icu_standby": False,
              "patients": bad_patients + [good_patient]}]
    result = process_triage_wards(wards, 10)
    assert result["status"] != "WARD_ALERT"


# ===========================================================================
# monitor_oxygen_manifolds — branch coverage
# ===========================================================================
#
# Branch map:
#   MB1: not sensor_streams          → T → NO_DATA,  F → iterate
#   MB2: pressure_bar < 4.0          → T → increment streak, F → reset streak
#   MB3: drop_streak >= 2            → T → PRESSURE_FAILURE, F → continue
#   (implicit) fall-through          → PRESSURE_NORMAL
# ===========================================================================


# --- MB1 T: empty list ---------------------------------------------------------
def test_mb1_empty_returns_no_data():
    """MB1=True: empty sensor_streams → NO_DATA"""
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


# --- MB1 T: None ---------------------------------------------------------------
def test_mb1_none_returns_no_data():
    """MB1=True: None sensor_streams → NO_DATA"""
    assert monitor_oxygen_manifolds(None) == "NO_DATA"


# --- MB1 F, MB2 F: all pressures >= 4.0 → normal ------------------------------
def test_mb2_all_high_pressure_normal():
    """MB1=False, MB2=False for all readings → PRESSURE_NORMAL"""
    assert monitor_oxygen_manifolds([[4.0, 5.0, 6.0]]) == "PRESSURE_NORMAL"


# --- MB2 T, MB3 F: single drop resets, no failure -----------------------------
def test_mb2_mb3_single_drop_no_failure():
    """MB2=True once, MB3=False (streak=1 < 2): then pressure recovers"""
    assert monitor_oxygen_manifolds([[5.0, 3.0, 5.0]]) == "PRESSURE_NORMAL"


# --- MB2 T, MB3 T: two consecutive drops → PRESSURE_FAILURE -------------------
def test_mb2_mb3_two_consecutive_drops_failure():
    """MB2=True twice, MB3=True (streak>=2) → PRESSURE_FAILURE"""
    assert monitor_oxygen_manifolds([[5.0, 3.0, 3.0]]) == "PRESSURE_FAILURE"


# --- Multiple manifolds: failure in second manifold ----------------------------
def test_multiple_manifolds_failure_in_second():
    """First manifold OK, second triggers PRESSURE_FAILURE"""
    streams = [
        [5.0, 6.0, 4.5],       # all OK
        [5.0, 3.5, 3.5, 5.0],  # consecutive drops → failure
    ]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_FAILURE"


# --- Multiple manifolds: all fine → PRESSURE_NORMAL ---------------------------
def test_multiple_manifolds_all_normal():
    """Multiple manifolds, none trigger failure → PRESSURE_NORMAL"""
    streams = [
        [5.0, 6.0],
        [4.1, 5.0],
        [6.0, 3.0, 5.0],  # single drop then recovery
    ]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_NORMAL"


# --- Boundary: pressure exactly 4.0 is NOT < 4.0 ------------------------------
def test_boundary_pressure_at_4_not_failing():
    """4.0 is not < 4.0, so no drop streak incremented → PRESSURE_NORMAL"""
    assert monitor_oxygen_manifolds([[4.0, 4.0, 4.0]]) == "PRESSURE_NORMAL"


# --- Boundary: pressure just below 4.0 is < 4.0 → streak increments -----------
def test_boundary_just_below_4_increments():
    """3.99 < 4.0, two consecutive 3.99 → PRESSURE_FAILURE"""
    assert monitor_oxygen_manifolds([[3.99, 3.99]]) == "PRESSURE_FAILURE"


# --- Empty inner manifold: no readings → fall-through to PRESSURE_NORMAL -------
def test_empty_inner_manifold_normal():
    """Outer list has one manifold, but that manifold is empty → PRESSURE_NORMAL"""
    assert monitor_oxygen_manifolds([[]]) == "PRESSURE_NORMAL"
