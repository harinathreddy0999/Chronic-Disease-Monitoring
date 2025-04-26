# Clinical Risk Dashboard using FHIR Data

## 🎯 Project Goal / Output
Build an intelligent clinical dashboard that:
- Ingests FHIR-based patient data
- Identifies at-risk patients for diabetes and cardiovascular issues
- Generates insights on medication adherence, lab results, and allergies
- Outputs a summarized report (JSON/CSV + Web Dashboard)

## 🧠 Use Case Summary
Detect patterns in FHIR records that indicate chronic health risks. Flag patients with:
- Hemoglobin A1c (≥ 6.5 for diabetes)
- Cholesterol (≥ 240 for cardiovascular risk)

## 🧱 Tech Stack

| Layer             | Tools/Tech                                                    |
| ----------------- | ------------------------------------------------------------- |
| Language          | Python 3.10+                                                  |
| IDE               | Cursor IDE                                                    |
| Data Format       | FHIR (JSON)                                                   |
| Libraries         | pandas, json, matplotlib/seaborn, fhir.resources (optional), scikit-learn (optional) |
| Visualization (Optional) | Streamlit or Dash                                             |
| Output            | JSON/CSV report & summary tables                              |

## 📁 Project Structure
```
clinical_risk_dashboard/
├── data/
│   └── fhir_sample_data.json
├── scripts/
│   ├── load_data.py
│   ├── process_patients.py
│   ├── risk_scoring.py
│   └── generate_report.py
├── dashboard/
│   └── streamlit_app.py (optional)
├── outputs/
│   └── high_risk_report.csv
├── README.md
├── requirements.txt
├── PLANNING.md
└── TASK.md
```

## 🛠️ How to Proceed – Step-by-Step
1.  **Data Loading:**
    - Load the JSON FHIR data.
    - Normalize into pandas DataFrames: patients, observations, medications, etc.
2.  **Risk Rules Implementation:**
    - For Diabetes risk: Hemoglobin A1c ≥ 6.5
    - For Heart Disease risk: Cholesterol ≥ 240
    - Flag each patient based on their latest lab values.
3.  **Report Generation:**
    - Output high-risk patients into CSV/JSON.
    - Include patient ID, name, reason for flagging, lab values.
4.  **(Optional) Visualization:**
    - Build a Streamlit/Dash UI to explore patients by risk level.
5.  **Evaluation / Deliverables:**
    - Code to extract and analyze FHIR data.
    - Risk scoring system.
    - Summary report.
    - (Optional) UI for stakeholder demo.

## 🔚 End Output
- Risk-scored patient list.
- Insightful trends in population health.
- Actionable insights for clinicians or decision support systems. 