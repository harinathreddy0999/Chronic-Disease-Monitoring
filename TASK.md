# Project Tasks

## Current Tasks
- [x] Create project directory structure (folders: `data`, `scripts`, `dashboard`, `outputs`).
- [x] Create `requirements.txt`.
- [x] Create `README.md`.

## Task Backlog

### 1. Data Loading (`scripts/load_data.py`)
- [x] Load `fhir_sample_data.json`.
- [x] Define function to normalize FHIR bundles into pandas DataFrames (Patients, Observations, etc.).

### 2. Patient Processing (`scripts/process_patients.py`)
- [x] Define function to extract relevant patient information (ID, name, demographics).

### 3. Risk Scoring (`scripts/risk_scoring.py`)
- [x] Define function to extract latest Hemoglobin A1c values for each patient.
- [x] Define function to extract latest Cholesterol values for each patient.
- [x] Implement Diabetes risk rule (HbA1c ≥ 6.5).
- [x] Implement Heart Disease risk rule (Cholesterol ≥ 240).
- [x] Create a combined risk score or flagging system.

### 4. Report Generation (`scripts/generate_report.py`)
- [x] Define function to filter for high-risk patients.
- [x] Generate CSV report (`outputs/high_risk_report.csv`) with patient ID, name, risk reason, lab values.
- [x] (Optional) Generate JSON report.

### 5. (Optional) Dashboard (`dashboard/streamlit_app.py`)
- [x] Set up basic Streamlit app.
- [x] Load generated report data.
- [x] Create UI to display and filter high-risk patients.
- [x] Add basic visualizations (e.g., risk distribution).

## Next Steps
- [ ] Test the application with the FHIR sample data.
- [ ] Create documentation on how to run the application.
- [ ] Consider adding more risk factors and medical insights.
- [ ] Improve visualizations with more in-depth analysis. 