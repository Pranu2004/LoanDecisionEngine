
import csv
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("data/anomalies")
MASTER_DIR = Path("data/master")


def load_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def validate():
    applications = load_csv(DATA_DIR / "loan_applications.csv")
    schedules = load_csv(DATA_DIR / "repayment_schedules.csv")
    events = load_csv(DATA_DIR / "event_history.csv")
    incomes = load_csv(DATA_DIR / "income_records.csv")
    products = load_csv(MASTER_DIR / "loan_products.csv")
    labels = load_csv(DATA_DIR / "ground_truth.csv")

    product_lookup = {p["product_id"]: p for p in products}
    app_lookup = {a["loan_id"]: a for a in applications}
    event_groups = defaultdict(list)
    income_groups = defaultdict(list)

    for event in events:
        event_groups[event["loan_id"]].append(event)

    for income in incomes:
        income_groups[income["applicant_id"]].append(income)

    def find_label(anomaly_type):
        matches = [r for r in labels if r["anomaly_type"] == anomaly_type]
        if len(matches) != 1:
            raise ValueError(
                f"Expected exactly one ground-truth label for "
                f"{anomaly_type}; found {len(matches)}"
            )
        return matches[0]

    results = {}

    # 1. Validate the labelled loan's term against its product.
    label = find_label("TERM_OUTSIDE_PRODUCT_RANGE")
    loan_id = label["target_id"]
    app = app_lookup.get(loan_id)
    detected = False

    if app and app["product_id"] in product_lookup:
        product = product_lookup[app["product_id"]]
        term = int(app["requested_term_months"])
        detected = (
            term < int(product["min_term_months"])
            or term > int(product["max_term_months"])
        )

    results["TERM_OUTSIDE_PRODUCT_RANGE"] = detected

    # 2. Validate the labelled schedule record's payment reconciliation.
    label = find_label("SCHEDULE_RECONCILIATION_MISMATCH")
    schedule_id = label["target_id"]
    schedule = next(
        (r for r in schedules if r["schedule_id"] == schedule_id), None
    )
    detected = False

    if schedule:
        components = (
            float(schedule["principal_component"])
            + float(schedule["interest_component"])
        )
        detected = abs(
            round(components, 2) - round(float(schedule["payment_amount"]), 2)
        ) > 0.01

    results["SCHEDULE_RECONCILIATION_MISMATCH"] = detected

    # 3. Check the labelled loan's event timestamps.
    label = find_label("DECISION_BEFORE_AFFORDABILITY_CHECK")
    loan_id = label["target_id"]
    loan_events = event_groups.get(loan_id, [])
    check_times = [
        e["event_timestamp"] for e in loan_events
        if e["event_type"] == "AFFORDABILITY_CHECK_COMPLETED"
    ]
    decision_times = [
        e["event_timestamp"] for e in loan_events
        if e["event_type"] == "DECISION_RECORDED"
    ]
    results["DECISION_BEFORE_AFFORDABILITY_CHECK"] = (
        bool(check_times and decision_times)
        and min(decision_times) < min(check_times)
    )

    # 4. Check income conflicts for the labelled applicant.
    label = find_label("CONFLICTING_INCOME_RECORDS")
    applicant_id = label["target_id"]
    applicant_incomes = income_groups.get(applicant_id, [])
    results["CONFLICTING_INCOME_RECORDS"] = (
        len(applicant_incomes) > 1
        and len({
            float(r["monthly_income"]) for r in applicant_incomes
        }) > 1
    )

    # 5. Check for duplicate disbursement events on the labelled loan.
    label = find_label("DUPLICATE_APPLICATION_DISBURSEMENT")
    loan_id = label["target_id"]
    loan_events = event_groups.get(loan_id, [])
    results["DUPLICATE_APPLICATION_DISBURSEMENT"] = (
        sum(e["event_type"] == "LOAN_DISBURSED" for e in loan_events) > 1
    )

    print("TARGETED ANOMALY VALIDATION RESULTS")
    print("-" * 45)

    all_passed = True

    for anomaly_type, detected in results.items():
        label = find_label(anomaly_type)
        labelled = label.get("injected", "").strip().lower() == "true"
        passed = detected and labelled
        all_passed = all_passed and passed

        print(
            f"{'PASS' if passed else 'FAIL'}: {anomaly_type} "
            f"(target_detected={detected}, injected={labelled})"
        )

    if not all_passed:
        raise SystemExit(
            "\nValidation failed. Check ground_truth.csv target IDs "
            "and the corresponding anomaly records."
        )

    print("\nAll five injected anomalies were verified against their targets.")


if __name__ == "__main__":
    validate()
