import math


def _parse_number(text):
    """Convert text to a finite float, or return None if that isn't possible."""
    try:
        value = float(text.strip())
    except (ValueError, AttributeError):
        return None
    if not math.isfinite(value):
        return None
    return value


def parse_vitals_summary(vitals_csv):
    if not isinstance(vitals_csv, str):
        return "Invalid input: vitals must be a string"
    parts = vitals_csv.split(',')
    if len(parts) != 3:
        return "Invalid input: expected HR,SpO2,Temp"
    hr, spo2, temp = (_parse_number(p) for p in parts)
    if hr is None or spo2 is None or temp is None:
        return "Invalid input: vitals must be numbers"
    critical = hr > 120 or spo2 < 90 or temp > 39.0
    return f"Vitals: HR={hr}, SpO2={spo2}% - {'CRITICAL' if critical else 'STABLE'}"


def compute_patient_bmi(bmi_string):
    if not isinstance(bmi_string, str):
        return None
    parts = bmi_string.split('/')
    if len(parts) != 2:
        return None
    weight = _parse_number(parts[0])
    height = _parse_number(parts[1])
    if weight is None or height is None or weight <= 0 or height <= 0:
        return None
    try:
        bmi = weight / (height ** 2)
    except (OverflowError, ZeroDivisionError):
        return None
    if not math.isfinite(bmi):
        return None
    return round(bmi, 2)


def assign_ward_bed(allocation_code):
    if not isinstance(allocation_code, str):
        return "Invalid input: allocation code must be a string"
    parts = allocation_code.strip().split('-')
    if len(parts) != 2:
        return "Invalid input: expected WARD-BED (e.g. ICU-05)"
    ward, bed_str = parts
    ward_names = {
        "ER": "Emergency Room",
        "ICU": "Intensive Care Unit",
        "GEN": "General Ward",
        "PED": "Pediatrics"
    }
    ward_name = ward_names.get(ward.strip().upper())
    if ward_name is None:
        return f"Invalid input: unknown ward {ward!r}"
    bed_str = bed_str.strip()
    if not (bed_str.isascii() and bed_str.isdigit()):
        return "Invalid input: bed number must be digits"
    bed_num = int(bed_str)
    if bed_num <= 0:
        return "Invalid input: bed number must be positive"
    return f"{ward_name} Bed #{bed_num}"


def main():
    print("==== Running parse_vitals_summary ====")
    v_input = input("Enter vitals (HR,SpO2,Temp): ")
    print("Summary:", parse_vitals_summary(v_input))

    print("\n==== Running compute_patient_bmi ====")
    b_input = input("Enter weight/height (e.g. 70/1.75): ")
    bmi = compute_patient_bmi(b_input)
    print("BMI:", bmi if bmi is not None else "Invalid input: expected weight/height")

    print("\n==== Running assign_ward_bed ====")
    w_input = input("Enter allocation (e.g. ICU-05): ")
    print("Assignment:", assign_ward_bed(w_input))


if __name__ == "__main__":
    main()
