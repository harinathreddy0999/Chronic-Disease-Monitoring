#!/usr/bin/env python3
"""
Load FHIR data from JSON file and normalize into pandas DataFrames.
"""
import json
import pandas as pd
from pathlib import Path

def load_fhir_data(file_path):
    """
    Load FHIR data from JSON file.
    
    Args:
        file_path (str): Path to the FHIR JSON file
        
    Returns:
        dict: The FHIR data as a dictionary
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def normalize_patients(data):
    """
    Convert FHIR patients into pandas DataFrame.
    
    Args:
        data (dict): FHIR data containing patient resources
        
    Returns:
        pandas.DataFrame: Normalized patient data
    """
    patients = []
    
    for patient in data.get('patients', []):
        # Extract basic information
        patient_id = patient.get('id', '')
        
        # Extract name
        name = patient.get('name', [{}])[0]
        family_name = name.get('family', '')
        given_names = name.get('given', [''])
        full_name = f"{' '.join(given_names)} {family_name}"
        
        # Extract gender and birthdate
        gender = patient.get('gender', '')
        birthdate = patient.get('birthDate', '')
        
        # Extract address
        address = patient.get('address', [{}])[0]
        city = address.get('city', '')
        state = address.get('state', '')
        postal_code = address.get('postalCode', '')
        
        # Create a dictionary for this patient
        patient_dict = {
            'patient_id': patient_id,
            'full_name': full_name,
            'family_name': family_name,
            'given_name': given_names[0] if given_names else '',
            'gender': gender,
            'birthdate': birthdate,
            'city': city,
            'state': state,
            'postal_code': postal_code
        }
        
        patients.append(patient_dict)
    
    return pd.DataFrame(patients)

def normalize_observations(data):
    """
    Convert FHIR observations into pandas DataFrame.
    
    Args:
        data (dict): FHIR data containing observation resources
        
    Returns:
        pandas.DataFrame: Normalized observation data
    """
    observations = []
    
    for obs in data.get('observations', []):
        # Extract basic information
        obs_id = obs.get('id', '')
        status = obs.get('status', '')
        code_text = obs.get('code', {}).get('text', '')
        
        # Extract value
        value_quantity = obs.get('valueQuantity', {})
        value = value_quantity.get('value', None)
        unit = value_quantity.get('unit', '')
        
        # Extract date and patient reference
        date = obs.get('effectiveDateTime', '')
        patient_ref = obs.get('subject', {}).get('reference', '')
        
        # Extract patient_id from reference (format: "Patient/patient-X")
        patient_id = patient_ref.split('/')[-1] if patient_ref else ''
        
        # Create a dictionary for this observation
        obs_dict = {
            'observation_id': obs_id,
            'status': status,
            'code': code_text,
            'value': value,
            'unit': unit,
            'date': date,
            'patient_id': patient_id
        }
        
        observations.append(obs_dict)
    
    return pd.DataFrame(observations)

def normalize_medications(data):
    """
    Convert FHIR medication requests into pandas DataFrame.
    
    Args:
        data (dict): FHIR data containing medication request resources
        
    Returns:
        pandas.DataFrame: Normalized medication data
    """
    medications = []
    
    for med in data.get('medications', []):
        # Extract basic information
        med_id = med.get('id', '')
        status = med.get('status', '')
        
        # Extract medication name
        med_name = med.get('medicationCodeableConcept', {}).get('text', '')
        
        # Extract patient reference and date
        patient_ref = med.get('subject', {}).get('reference', '')
        date = med.get('authoredOn', '')
        
        # Extract patient_id from reference (format: "Patient/patient-X")
        patient_id = patient_ref.split('/')[-1] if patient_ref else ''
        
        # Create a dictionary for this medication
        med_dict = {
            'medication_id': med_id,
            'status': status,
            'medication_name': med_name,
            'date': date,
            'patient_id': patient_id
        }
        
        medications.append(med_dict)
    
    return pd.DataFrame(medications)

def normalize_allergies(data):
    """
    Convert FHIR allergy intolerances into pandas DataFrame.
    
    Args:
        data (dict): FHIR data containing allergy intolerance resources
        
    Returns:
        pandas.DataFrame: Normalized allergy data
    """
    allergies = []
    
    for allergy in data.get('allergies', []):
        # Extract basic information
        allergy_id = allergy.get('id', '')
        status = allergy.get('clinicalStatus', {}).get('text', '')
        
        # Extract allergy code/name
        code_text = allergy.get('code', {}).get('text', '')
        
        # Extract reaction
        reactions = allergy.get('reaction', [{}])
        manifestation = reactions[0].get('manifestation', [{}])[0].get('text', '') if reactions else ''
        
        # Extract patient reference
        patient_ref = allergy.get('patient', {}).get('reference', '')
        
        # Extract patient_id from reference (format: "Patient/patient-X")
        patient_id = patient_ref.split('/')[-1] if patient_ref else ''
        
        # Create a dictionary for this allergy
        allergy_dict = {
            'allergy_id': allergy_id,
            'status': status,
            'allergy_type': code_text,
            'manifestation': manifestation,
            'patient_id': patient_id
        }
        
        allergies.append(allergy_dict)
    
    return pd.DataFrame(allergies)

def load_and_normalize_data(file_path=None):
    """
    Main function to load FHIR data and convert to DataFrames.
    
    Args:
        file_path (str, optional): Path to the FHIR JSON file.
            If None, use default path.
    
    Returns:
        tuple: (patients_df, observations_df, medications_df, allergies_df)
    """
    if file_path is None:
        # Default path relative to project root
        file_path = Path(__file__).parent.parent / 'data' / 'fhir_sample_data.json'
    
    # Load the data
    data = load_fhir_data(file_path)
    
    # Normalize into DataFrames
    patients_df = normalize_patients(data)
    observations_df = normalize_observations(data)
    medications_df = normalize_medications(data)
    allergies_df = normalize_allergies(data)
    
    return patients_df, observations_df, medications_df, allergies_df

if __name__ == "__main__":
    # Demo: Load and display data
    patients, observations, medications, allergies = load_and_normalize_data()
    
    print(f"Loaded {len(patients)} patients")
    print(f"Loaded {len(observations)} observations")
    print(f"Loaded {len(medications)} medications")
    print(f"Loaded {len(allergies)} allergies")
    
    # Preview patients
    print("\nPatient Preview:")
    print(patients.head()) 