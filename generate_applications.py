
import csv
import random
from pathlib import Path

SEED = 20261022
N_APPLICATIONS = 6_000

MASTER_DIR = Path("data") / "master"
OUTPUT_DIR = Path("data") / "transactions"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

rng = random.Random(SEED + 1)


def load_csv(filename):
    with (MASTER_DIR / filename).open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def save_csv(filename, rows):
    if not rows:
        raise ValueError("Cannot save an empty dataset")

    with (OUTPUT_DIR / filename).open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {filename}: {len(rows)} rows")


def generate_applications():
    applicants = load_csv("applicants.csv")
    products = load_csv("loan_products.csv")

    if not applicants or not products:
        raise ValueError("Master data must exist before applications")

    applications = []

    for i in range(1, N_APPLICATIONS + 1):
        applicant = rng.choice(applicants)
        product = rng.choice(products)

        min_amount = int(product["min_principal"])
        max_amount = int(product["max_principal"])
        min_term = int(product["min_term_months"])
        max_term = int(product["max_term_months"])

        # Generate valid baseline applications first.
        principal = rng.randrange(
            (min_amount + 999) // 1000,
            max_amount // 1000 + 1,
        ) * 1000

        term = rng.randint(min_term, max_term)

        applications.append({
            "loan_id": f"LOAN-2026-{i:06d}",
            "applicant_id": applicant["applicant_id"],
            "product_id": product["product_id"],
            "requested_principal": principal,
            "requested_term_months": term,
            "application_date": "2026-10-22",
            "application_status": "submitted",
        })

    return applications


def validate_applications(applications):
    applicants = load_csv("applicants.csv")
    products = load_csv("loan_products.csv")

    applicant_ids = {row["applicant_id"] for row in applicants}
    product_lookup = {row["product_id"]: row for row in products}
    loan_ids = [row["loan_id"] for row in applications]

    assert len(loan_ids) == len(set(loan_ids)), "Duplicate loan IDs"

    for app in applications:
        assert app["applicant_id"] in applicant_ids, (
            f"Invalid applicant: {app['applicant_id']}"
        )
        assert app["product_id"] in product_lookup, (
            f"Invalid product: {app['product_id']}"
        )

        product = product_lookup[app["product_id"]]
        amount = int(app["requested_principal"])
        term = int(app["requested_term_months"])

        assert int(product["min_principal"]) <= amount <= int(
            product["max_principal"]
        ), f"Invalid principal: {app['loan_id']}"

        assert int(product["min_term_months"]) <= term <= int(
            product["max_term_months"]
        ), f"Invalid term: {app['loan_id']}"

    print("PASS: Loan IDs are unique")
    print("PASS: Applicant and product references are valid")
    print("PASS: All baseline amounts and terms are within limits")


if __name__ == "__main__":
    applications = generate_applications()
    validate_applications(applications)
    save_csv("loan_applications.csv", applications)
    print("Loan application generation complete.")
    print(f"Fixed seed: {SEED}")
