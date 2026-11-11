# L6_L7_07 — Hospital Triage Priority

Lab 7: Fuzz Testing with Hypothesis

**Name:** Sharat Doddihal  **SRN:** PES1UG24CS430

## About

Property-based fuzz tests (Hypothesis) for patient vitals summaries, BMI calculations and ward bed allocation codes. The tests exposed 9 crashes on malformed and `None` input in the starter `processor.py`; the fixed version validates its input and all tests pass.

## Files

| File | Description |
|------|-------------|
| `processor.py` | Fixed module under test (hardened against invalid input) |
| `test_processor.py` | Hypothesis fuzz tests for all three functions |
| `Lab7_FuzzTesting_pes1ug24cs430.pdf` | Lab report with the screenshots for Steps 2, 4, 5 and 6 |
| `screenshots/` | The individual screenshots used in the report |
| `fuzz_report_before_fix_pes1ug24cs430.txt` | Full pytest output against the buggy code (3 failed) |
| `fuzz_report_after_fix_pes1ug24cs430.txt` | Full pytest output against the fixed code (3 passed) |

## Running

```
pip install hypothesis pytest
python processor.py
python -m pytest test_processor.py
```
