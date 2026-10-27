# Loan Decision Engine

## Overview

The **Loan Decision Engine** is a reproducible Python-based synthetic loan-processing data pipeline. It generates interconnected datasets for applicants, employment, income, credit facilities, loan products, applications, affordability checks, decisions, repayment schedules, documents, and event history.

The project demonstrates relational data generation, affordability calculations, explainable decision rules, database loading, data validation, reproducibility, and anomaly injection for testing.

All records are synthetic and intended for engineering and testing purposes.

## Key Features

- Reproducible synthetic data generation using a fixed random seed.
- Relational master and transaction datasets with identifiers and references.
- Debt-to-income (DTI) calculations and affordability checks.
- Explainable loan decisions with outcome and reason codes.
- Repayment schedule generation.
- Synthetic document metadata and application event history.
- SQLite database creation and foreign-key validation.
- Targeted anomaly injection and validation.
- Data dictionary, source manifest, and SHA-256 checksum file.

## Dataset Summary

| Dataset | Expected records |
|---|---:|
| Applicants | 10,000 |
| Employment records | 10,000 |
| Income records | 20,000 |
| Credit facilities | 7,487 |
| Loan products | 4 |
| Loan applications | 6,000 |
| Affordability checks | 6,000 |
| Decisions | 6,000 |
| Repayment schedule entries | 157,242 |
| Document metadata records | 17,993 |
| Event history records | 18,000 |

Counts reflect the current generated dataset. Counts may change if generation logic or configuration changes.

## Technologies

- Python 3
- CSV and JSON
- SQLite
- SQL
- Python standard library

## Project Structure

```text
LoanDecisionEngine/
├── data/
│   ├── master/
│   ├── transactions/
│   └── anomalies/
├── docs/
│   ├── data_dictionary.csv
│   └── data_dictionary.json
├── sql/
│   └── schema.sql
├── database/                  # Local database; excluded from Git
├── generate_master_data.py
├── validate_master_data.py
├── generate_applications.py
├── generate_affordability.py
├── generate_decisions.py
├── generate_repayment_schedules.py
├── generate_event_history.py
├── generate_documents.py
├── generate_anomalies.py
├── inject_anomalies.py
├── validate_anomalies.py
├── generate_data_dictionary.py
├── generate_manifest.py
├── load_sqlite.py
├── check_database.py
├── source_manifest.json
├── checksums.sha256
├── .gitignore
└── README.md
```

## Setup

### Requirements

- Python 3.10 or later recommended.
- Git (optional, for version control).
- No third-party Python packages are required if the scripts use only the Python standard library.

Open a terminal in the project root directory.

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

## Run Order

Run each command separately from the project root.

### 1. Generate master data

```powershell
python generate_master_data.py
python validate_master_data.py
```

### 2. Generate loan applications and affordability checks

```powershell
python generate_applications.py
python generate_affordability.py
```

### 3. Generate decisions and repayment schedules

```powershell
python generate_decisions.py
python generate_repayment_schedules.py
```

### 4. Generate event history and document metadata

```powershell
python generate_event_history.py
python generate_documents.py
```

### 5. Generate and validate anomaly test data

```powershell
python generate_anomalies.py
python inject_anomalies.py
python validate_anomalies.py
```

### 6. Generate metadata and checksums

```powershell
python generate_data_dictionary.py
python generate_manifest.py
```

### 7. Create and verify the SQLite database

```powershell
python load_sqlite.py
python check_database.py
```

**Important:** Run the generators in the order shown. If you regenerate datasets, rerun the downstream scripts and validations so the outputs remain consistent. Regenerating anomaly datasets may overwrite existing injected test data.

## Database

The SQL schema is provided in `sql/schema.sql`. The database loader creates a local SQLite database at:

```text
database/loan_decision_engine.db
```

The loader imports the generated CSV datasets into relational tables and checks foreign-key integrity. The database is a local generated artifact and is excluded from version control; run the loader to recreate it.

Use `check_database.py` to inspect table names and record counts.

## Affordability and Decision Logic

The affordability pipeline calculates proposed monthly repayments, total monthly debt, and debt-to-income ratio from synthetic income, existing debt, and proposed loan payments.

The decision pipeline applies illustrative rules to produce outcomes such as approval, review, or rejection, together with reason codes.

These rules are designed for engineering demonstration and **are not a validated lending policy or financial advice**.

## Anomaly Testing

The anomaly test data contains examples of:

- Loan terms outside the associated product's permitted range.
- Repayment schedule reconciliation mismatches.
- Decisions recorded before affordability checks.
- Conflicting income records.
- Duplicate application disbursement events.

The anomaly datasets and `ground_truth.csv` files identify intended test cases. The validation script checks the injected anomaly targets.

**Evaluation note:** If this repository is used for a challenge or assessment, confirm whether ground-truth labels should be kept separate from the publicly accessible submission before publishing them.

## Reproducibility and Integrity

The generators use the fixed random seed `20261022` where configured, supporting repeatable synthetic data generation.

The repository includes:

- `source_manifest.json` — manifest of generated data files.
- `checksums.sha256` — SHA-256 checksums for the files included by the manifest-generation script.
- `docs/data_dictionary.csv` and `docs/data_dictionary.json` — descriptions of dataset fields.

Regenerate the manifest and checksums after changing generated datasets. Reproducibility also depends on keeping the generator code and configuration unchanged.

## Data Limitations

- All records are synthetic; they do not represent real applicants or customers.
- Document records contain metadata, not actual identity or financial documents.
- Decision rules are simplified and intended for testing, not production lending.
- Validation coverage can be extended with additional boundary cases, relationship checks, and reconciliation tests.

## Disclaimer

This project is an educational data-engineering demonstration. It must not be used to make real credit decisions or process real customer financial information.
