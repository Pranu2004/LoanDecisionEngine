# AI Prompt History



## Purpose



This document records AI assistance used during development of the Loan Decision Engine. It summarizes the assistance and development activities documented during the project review. It is not represented as a verbatim export of every AI conversation.



## AI-Assisted Development Activities



### 1. Review of affordability calculations



**Prompt topic:** Review the affordability-generation code and explain how monthly debt-to-income ratio (DTI) is calculated.



**Assistance received:** Reviewed the calculation using the latest income record, active credit-facility payments, proposed loan payment, and monthly income. Identified validation improvements worth considering.



**Developer review:** Examined the existing Python implementation and its generated output.



### 2. Review of decision outcomes



**Prompt topic:** Investigate the decision outcome distribution and assess how the current approval, review, and rejection rules behave.



**Assistance received:** Compared the decision-generation logic with the observed DTI ranges and recommended explicitly documenting the illustrative thresholds.



**Developer review and change:** Updated the decision logic to approve applications with positive income and DTI at or below 0.40, send DTI above 0.40 through 0.50 to review, reject DTI above 0.50, and send unavailable DTI or non-positive income to review.



### 3. Validation and consistency checks



**Prompt topic:** Identify an appropriate sequence for validating generated data, injected anomalies, and SQLite contents.



**Assistance received:** Recommended running the existing validation scripts and rebuilding the dataset in the documented pipeline order after changing decision logic.



**Developer verification:** Regenerated the data, validated master records, verified all five injected anomalies, rebuilt SQLite, and checked foreign-key integrity and table row counts.



### 4. Documentation support



**Prompt topic:** Draft design and validation documentation describing the synthetic data pipeline, assumptions, decision rules, validation results, and limitations.



**Assistance received:** Helped organize the design and validation documentation.



**Developer review:** Reviewed the proposed content against the scripts and outputs reported during the project workflow.



## Limitations of This Record



This is a summary of AI-assisted activities, not a complete verbatim prompt transcript. Exact prompt wording and timestamps for every earlier AI interaction have not been reconstructed here. Any additional AI tools used during development should be documented separately using their actual prompt records.



The developer remains responsible for reviewing, understanding, running, and validating the submitted code. The decision thresholds are illustrative assumptions for synthetic data and are not presented as production lending policy.
