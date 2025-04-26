# Clinical Risk Dashboard using FHIR Data

This project builds a dashboard to identify patients at risk for chronic diseases (Diabetes, Cardiovascular issues) using FHIR data.

## Overview

The Clinical Risk Dashboard analyzes patient health data in FHIR format to identify individuals at risk for diabetes and cardiovascular disease based on clinical markers:
- Diabetes Risk: Hemoglobin A1c ≥ 6.5%
- Cardiovascular Risk: Cholesterol ≥ 240 mg/dL

## Project Structure

Refer to `PLANNING.md` for project architecture and details.
Refer to `TASK.md` for the current task status.

```
clinical_risk_dashboard/
├── data/
│   └── fhir_sample_data.json  # Sample FHIR data
├── scripts/
│   ├── __init__.py          # Makes scripts a package
│   ├── load_data.py           # Load and normalize FHIR data
│   ├── process_patients.py    # Process patient information
│   ├── risk_scoring.py        # Apply risk rules
│   └── generate_report.py     # Generate risk reports
├── dashboard/
│   └── streamlit_app.py       # Interactive dashboard
├── outputs/                   # Generated reports and visualizations
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── PLANNING.md                # Project plan
└── TASK.md                    # Task tracking
```

## Setup

1. Clone the repository.
2. Navigate to the project directory:
   ```bash
   cd clinical_risk_dashboard # Or your project folder name
   ```
3. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Dashboard (Recommended)

From the project root directory (`clinical_risk_dashboard/`), run:

```bash
streamlit run dashboard/streamlit_app.py
```

This will start the dashboard on your local machine (typically at http://localhost:8501).

### Running Individual Scripts

You can also run the individual scripts from the project root directory to generate reports:

```bash
# Generate reports
python scripts/generate_report.py

# Process patient data
python scripts/process_patients.py

# Score patient risks
python scripts/risk_scoring.py
```

## Features

1. **Data Loading**: Load and normalize FHIR patient data, observations, medications, and allergies.
2. **Patient Processing**: Extract and enrich patient demographic information.
3. **Risk Scoring**: Apply clinical rules to identify at-risk patients.
4. **Report Generation**: Create CSV and JSON reports of high-risk patients.
5. **Interactive Dashboard**: Filter and explore patient risk data with visualizations.

## Dashboard Features

- View high-risk patients
- Filter by risk category and age
- Detailed patient views with lab values
- Population-level visualizations
- Risk distribution analytics

## Sample Data

The project includes a sample FHIR dataset in the `data/` directory. This synthetic data contains:
- Patient demographics
- Lab observations (HbA1c, Cholesterol)
- Medication information
- Allergy data

## License

[Add your license information here] 