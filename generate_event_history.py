
import csv
from pathlib import Path

TRANSACTION_DIR = Path("data") / "transactions"


def load_csv(filename):
    with (TRANSACTION_DIR / filename).open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def save_csv(filename, rows):
    if not rows:
        raise ValueError(f"No rows to save: {filename}")

    path = TRANSACTION_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}: {len(rows)} rows")


def generate_events():
    applications = load_csv("loan_applications.csv")
    decisions = load_csv("decisions.csv")
    checks = load_csv("affordability_checks.csv")

    decision_ids = {row["loan_id"] for row in decisions}
    check_ids = {row["loan_id"] for row in checks}

    events = []

    for app in applications:
        loan_id = app["loan_id"]
        timestamp = app["application_date"] + "T09:00:00"

        events.append({
            "event_id": f"EVT-{loan_id}-001",
            "loan_id": loan_id,
            "event_type": "APPLICATION_SUBMITTED",
            "event_timestamp": timestamp,
            "event_status": "completed",
        })

        if loan_id in check_ids:
            events.append({
                "event_id": f"EVT-{loan_id}-002",
                "loan_id": loan_id,
                "event_type": "AFFORDABILITY_CHECK_COMPLETED",
                "event_timestamp": app["application_date"] + "T09:05:00",
                "event_status": "completed",
            })

        if loan_id in decision_ids:
            events.append({
                "event_id": f"EVT-{loan_id}-003",
                "loan_id": loan_id,
                "event_type": "DECISION_RECORDED",
                "event_timestamp": app["application_date"] + "T09:10:00",
                "event_status": "completed",
            })

    return events


def validate_events(events, applications):
    event_ids = [event["event_id"] for event in events]
    loan_ids = {app["loan_id"] for app in applications}

    assert len(event_ids) == len(set(event_ids)), "Duplicate event IDs"
    assert all(event["loan_id"] in loan_ids for event in events)
    assert all(event["event_timestamp"] for event in events)

    print("PASS: Event IDs are unique")
    print("PASS: Every event references a valid application")
    print("PASS: Every event has a timestamp")


if __name__ == "__main__":
    applications = load_csv("loan_applications.csv")
    events = generate_events()
    validate_events(events, applications)
    save_csv("event_history.csv", events)
    print("Event history generation complete.")
