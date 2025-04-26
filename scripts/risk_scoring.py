#!/usr/bin/env python3
"""
Implement risk scoring rules for diabetes and cardiovascular disease.
"""
import pandas as pd
from pathlib import Path

# Import from our local modules
import scripts.load_data as load_data
import scripts.process_patients as process_patients

# Define risk thresholds
DIABETES_HBA1C_THRESHOLD = 6.5
CARDIOVASCULAR_CHOLESTEROL_THRESHOLD = 240

def get_latest_lab_values(observations_df):
    """
    Extract the latest lab values (HbA1c and Cholesterol) for each patient.
    
    Args:
        observations_df (pandas.DataFrame): DataFrame with observation data
        
    Returns:
        pandas.DataFrame: DataFrame with latest lab values per patient
    """
    # Filter for HbA1c and Cholesterol observations
    hba1c_obs = observations_df[observations_df['code'].str.lower() == 'hemoglobin a1c']
    cholesterol_obs = observations_df[observations_df['code'].str.lower() == 'cholesterol']
    
    # Get the latest HbA1c for each patient
    latest_hba1c = (hba1c_obs
                   .sort_values(['patient_id', 'date'], ascending=[True, False])
                   .groupby('patient_id')
                   .first()
                   .reset_index()
                   .rename(columns={'value': 'hba1c_value', 'date': 'hba1c_date'})
                   [['patient_id', 'hba1c_value', 'hba1c_date']])
    
    # Get the latest Cholesterol for each patient
    latest_cholesterol = (cholesterol_obs
                         .sort_values(['patient_id', 'date'], ascending=[True, False])
                         .groupby('patient_id')
                         .first()
                         .reset_index()
                         .rename(columns={'value': 'cholesterol_value', 'date': 'cholesterol_date'})
                         [['patient_id', 'cholesterol_value', 'cholesterol_date']])
    
    # Merge the two datasets
    latest_labs = pd.merge(latest_hba1c, latest_cholesterol, on='patient_id', how='outer')
    
    return latest_labs

def apply_diabetes_risk_rule(latest_labs_df):
    """
    Apply Diabetes risk rule: HbA1c ≥ 6.5
    
    Args:
        latest_labs_df (pandas.DataFrame): DataFrame with latest lab values
        
    Returns:
        pandas.DataFrame: DataFrame with diabetes risk flag added
    """
    df = latest_labs_df.copy()
    
    # Apply diabetes risk rule
    df['diabetes_risk'] = df['hba1c_value'] >= DIABETES_HBA1C_THRESHOLD
    
    return df

def apply_cardiovascular_risk_rule(latest_labs_df):
    """
    Apply Cardiovascular risk rule: Cholesterol ≥ 240
    
    Args:
        latest_labs_df (pandas.DataFrame): DataFrame with latest lab values
        
    Returns:
        pandas.DataFrame: DataFrame with cardiovascular risk flag added
    """
    df = latest_labs_df.copy()
    
    # Apply cardiovascular risk rule
    df['cardiovascular_risk'] = df['cholesterol_value'] >= CARDIOVASCULAR_CHOLESTEROL_THRESHOLD
    
    return df

def calculate_combined_risk(risk_df):
    """
    Calculate a combined risk score and category.
    
    Args:
        risk_df (pandas.DataFrame): DataFrame with risk flags
        
    Returns:
        pandas.DataFrame: DataFrame with combined risk score and category
    """
    df = risk_df.copy()
    
    # Initialize risk score (0-2 based on number of risks)
    df['risk_score'] = 0
    
    # Add 1 for diabetes risk
    df.loc[df['diabetes_risk'] == True, 'risk_score'] += 1
    
    # Add 1 for cardiovascular risk
    df.loc[df['cardiovascular_risk'] == True, 'risk_score'] += 1
    
    # Create risk category
    risk_categories = {
        0: 'Low Risk',
        1: 'Moderate Risk',
        2: 'High Risk'
    }
    
    df['risk_category'] = df['risk_score'].map(risk_categories)
    
    # Add reasons for flagging
    df['risk_reasons'] = ''
    
    # Add diabetes reason
    df.loc[df['diabetes_risk'] == True, 'risk_reasons'] += 'Diabetes Risk (HbA1c >= 6.5); '
    
    # Add cardiovascular reason
    df.loc[df['cardiovascular_risk'] == True, 'risk_reasons'] += 'Cardiovascular Risk (Cholesterol >= 240); '
    
    # Trim trailing separator
    df['risk_reasons'] = df['risk_reasons'].str.rstrip('; ')
    
    return df

def score_patient_risks(file_path=None):
    """
    Main function to score patient risks.
    
    Args:
        file_path (str, optional): Path to the FHIR JSON file.
            If None, use default path.
            
    Returns:
        tuple: (patients_with_risks_df, risk_summary)
    """
    # Load data
    patients_df, observations_df, _, _ = load_data.load_and_normalize_data(file_path)
    
    # Enrich patient data
    enriched_patients_df = process_patients.enrich_patient_data(patients_df)
    
    # Get latest lab values
    latest_labs_df = get_latest_lab_values(observations_df)
    
    # Apply risk rules
    risk_df = apply_diabetes_risk_rule(latest_labs_df)
    risk_df = apply_cardiovascular_risk_rule(risk_df)
    
    # Calculate combined risk
    risk_df = calculate_combined_risk(risk_df)
    
    # Merge with patient data
    patients_with_risks_df = pd.merge(enriched_patients_df, risk_df, on='patient_id', how='left')
    
    # Generate risk summary
    risk_summary = {
        'total_patients': len(patients_with_risks_df),
        'diabetes_risk_count': patients_with_risks_df['diabetes_risk'].sum(),
        'cardiovascular_risk_count': patients_with_risks_df['cardiovascular_risk'].sum(),
        'risk_category_counts': patients_with_risks_df['risk_category'].value_counts().to_dict(),
        'diabetes_risk_percentage': (patients_with_risks_df['diabetes_risk'].sum() / len(patients_with_risks_df)) * 100,
        'cardiovascular_risk_percentage': (patients_with_risks_df['cardiovascular_risk'].sum() / len(patients_with_risks_df)) * 100
    }
    
    return patients_with_risks_df, risk_summary

if __name__ == "__main__":
    # Demo: Score patient risks and display results
    patients_with_risks, risk_summary = score_patient_risks()
    
    print(f"Analyzed risks for {risk_summary['total_patients']} patients")
    
    # Display risk summary
    print("\nRisk Summary:")
    print(f"Diabetes Risk Count: {risk_summary['diabetes_risk_count']} ({risk_summary['diabetes_risk_percentage']:.1f}%)")
    print(f"Cardiovascular Risk Count: {risk_summary['cardiovascular_risk_count']} ({risk_summary['cardiovascular_risk_percentage']:.1f}%)")
    print(f"Risk Category Counts: {risk_summary['risk_category_counts']}")
    
    # Preview high-risk patients
    high_risk_patients = patients_with_risks[patients_with_risks['risk_category'] == 'High Risk']
    if len(high_risk_patients) > 0:
        print("\nHigh Risk Patients Preview:")
        print(high_risk_patients[['patient_id', 'full_name', 'age', 'risk_category', 'risk_reasons']].head())
    else:
        print("\nNo high-risk patients identified.") 