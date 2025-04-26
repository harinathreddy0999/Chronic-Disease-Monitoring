#!/usr/bin/env python3
"""
Process patient data to extract relevant information and demographic statistics.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Import from our local module
import scripts.load_data as load_data

def calculate_age(birthdate):
    """
    Calculate age based on birthdate.
    
    Args:
        birthdate (str): Birthdate in format "YYYY-MM-DD"
        
    Returns:
        int: Age in years, or None if birthdate is invalid
    """
    if not birthdate:
        return None
    
    try:
        birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def enrich_patient_data(patients_df):
    """
    Add derived fields and enrich patient data.
    
    Args:
        patients_df (pandas.DataFrame): DataFrame with patient data
        
    Returns:
        pandas.DataFrame: Enriched patient data
    """
    # Make a copy to avoid modifying original
    df = patients_df.copy()
    
    # Calculate age from birthdate
    df['age'] = df['birthdate'].apply(calculate_age)
    
    # Create age groups
    bins = [0, 18, 35, 50, 65, 120]
    labels = ['0-18', '19-35', '36-50', '51-65', '65+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    
    return df

def get_patient_demographics(patients_df):
    """
    Generate demographic statistics from patient data.
    
    Args:
        patients_df (pandas.DataFrame): DataFrame with patient data
        
    Returns:
        dict: Dictionary with demographic statistics
    """
    demographics = {}
    
    # Gender distribution
    demographics['gender_distribution'] = patients_df['gender'].value_counts().to_dict()
    
    # Age statistics
    demographics['age_mean'] = patients_df['age'].mean()
    demographics['age_median'] = patients_df['age'].median()
    demographics['age_min'] = patients_df['age'].min()
    demographics['age_max'] = patients_df['age'].max()
    
    # Age group distribution
    demographics['age_group_distribution'] = patients_df['age_group'].value_counts().to_dict()
    
    # State distribution
    demographics['state_distribution'] = patients_df['state'].value_counts().to_dict()
    
    return demographics

def process_patients(file_path=None):
    """
    Main function to process patient data.
    
    Args:
        file_path (str, optional): Path to the FHIR JSON file.
            If None, use default path.
            
    Returns:
        tuple: (enriched_patients_df, demographics)
    """
    # Load data
    patients_df, _, _, _ = load_data.load_and_normalize_data(file_path)
    
    # Enrich patient data
    enriched_df = enrich_patient_data(patients_df)
    
    # Get demographics
    demographics = get_patient_demographics(enriched_df)
    
    return enriched_df, demographics

if __name__ == "__main__":
    # Demo: Process and display patient data
    patients_df, demographics = process_patients()
    
    print(f"Processed {len(patients_df)} patients")
    
    # Preview enriched data
    print("\nEnriched Patient Data Preview:")
    print(patients_df[['patient_id', 'full_name', 'gender', 'birthdate', 'age', 'age_group']].head())
    
    # Display demographics
    print("\nDemographic Statistics:")
    print(f"Gender Distribution: {demographics['gender_distribution']}")
    print(f"Age Range: {demographics['age_min']} - {demographics['age_max']} years")
    print(f"Mean Age: {demographics['age_mean']:.1f} years")
    print(f"Age Group Distribution: {demographics['age_group_distribution']}") 