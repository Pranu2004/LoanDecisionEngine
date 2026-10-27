
import csv
from pathlib import Path

MASTER_DIR = Path("data") / "master"
TRANSACTION_DIR = Path("data") / "transactions"
TRANSACTION_DIR.mkdir(parents=True, exist_ok=True)


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


def generate_anomalies():
    applications = load_csv(TRANSACTION_DIR / "loan_applications.csv")
    schedules = load_csv(TRANSACTION_DIR / "repayment_schedules.csv")
    decisions = load_csv(TRANSACTION_DIR / "decisions.csv")

    # Only use approved loans with schedules for the first anomaly cases.
    approved_ids = {
        row["loan_id"]
        for row in decisions
        if row["decision_outcome"] == "approve"
    }
    scheduled_ids = {row["loan_id"] for row in schedules}
    eligible = [
        row for row in applications
        if row["loan_id"] in approved_ids
        and row["loan_id"] in scheduled_ids
    ]

    if len(eligible) < 5:
        raise ValueError(
            "Need at least 5 approved applications with schedules "
            "to create these anomaly examples."
        )

    # Pick distinct applications for distinct anomaly types.
    selected = eligible[:5]
    ground_truth = []

    anomaly_definitions = [
        (
            "TERM_OUTSIDE_PRODUCT_RANGE",
            "loan_applications.csv",
            selected[0]["loan_id"],
            "Requested term is outside the selected product's allowed range.",
        ),
        (
            "SCHEDULE_RECONCILIATION_MISMATCH",
            "repayment_schedules.csv",
            selected[1]["loan_id"],
            "Repayment schedule totals do not reconcile with the expected amount.",
        ),
        (
            "DECISION_BEFORE_AFFORDABILITY_CHECK",
            "event_history.csv",
            selected[2]["loan_id"],
            "Decision event occurs before the affordability check event.",
        ),
        (
            "CONFLICTING_INCOME_RECORDS",
            "income_records.csv",
            selected[3]["applicant_id"],
            "Income records for the same applicant contain conflicting values.",
        ),
        (
            "DUPLICATE_APPLICATION_DISBURSEMENT",
            "event_history.csv",
            selected[4]["loan_id"],
            "The same loan has more than one disbursement event.",
        ),
    ]

    for index, (anomaly_type, target_file, target_id, description) in enumerate(
        anomaly_definitions, start=1
    ):
        ground_truth.append({
            "anomaly_id": f"ANOM-{index:03d}",
            "anomaly_type": anomaly_type,
            "target_file": target_file,
            "target_id": target_id,
            "description": description,
            "injected": "false",
        })

    return ground_truth


if __name__ == "__main__":
    ground_truth = generate_anomalies()
    save_csv(TRANSACTION_DIR / "ground_truth.csv", ground_truth)
    print("Ground-truth labels created.")
    print(
        "Note: These are anomaly labels only; actual anomaly injection "
        "will be implemented in the next step."
    )
