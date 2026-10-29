# Design and Validation



## 1. Project Overview



The Loan Decision Engine generates reproducible synthetic loan data, calculates affordability indicators, assigns reason-coded loan decisions, creates repayment schedules and event history, and stores the generated records in SQLite.



The project is intended for data engineering practice and validation of synthetic loan data. It is not a production lending system.



## 2. Data Generation and Reproducibility



- Random seed: `20261022`

- Applicants: 10,000

- Loan applications: 6,000

- Affordability checks: 6,000

- Decisions: 6,000

- Repayment schedule rows: 157,242

- Document metadata rows: 17,993

- Event history rows: 18,000

- Loan products: 4



The generation scripts use a fixed seed to support reproducible synthetic data generation. The manifest and checksum files provide a record of generated artifacts and file integrity.



## 3. Affordability Calculation



The affordability process uses the latest available income record for each applicant and sums monthly payments from active credit facilities.



The proposed monthly loan payment is calculated using the standard amortizing-loan payment formula. Total monthly debt is calculated as existing monthly debt plus the proposed payment.



Debt-to-income ratio (DTI) is calculated as:



`DTI = Total monthly debt / Monthly income`



When monthly income is not positive, DTI is unavailable and is recorded as blank.



## 4. Illustrative Decision Rules



The decision rules are example rules for this synthetic project, not real-world lending guidance.



- Approve when monthly income is positive and DTI is at or below 0.40.

- Send for review when DTI is above 0.40 and at or below 0.50.

- Reject when DTI is above 0.50.

- Send for review when income is not positive or DTI is unavailable.

- Send for review when the affordability check or loan product is missing.



Each decision includes a decision outcome, reason code, rule version, and decision date.



## 5. Validation Performed



The following checks passed during the project run:



- Master-data identifiers are present and unique.

- Master-data references are valid.

- Income and credit amounts are non-negative.

- Loan application IDs are unique and applicant/product references are valid.

- One affordability check is generated per application.

- Generated decision records cover all applications exactly once and use valid outcomes with reason codes.

- Repayment payment amounts are positive and principal, interest, and remaining-balance values satisfy the implemented checks.

- Event IDs are unique, application references are valid, and timestamps are present.

- All five targeted injected anomalies were verified against their expected targets.

- SQLite foreign-key integrity passed.

- The SQLite database was populated with the expected table row counts.



## 6. Injected Anomalies



Five intentional anomalies are generated in separate anomaly datasets:



1\. Loan term outside the product range.

2\. Repayment schedule reconciliation mismatch.

3\. Decision occurring before the affordability check.

4\. Conflicting income records.

5\. Duplicate application disbursement.



The anomaly validation script reported all five injected anomalies as detected and verified. The original generated transaction files are kept separate from the anomaly datasets.



## 7. Current Decision Distribution



For the validated run:



| Outcome | Count |

|---|---:|

| Approve | 4,266 |

| Review | 924 |

| Reject | 810 |

| Total | 6,000 |



These counts describe the generated synthetic dataset and should not be interpreted as real lending performance.



## 8. Limitations and Next Steps



- The dataset is synthetic and does not represent actual customers or lending outcomes.

- Decision thresholds are illustrative and have not been calibrated against real repayment outcomes or regulatory requirements.

- The project does not establish that the rules are suitable for production credit decisions.

- Further work could include stronger cross-file consistency checks, additional edge-case tests, and independent review of the decision rules.
