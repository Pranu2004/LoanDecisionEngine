
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


def generate_affordability_checks():
    applications = load_csv(TRANSACTION_DIR / "loan_applications.csv")
    income_records = load_csv(MASTER_DIR / "income_records.csv")
    credit_facilities = load_csv(MASTER_DIR / "credit_facilities.csv")
    products = load_csv(MASTER_DIR / "loan_products.csv")

    # Use the most recent income record for each applicant.
    latest_income = {}
    for record in income_records:
        applicant_id = record["applicant_id"]

        if (
            applicant_id not in latest_income
            or record["recorded_date"] > latest_income[applicant_id]["recorded_date"]
        ):
            latest_income[applicant_id] = record

    # Sum monthly payments on existing credit facilities.
    monthly_debt = {}
    for facility in credit_facilities:
        applicant_id = facility["applicant_id"]

        if facility["status"].lower() == "active":
            monthly_debt[applicant_id] = (
                monthly_debt.get(applicant_id, 0)
                + float(facility["monthly_payment"])
            )

    product_lookup = {p["product_id"]: p for p in products}
    checks = []

    for app in applications:
        applicant_id = app["applicant_id"]
        income = latest_income.get(applicant_id)

        monthly_income = float(income["monthly_income"]) if income else 0
        existing_debt = monthly_debt.get(applicant_id, 0)

        product = product_lookup[app["product_id"]]
        annual_rate = float(product["annual_interest_rate"]) / 100
        monthly_rate = annual_rate / 12
        principal = float(app["requested_principal"])
        months = int(app["requested_term_months"])

        if monthly_rate == 0:
            proposed_payment = principal / months
        else:
            proposed_payment = (
                principal
                * monthly_rate
                * (1 + monthly_rate) ** months
                / ((1 + monthly_rate) ** months - 1)
            )

        total_monthly_debt = existing_debt + proposed_payment
        dti = (
            total_monthly_debt / monthly_income
            if monthly_income > 0
            else None
        )

        checks.append({
            "affordability_check_id": f"AFF-{app['loan_id']}",
            "loan_id": app["loan_id"],
            "monthly_income": round(monthly_income, 2),
            "existing_monthly_debt": round(existing_debt, 2),
            "proposed_monthly_payment": round(proposed_payment, 2),
            "total_monthly_debt": round(total_monthly_debt, 2),
            "debt_to_income_ratio": round(dti, 4) if dti is not None else "",
            "check_status": "completed",
            "calculation_version": "1.0",
        })

    return checks


def validate_checks(checks):
    loan_ids = [row["loan_id"] for row in checks]

    assert len(loan_ids) == len(set(loan_ids)), "Duplicate affordability checks"
    assert all(float(row["monthly_income"]) >= 0 for row in checks)
    assert all(float(row["proposed_monthly_payment"]) > 0 for row in checks)

    for row in checks:
        ratio = row["debt_to_income_ratio"]
        if ratio != "":
            assert float(ratio) >= 0, "Negative debt-to-income ratio"

    print("PASS: One affordability check per application")
    print("PASS: Income and payment values are valid")
    print("PASS: Debt-to-income ratios are non-negative")


if __name__ == "__main__":
    checks = generate_affordability_checks()
    validate_checks(checks)
    save_csv(TRANSACTION_DIR / "affordability_checks.csv", checks)
    print("Affordability calculation complete.")
