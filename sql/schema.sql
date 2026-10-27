
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Applicant (
    applicant_id TEXT PRIMARY KEY,
    age INTEGER,
    residence_years INTEGER,
    created_date TEXT
);

CREATE TABLE IF NOT EXISTS Employment (
    employment_id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    employment_status TEXT,
    employer_name TEXT,
    months_in_current_job INTEGER,
    effective_from TEXT,
    FOREIGN KEY (applicant_id) REFERENCES Applicant(applicant_id)
);

CREATE TABLE IF NOT EXISTS IncomeRecord (
    income_id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    monthly_income REAL NOT NULL CHECK (monthly_income >= 0),
    income_source TEXT,
    verified TEXT,
    recorded_date TEXT,
    FOREIGN KEY (applicant_id) REFERENCES Applicant(applicant_id)
);

CREATE TABLE IF NOT EXISTS CreditFacility (
    credit_facility_id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    outstanding_balance REAL CHECK (outstanding_balance >= 0),
    monthly_payment REAL CHECK (monthly_payment >= 0),
    status TEXT,
    effective_from TEXT,
    FOREIGN KEY (applicant_id) REFERENCES Applicant(applicant_id)
);

CREATE TABLE IF NOT EXISTS LoanProduct (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    min_principal REAL NOT NULL,
    max_principal REAL NOT NULL,
    annual_interest_rate REAL NOT NULL,
    min_term_months INTEGER NOT NULL,
    max_term_months INTEGER NOT NULL,
    CHECK (min_principal <= max_principal),
    CHECK (min_term_months <= max_term_months)
);

CREATE TABLE IF NOT EXISTS LoanApplication (
    loan_id TEXT PRIMARY KEY,
    applicant_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    requested_principal REAL NOT NULL,
    requested_term_months INTEGER NOT NULL,
    application_date TEXT,
    application_status TEXT,
    FOREIGN KEY (applicant_id) REFERENCES Applicant(applicant_id),
    FOREIGN KEY (product_id) REFERENCES LoanProduct(product_id)
);

CREATE TABLE IF NOT EXISTS AffordabilityCheck (
    affordability_check_id TEXT PRIMARY KEY,
    loan_id TEXT NOT NULL UNIQUE,
    monthly_income REAL NOT NULL,
    existing_monthly_debt REAL NOT NULL,
    proposed_monthly_payment REAL NOT NULL,
    total_monthly_debt REAL NOT NULL,
    debt_to_income_ratio REAL,
    check_status TEXT,
    calculation_version TEXT,
    FOREIGN KEY (loan_id) REFERENCES LoanApplication(loan_id)
);

CREATE TABLE IF NOT EXISTS Decision (
    decision_id TEXT PRIMARY KEY,
    loan_id TEXT NOT NULL UNIQUE,
    decision_outcome TEXT NOT NULL,
    decision_reason_codes TEXT NOT NULL,
    decision_rule_version TEXT,
    decision_date TEXT,
    FOREIGN KEY (loan_id) REFERENCES LoanApplication(loan_id)
);

CREATE TABLE IF NOT EXISTS RepaymentSchedule (
    schedule_id TEXT PRIMARY KEY,
    loan_id TEXT NOT NULL,
    installment_number INTEGER,
    payment_amount REAL,
    principal_component REAL,
    interest_component REAL,
    remaining_balance REAL,
    UNIQUE (loan_id, installment_number),
    FOREIGN KEY (loan_id) REFERENCES LoanApplication(loan_id)
);

CREATE TABLE IF NOT EXISTS Document (
    document_id TEXT PRIMARY KEY,
    loan_id TEXT NOT NULL,
    document_type TEXT,
    document_status TEXT,
    submitted_at TEXT,
    FOREIGN KEY (loan_id) REFERENCES LoanApplication(loan_id)
);

CREATE TABLE IF NOT EXISTS EventHistory (
    event_id TEXT PRIMARY KEY,
    loan_id TEXT NOT NULL,
    event_type TEXT,
    event_timestamp TEXT,
    event_status TEXT,
    FOREIGN KEY (loan_id) REFERENCES LoanApplication(loan_id)
);

CREATE INDEX IF NOT EXISTS idx_application_applicant
    ON LoanApplication(applicant_id);

CREATE INDEX IF NOT EXISTS idx_income_applicant
    ON IncomeRecord(applicant_id);

CREATE INDEX IF NOT EXISTS idx_events_loan_timestamp
    ON EventHistory(loan_id, event_timestamp);
