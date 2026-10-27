# Loan Decision Engine

## Overview

A reproducible synthetic loan-processing data pipeline built with Python. It generates loan master data, applications, affordability calculations, explainable decisions, repayment schedules, event history, and labelled anomaly test data.

## Dataset Summary

| Dataset | Expected records |
|---|---:|
| Applicants | 10,000 |
| Employment records | 10,000 |
| Income records | 20,000 |
| Loan products | 4 |
| Loan applications | 6,000 |
| Affordability checks | 6,000 |
| Decisions | 6,000 |

Repayment schedules and event-history counts depend on the generated applications and decisions.

## Technologies

- Python 3
- CSV-based synthetic datasets
- Python standard library

## Reproducibility

The generators use the fixed seed `20261022` for repeatable synthetic data generation. Run scripts from the project root using the same Python environment.

## Project Structure

```text
LoanDecisionEngine/
├── data/
│   ├── master/
│   ├── transactions/
│   └── anomalies/
├── generate_master_data.py
├── validate_master_data.py
├── generate_applications.py
├── generate_affordability.py
├── generate_decisions.py
├── generate_repayment_schedules.py
├── generate_event_history.py
├── generate_anomalies.py
├── inject_anomalies.py
├── validate_anomalies.py
└── README.md
```

## Run Order

Run these commands from the project root:

```powershell
python generate_master_data.py
python validate_master_data.py
python generate_applications.py
python generate_affordability.py
python generate_decisions.py
python generate_repayment_schedules.py
python generate_event_history.py
python generate_anomalies.py
python inject_anomalies.py
python validate_anomalies.py
```

## Affordability and Decisions

The affordability script estimates monthly repayments and calculates a debt-to-income ratio using the available synthetic income and credit data.

The decision script applies illustrative, explainable rules and records a reason code. These rules are for engineering demonstration only and are not a validated lending policy.

## Anomaly Testing

The anomaly dataset is kept separate from the clean source data. It includes examples of:

- Loan term outside product limits
- Repayment schedule reconciliation mismatch
- Decision before affordability check
- Conflicting income records
- Duplicate disbursement events

`ground_truth.csv` records the intended anomaly types. The final validation should verify each labelled anomaly against its specific target record.

## Data Limitations

All records are synthetic and intended for testing. The dataset does not represent real customers or actual lending decisions. Validation and rule coverage should be expanded before production use.
