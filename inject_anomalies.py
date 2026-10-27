
import csv
import json
from pathlib import Path

TRANSACTION_DIR = Path("data") / "transactions"
ANOMALY_DIR = Path("data") / "anomalies"
ANOMALY_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows to save: {path}")

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}: {len(rows)} rows")


def inject_anomalies():
    applications = load_csv(TRANSACTION_DIR / "loan_applications.csv")
    schedules = load_csv(TRANSACTION_DIR / "repayment_schedules.csv")
    events = load_csv(TRANSACTION_DIR / "event_history.csv")
    income_path = Path("data") / "master" / "income_records.csv"
    incomes = load_csv(income_path)
    products = load_csv(Path("data") / "master" / "loan_products.csv")

    products_by_id = {p["product_id"]: p for p in products}
    app_by_loan = {a["loan_id"]: a for a in applications}
    app_ids = list(app_by_loan)

    if len(app_ids) < 5:
        raise ValueError("At least five applications are required.")

    # Separate copies: source files remain unchanged.
    anomaly_apps = [dict(row) for row in applications]
    anomaly_schedules = [dict(row) for row in schedules]
    anomaly_events = [dict(row) for row in events]
    anomaly_incomes = [dict(row) for row in incomes]

    labels = []

    # 1. Requested term outside the product's allowed range.
    app = anomaly_apps[0]
    product = products_by_id[app["product_id"]]
    app["requested_term_months"] = str(
        int(product["max_term_months"]) + 1
    )
    labels.append({
        "anomaly_id": "ANOM-001",
        "anomaly_type": "TERM_OUTSIDE_PRODUCT_RANGE",
        "target_file": "loan_applications.csv",
        "target_id": app["loan_id"],
        "injected": "true",
    })

    # 2. Change one schedule payment to create a reconciliation anomaly.
    if not anomaly_schedules:
        raise ValueError("No repayment schedule rows are available.")

    schedule = anomaly_schedules[0]
    schedule["payment_amount"] = str(
        round(float(schedule["payment_amount"]) + 100, 2)
    )
    labels.append({
        "anomaly_id": "ANOM-002",
        "anomaly_type": "SCHEDULE_RECONCILIATION_MISMATCH",
        "target_file": "repayment_schedules.csv",
        "target_id": schedule["schedule_id"],
        "injected": "true",
    })

    # 3. Move a decision event before the affordability-check event.
    loan_for_timeline = app_ids[2]
    loan_events = [
        e for e in anomaly_events if e["loan_id"] == loan_for_timeline
    ]
    check_event = next(
        (e for e in loan_events
         if e["event_type"] == "AFFORDABILITY_CHECK_COMPLETED"),
        None,
    )
    decision_event = next(
        (e for e in loan_events if e["event_type"] == "DECISION_RECORDED"),
        None,
    )

    if check_event and decision_event:
        decision_event["event_timestamp"] = (
            app_by_loan[loan_for_timeline]["application_date"]
            + "T09:01:00"
        )
        labels.append({
            "anomaly_id": "ANOM-003",
            "anomaly_type": "DECISION_BEFORE_AFFORDABILITY_CHECK",
            "target_file": "event_history.csv",
            "target_id": loan_for_timeline,
            "injected": "true",
        })

    # 4. Make two income records for one applicant conflict.
    income_groups = {}
    for row in anomaly_incomes:
        income_groups.setdefault(row["applicant_id"], []).append(row)

    conflicting = next(
        (rows for rows in income_groups.values() if len(rows) >= 2),
        None,
    )
    if conflicting:
        conflicting[1]["monthly_income"] = str(
            round(float(conflicting[0]["monthly_income"]) * 2 + 1, 2)
        )
        labels.append({
            "anomaly_id": "ANOM-004",
            "anomaly_type": "CONFLICTING_INCOME_RECORDS",
            "target_file": "income_records.csv",
            "target_id": conflicting[0]["applicant_id"],
            "injected": "true",
        })

    # 5. Add a second disbursement event for the same loan.
    loan_for_disbursement = app_ids[4]
    anomaly_events.append({
        "event_id": f"EVT-{loan_for_disbursement}-DUP-DISB",
        "loan_id": loan_for_disbursement,
        "event_type": "LOAN_DISBURSED",
        "event_timestamp": "2026-10-22T12:00:00",
        "event_status": "completed",
    })
    anomaly_events.append({
        "event_id": f"EVT-{loan_for_disbursement}-DUP-DISB-2",
        "loan_id": loan_for_disbursement,
        "event_type": "LOAN_DISBURSED",
        "event_timestamp": "2026-10-22T12:05:00",
        "event_status": "completed",
    })
    labels.append({
        "anomaly_id": "ANOM-005",
        "anomaly_type": "DUPLICATE_APPLICATION_DISBURSEMENT",
        "target_file": "event_history.csv",
        "target_id": loan_for_disbursement,
        "injected": "true",
    })

    save_csv(ANOMALY_DIR / "loan_applications.csv", anomaly_apps)
    save_csv(ANOMALY_DIR / "repayment_schedules.csv", anomaly_schedules)
    save_csv(ANOMALY_DIR / "event_history.csv", anomaly_events)
    save_csv(ANOMALY_DIR / "income_records.csv", anomaly_incomes)
    save_csv(ANOMALY_DIR / "ground_truth.csv", labels)

    manifest = {
        "source": "synthetic generated data",
        "anomaly_count": len(labels),
        "anomaly_types": [row["anomaly_type"] for row in labels],
        "note": "Original master and transaction files were not modified.",
    }
    with (ANOMALY_DIR / "manifest.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(manifest, file, indent=2)

    print(f"Injected {len(labels)} labelled anomalies.")
    print("Original files remain unchanged.")


if __name__ == "__main__":
    inject_anomalies()
