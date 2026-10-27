
import csv
import json
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = Path("docs")
OUTPUT_DIR.mkdir(exist_ok=True)

DESCRIPTIONS = {
    "applicant_id": "Unique identifier for an applicant.",
    "employment_id": "Unique identifier for an employment record.",
    "income_id": "Unique identifier for an income record.",
    "credit_facility_id": "Unique identifier for an existing credit facility.",
    "product_id": "Unique identifier for a loan product.",
    "loan_id": "Unique identifier for a loan application.",
    "requested_principal": "Loan principal requested by the applicant.",
    "requested_term_months": "Requested loan term in months.",
    "monthly_income": "Recorded monthly income in the dataset's currency.",
    "monthly_payment": "Monthly payment on an existing credit facility.",
    "annual_interest_rate": "Annual interest rate expressed as a percentage.",
    "affordability_check_id": "Unique identifier for an affordability check.",
    "debt_to_income_ratio": "Total monthly debt divided by monthly income.",
    "decision_id": "Unique identifier for a loan decision.",
    "decision_outcome": "Recorded outcome of the decision rules.",
    "schedule_id": "Unique identifier for a repayment installment.",
    "installment_number": "Sequential installment number.",
    "payment_amount": "Total amount due for an installment.",
    "principal_component": "Principal repaid in an installment.",
    "interest_component": "Interest charged in an installment.",
    "remaining_balance": "Principal balance remaining after an installment.",
    "event_id": "Unique identifier for an application event.",
    "event_type": "Type of event recorded in the workflow.",
    "event_timestamp": "Timestamp associated with the event.",
    "anomaly_id": "Unique identifier for an anomaly label.",
    "anomaly_type": "Category of deliberately injected data issue.",
}


def main():
    dictionary = []

    for folder in ["master", "transactions", "anomalies"]:
        directory = DATA_DIR / folder
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*.csv")):
            with path.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames or []

            for column in columns:
                dictionary.append({
                    "dataset": f"{folder}/{path.name}",
                    "column_name": column,
                    "data_type": "string",
                    "description": DESCRIPTIONS.get(
                        column, "Description to be reviewed."
                    ),
                })

    csv_path = OUTPUT_DIR / "data_dictionary.csv"
    if dictionary:
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "dataset", "column_name", "data_type", "description"
                ],
            )
            writer.writeheader()
            writer.writerows(dictionary)

    json_path = OUTPUT_DIR / "data_dictionary.json"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(dictionary, file, indent=2)

    print(f"Created {csv_path}: {len(dictionary)} column definitions")
    print(f"Created {json_path}")


if __name__ == "__main__":
    main()
