
import csv
from pathlib import Path

DATA_DIR = Path("data") / "master"


def load_csv(filename):
    path = DATA_DIR / filename

    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def check_unique_ids(rows, id_field):
    ids = [row[id_field] for row in rows]

    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate IDs found in {id_field}")

    if any(not value for value in ids):
        raise ValueError(f"Missing IDs found in {id_field}")

    print(f"PASS: {id_field} are unique and present")


def check_foreign_keys(child_rows, child_field, parent_ids):
    invalid = [
        row[child_field]
        for row in child_rows
        if row[child_field] not in parent_ids
    ]

    if invalid:
        raise ValueError(
            f"Invalid references in {child_field}: {invalid[:5]}"
        )

    print(f"PASS: {child_field} references are valid")


def main():
    applicants = load_csv("applicants.csv")
    employment = load_csv("employment.csv")
    incomes = load_csv("income_records.csv")
    credit = load_csv("credit_facilities.csv")
    products = load_csv("loan_products.csv")

    # Primary key checks
    check_unique_ids(applicants, "applicant_id")
    check_unique_ids(employment, "employment_id")
    check_unique_ids(incomes, "income_id")
    check_unique_ids(credit, "credit_facility_id")
    check_unique_ids(products, "product_id")

    # Foreign key checks
    applicant_ids = {r["applicant_id"] for r in applicants}

    check_foreign_keys(
        employment, "applicant_id", applicant_ids
    )
    check_foreign_keys(
        incomes, "applicant_id", applicant_ids
    )
    check_foreign_keys(
        credit, "applicant_id", applicant_ids
    )

    # Basic domain checks
    for row in incomes:
        if int(row["monthly_income"]) < 0:
            raise ValueError("Negative monthly income found")

    for row in credit:
        if int(row["outstanding_balance"]) < 0:
            raise ValueError("Negative credit balance found")
        if int(row["monthly_payment"]) < 0:
            raise ValueError("Negative monthly payment found")

    print("PASS: Income and credit amounts are non-negative")
    print("\nAll master-data validation checks passed!")
    print(f"Applicants: {len(applicants)}")
    print(f"Employment: {len(employment)}")
    print(f"Income records: {len(incomes)}")
    print(f"Credit facilities: {len(credit)}")
    print(f"Loan products: {len(products)}")


if __name__ == "__main__":
    main()
