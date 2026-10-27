
import csv
import random
from pathlib import Path

SEED = 20261022
N_APPLICANTS = 10_000

random.seed(SEED)

OUTPUT_DIR = Path("data") / "master"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_csv(filename, rows):
    """Save records to CSV with consistent column names."""
    if not rows:
        raise ValueError(f"No records generated for {filename}")

    path = OUTPUT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}: {len(rows)} rows")


def generate_loan_products():
    return [
        {
            "product_id": "PROD-001",
            "product_name": "Personal Starter",
            "min_principal": 10000,
            "max_principal": 200000,
            "annual_interest_rate": 0.15,
            "min_term_months": 6,
            "max_term_months": 36,
        },
        {
            "product_id": "PROD-002",
            "product_name": "Personal Plus",
            "min_principal": 25000,
            "max_principal": 500000,
            "annual_interest_rate": 0.12,
            "min_term_months": 12,
            "max_term_months": 60,
        },
        {
            "product_id": "PROD-003",
            "product_name": "Education Support",
            "min_principal": 20000,
            "max_principal": 800000,
            "annual_interest_rate": 0.09,
            "min_term_months": 12,
            "max_term_months": 84,
        },
        {
            "product_id": "PROD-004",
            "product_name": "Small Business",
            "min_principal": 50000,
            "max_principal": 1000000,
            "annual_interest_rate": 0.14,
            "min_term_months": 12,
            "max_term_months": 60,
        },
    ]


def generate_applicants(count):
    applicants = []
    employment = []
    income_records = []
    credit_facilities = []

    for i in range(1, count + 1):
        applicant_id = f"APP-2026-{i:06d}"

        applicants.append({
            "applicant_id": applicant_id,
            "age": random.randint(21, 60),
            "residence_years": random.randint(0, 25),
            "created_date": "2026-10-22",
        })

        employment_id = f"EMP-{i:06d}"
        employment_status = random.choices(
            ["employed", "self_employed", "unemployed"],
            weights=[70, 20, 10],
            k=1,
        )[0]

        employment.append({
            "employment_id": employment_id,
            "applicant_id": applicant_id,
            "employment_status": employment_status,
            "employer_name": (
                f"Synthetic Employer {i:04d}"
                if employment_status == "employed"
                else ""
            ),
            "months_in_current_job": (
                random.randint(1, 120)
                if employment_status != "unemployed"
                else 0
            ),
            "effective_from": "2025-01-01",
        })

        # Two income observations per applicant for initial testing.
        for j in range(1, 3):
            income_records.append({
                "income_id": f"INC-{i:06d}-{j:02d}",
                "applicant_id": applicant_id,
                "monthly_income": (
                    random.randint(15000, 150000)
                    if employment_status != "unemployed"
                    else 0
                ),
                "income_source": (
                    "salary"
                    if employment_status == "employed"
                    else "business"
                    if employment_status == "self_employed"
                    else "none"
                ),
                "verified": random.choice([True, False]),
                "recorded_date": (
                    "2026-09-30" if j == 1 else "2026-10-22"
                ),
            })

        # Zero or more existing credit facilities.
        if random.random() < 0.75:
            credit_facilities.append({
                "credit_facility_id": f"CF-{i:06d}",
                "applicant_id": applicant_id,
                "outstanding_balance": random.randint(5000, 300000),
                "monthly_payment": random.randint(500, 15000),
                "status": "active",
                "effective_from": "2026-01-01",
            })

    return applicants, employment, income_records, credit_facilities


def main():
    products = generate_loan_products()

    applicants, employment, incomes, credit = generate_applicants(
        N_APPLICANTS
    )

    save_csv("loan_products.csv", products)
    save_csv("applicants.csv", applicants)
    save_csv("employment.csv", employment)
    save_csv("income_records.csv", incomes)
    save_csv("credit_facilities.csv", credit)

    print("\nMaster data generation complete.")
    print(f"Fixed seed: {SEED}")
    print(f"Applicants requested: {N_APPLICANTS}")


if __name__ == "__main__":
    main()
