
import csv
from pathlib import Path

TRANSACTION_DIR = Path("data") / "transactions"
MASTER_DIR = Path("data") / "master"

# Example thresholds for this synthetic challenge only.
MAX_DTI = 0.40
REVIEW_DTI = 0.50


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


def generate_decisions():
    applications = load_csv(TRANSACTION_DIR / "loan_applications.csv")
    checks = load_csv(TRANSACTION_DIR / "affordability_checks.csv")
    products = load_csv(MASTER_DIR / "loan_products.csv")

    checks_by_loan = {row["loan_id"]: row for row in checks}
    products_by_id = {row["product_id"]: row for row in products}

    decisions = []

    for app in applications:
        loan_id = app["loan_id"]
        check = checks_by_loan.get(loan_id)
        product = products_by_id.get(app["product_id"])

        reasons = []
        outcome = "review"

        if check is None:
            reasons.append("AFFORDABILITY_CHECK_MISSING")
        elif product is None:
            reasons.append("LOAN_PRODUCT_MISSING")
        else:
            income = float(check["monthly_income"])
            dti_text = check["debt_to_income_ratio"]
            dti = float(dti_text) if dti_text else None

            # Missing or unverified information needs manual review.
            if income <= 0:
                reasons.append("NO_POSITIVE_MONTHLY_INCOME")
            if dti is None:
                reasons.append("DTI_UNAVAILABLE")

            if income <= 0 or dti is None:
                outcome = "review"
                reasons.append("MANUAL_REVIEW_REQUIRED")
            elif dti <= MAX_DTI:
                outcome = "approve"
                reasons.append("DTI_WITHIN_EXAMPLE_THRESHOLD")
            elif dti <= REVIEW_DTI:
                outcome = "review"
                reasons.append("DTI_ABOVE_APPROVAL_THRESHOLD")
            else:
                outcome = "reject"
                reasons.append("DTI_ABOVE_REVIEW_THRESHOLD")

        decisions.append({
            "decision_id": f"DEC-{loan_id}",
            "loan_id": loan_id,
            "decision_outcome": outcome,
            "decision_reason_codes": "|".join(reasons),
            "decision_rule_version": "1.0",
            "decision_date": "2026-10-22",
        })

    return decisions


def validate_decisions(decisions, applications):
    allowed = {"approve", "review", "reject"}
    loan_ids = [row["loan_id"] for row in decisions]
    application_ids = {row["loan_id"] for row in applications}

    assert len(loan_ids) == len(set(loan_ids)), "Duplicate decisions"
    assert set(loan_ids) == application_ids, (
        "Every application must have exactly one decision"
    )
    assert all(row["decision_outcome"] in allowed for row in decisions)
    assert all(row["decision_reason_codes"] for row in decisions)

    print("PASS: Exactly one decision per application")
    print("PASS: All outcomes are valid")
    print("PASS: Every decision has a reason code")


if __name__ == "__main__":
    applications = load_csv(TRANSACTION_DIR / "loan_applications.csv")
    decisions = generate_decisions()
    validate_decisions(decisions, applications)
    save_csv(TRANSACTION_DIR / "decisions.csv", decisions)

    print("Loan decision generation complete.")
