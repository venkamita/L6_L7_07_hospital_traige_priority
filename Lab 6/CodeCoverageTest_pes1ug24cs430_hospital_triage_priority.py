"""
Code Coverage Test File
Target: hospital_triage_priority.py
Goal: Achieve >= 90% LINE (statement) coverage

Author: Student
"""

import pytest
from hospital_triage_priority import process_triage_wards, monitor_oxygen_manifolds


# ---------------------------------------------------------------------------
# process_triage_wards — line coverage tests
# ---------------------------------------------------------------------------

# 1. Invalid input: wards is not a list  →  line 2 (isinstance check), line 3
def test_invalid_wards_not_a_list():
    with pytest.raises(ValueError):
        process_triage_wards("not a list", 10)


# 2. Invalid input: negative default_acuity_score  →  line 2 (< 0 check), line 3
def test_invalid_negative_acuity_score():
    with pytest.raises(ValueError):
        process_triage_wards([], -1)


# 3. Ward not accepting  →  line 9-10 (continue branch)
def test_ward_not_accepting_is_skipped():
    wards = [
        {
            "is_accepting": False,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0
    assert result["status"] == "NO_URGENT_CASES"


# 4. Patient with spo2 <= 0  →  lines 20-22 (flagged + continue)
def test_patient_invalid_spo2_flagged():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 0, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    # flagged but acuity stays 0
    assert result["acuity_score"] == 0


# 5. Patient with heart_rate <= 0  →  lines 20-22
def test_patient_invalid_heart_rate_flagged():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 0, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


# 6. Unconscious patient in NON-outpatient ward  →  lines 24-25, 29
def test_unconscious_patient_non_outpatient():
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
    assert result["status"] == "TRIAGE_STABLE"


# 7. Unconscious patient in OUTPATIENT ward  →  lines 24-28 (reset + break)
def test_unconscious_patient_outpatient_resets():
    wards = [
        {
            "is_accepting": True,
            "tier": "outpatient",
            "icu_standby": False,
            "patients": [
                {"spo2": 98, "hr": 72, "unconscious": False},   # contributes 10 first
                {"spo2": 98, "hr": 72, "unconscious": True},    # resets to 0 and breaks
            ],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


# 8. Low spo2 (< 90) → line 30-31 (+60)
def test_low_spo2_adds_60():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 85, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


# 9. High heart_rate (> 120) → line 30-31 (+60)
def test_high_heart_rate_adds_60():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 130, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


# 10. Normal patient → line 32-33 (default acuity)
def test_normal_patient_uses_default_acuity():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 15)
    assert result["acuity_score"] == 15


# 11. ICU standby adds 25  →  line 35-36
def test_icu_standby_adds_25():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": True,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 35   # 10 + 25


# 12. More than 4 flagged entries → WARD_ALERT  →  line 38-39
def test_more_than_4_flagged_ward_alert():
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


# 13. Empty wards list → NO_URGENT_CASES  →  line 40-41
def test_empty_wards_no_urgent_cases():
    result = process_triage_wards([], 10)
    assert result["status"] == "NO_URGENT_CASES"
    assert result["acuity_score"] == 0


# 14. Standard stable result → TRIAGE_STABLE  →  line 42
def test_triage_stable_return():
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


# ---------------------------------------------------------------------------
# monitor_oxygen_manifolds — line coverage tests
# ---------------------------------------------------------------------------

# 15. Empty sensor_streams → NO_DATA  →  line 46-47
def test_empty_sensor_streams_no_data():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


# 16. None / falsy sensor_streams → NO_DATA
def test_none_sensor_streams_no_data():
    assert monitor_oxygen_manifolds(None) == "NO_DATA"


# 17. All pressures normal → PRESSURE_NORMAL  →  lines 49-57 (else branch + return)
def test_all_normal_pressure():
    sensor_streams = [[5.0, 6.0, 4.5]]
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_NORMAL"


# 18. Single drop but not consecutive → resets streak, PRESSURE_NORMAL  →  line 56-57
def test_single_drop_then_recovery():
    sensor_streams = [[3.0, 5.0, 3.0]]   # drops never consecutive
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_NORMAL"


# 19. Two consecutive drops → PRESSURE_FAILURE  →  lines 52-55
def test_consecutive_drops_pressure_failure():
    sensor_streams = [[5.0, 3.0, 2.0, 5.0]]
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_FAILURE"


# 20. Multiple manifolds, failure in second  →  verify early return
def test_pressure_failure_in_second_manifold():
    sensor_streams = [
        [5.0, 6.0],       # all good
        [3.5, 3.5, 5.0],  # consecutive drops in second manifold
    ]
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_FAILURE"


# 21. Drop streak exactly 2  →  boundary check for >= 2
def test_drop_streak_exactly_2():
    sensor_streams = [[4.0, 3.9, 3.9]]   # 4.0 is NOT < 4.0; 3.9, 3.9 are → streak=2
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_FAILURE"


# 22. Pressure exactly at boundary 4.0 (not failing)
def test_pressure_exactly_4_not_failing():
    sensor_streams = [[4.0, 4.0, 4.0]]
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_NORMAL"
