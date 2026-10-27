
import csv
import random
from pathlib import Path

SEED = 20261022
DATA_DIR = Path("data")
OUTPUT_DIR = DATA_DIR / "transactions"
APPLICATIONS_FILE = OUTPUT_DIR / "loan_applications.csv"
OUTPUT_FILE = OUTPUT_DIR / "documents.csv"

DOCUMENT_TYPES = [
    "IDENTITY_PROOF",
    "ADDRESS_PROOF",
    "INCOME_PROOF",
    "BANK_STATEMENT",
]

DOCUMENT_STATUSES = [
    "RECEIVED",
    "VERIFIED",
    "PENDING",
    "REJECTED",
]


def main():
    random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with APPLICATIONS_FILE.open(
        "r", newline="", encoding="utf-8"
    ) as file:
        applications = list(csv.DictReader(file))

    fields = [
        "document_id",
        "loan_id",
        "document_type",
        "document_status",
        "submitted_at",
    ]

    rows = []
    document_number = 1

    for application in applications:
        # Generate 2–4 synthetic document records per loan.
        number_of_documents = random.randint(2, 4)

        for _ in range(number_of_documents):
            rows.append({
                "document_id": f"DOC{document_number:07d}",
                "loan_id": application["loan_id"],
                "document_type": random.choice(DOCUMENT_TYPES),
                "document_status": random.choice(DOCUMENT_STATUSES),
                "submitted_at": application["application_date"],
            })
            document_number += 1

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Applications processed: {len(applications)}")
    print(f"Documents generated: {len(rows)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
