# Lab 7: Fuzz Testing with Hypothesis
# Name: Sharat Doddihal
# SRN : PES1UG24CS430

import pytest
from hypothesis import given, settings, strategies as st
from processor import parse_vitals_summary, compute_patient_bmi, assign_ward_bed


@settings(max_examples=500)
@given(st.text() | st.none())
def test_parse_vitals_summary_no_crash(s):
    try:
        result = parse_vitals_summary(s)
    except Exception as e:
        pytest.fail(f"parse_vitals_summary crashed on {s!r}: {type(e).__name__}: {e}")
    assert isinstance(result, str)


@settings(max_examples=500)
@given(st.text() | st.none())
def test_compute_patient_bmi_safe(s):
    try:
        result = compute_patient_bmi(s)
    except Exception as e:
        pytest.fail(f"compute_patient_bmi crashed on {s!r}: {type(e).__name__}: {e}")
    assert result is None or isinstance(result, float)


@settings(max_examples=500)
@given(st.text() | st.none())
def test_assign_ward_bed_safe(s):
    try:
        result = assign_ward_bed(s)
    except Exception as e:
        pytest.fail(f"assign_ward_bed crashed on {s!r}: {type(e).__name__}: {e}")
    assert isinstance(result, str)
