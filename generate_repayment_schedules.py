
import csv
from pathlib import Path

MASTER_DIR = Path("data") / "master"
TRANSACTION_DIR = Path("data") / "transactions"


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


def generate_schedules():
    applications = load_csv(TRANSACTION_DIR / "loan_applications.csv")
    decisions = load_csv(TRANSACTION_DIR / "decisions.csv")
    products = load_csv(MASTER_DIR / "loan_products.csv")

    decision_lookup = {d["loan_id"]: d for d in decisions}
    product_lookup = {p["product_id"]: p for p in products}

    schedules = []

    for app in applications:
        decision = decision_lookup.get(app["loan_id"])

        if not decision or decision["decision_outcome"] != "approve":
            continue

        product = product_lookup[app["product_id"]]
        principal = float(app["requested_principal"])
        months = int(app["requested_term_months"])
        monthly_rate = float(product["annual_interest_rate"]) / 100 / 12

        if monthly_rate == 0:
            payment = principal / months
        else:
            payment = (
                principal * monthly_rate * (1 + monthly_rate) ** months
                / ((1 + monthly_rate) ** months - 1)
            )

        balance = principal

        for month in range(1, months + 1):
            interest = round(balance * monthly_rate, 2)
            principal_payment = round(payment - interest, 2)

            if month == months:
                principal_payment = round(balance, 2)
                actual_payment = round(principal_payment + interest, 2)
            else:
                actual_payment = round(principal_payment + interest, 2)

            balance = round(max(0, balance - principal_payment), 2)

            schedules.append({
                "schedule_id": f"SCH-{app['loan_id']}-{month:03d}",
                "loan_id": app["loan_id"],
                "installment_number": month,
                "payment_amount": actual_payment,
                "principal_component": principal_payment,
                "interest_component": interest,
                "remaining_balance": balance,
            })

    return schedules


def validate_schedules(schedules):
    assert all(float(row["payment_amount"]) > 0 for row in schedules)
    assert all(float(row["principal_component"]) >= 0 for row in schedules)
    assert all(float(row["interest_component"]) >= 0 for row in schedules)
    assert all(float(row["remaining_balance"]) >= 0 for row in schedules)

    print("PASS: Payment amounts are positive")
    print("PASS: Principal and interest components are non-negative")
    print("PASS: Remaining balances are non-negative")


if __name__ == "__main__":
    schedules = generate_schedules()

    if schedules:
        validate_schedules(schedules)
        save_csv(TRANSACTION_DIR / "repayment_schedules.csv", schedules)
    else:
        print("No approved loans found; no repayment schedules generated.")

    print("Repayment schedule generation complete.")
