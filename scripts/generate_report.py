#!/usr/bin/env python3
"""
Generate reports of high-risk patients and insights.
"""
import pandas as pd
import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Import from our local modules
import scripts.load_data as load_data
import scripts.process_patients as process_patients
import scripts.risk_scoring as risk_scoring

# Custom JSON encoder to handle NumPy data types
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

def filter_high_risk_patients(patients_with_risks_df):
    """
    Filter for high-risk patients based on risk category.
    
    Args:
        patients_with_risks_df (pandas.DataFrame): DataFrame with patient risk data
        
    Returns:
        pandas.DataFrame: DataFrame with only high-risk patients
    """
    # Filter for patients with at least one risk factor
    high_risk_df = patients_with_risks_df[patients_with_risks_df['risk_score'] > 0].copy()
    
    # Sort by risk score (descending)
    high_risk_df = high_risk_df.sort_values('risk_score', ascending=False)
    
    return high_risk_df

def generate_csv_report(high_risk_df, output_path):
    """
    Generate a CSV report of high-risk patients.
    
    Args:
        high_risk_df (pandas.DataFrame): DataFrame with high-risk patient data
        output_path (str): Path to save the CSV report
        
    Returns:
        str: Path to the generated CSV file
    """
    # Select relevant columns for the report
    report_columns = [
        'patient_id', 'full_name', 'gender', 'age', 'risk_category', 
        'risk_score', 'risk_reasons', 'hba1c_value', 'cholesterol_value'
    ]
    
    # Create the report DataFrame
    report_df = high_risk_df[report_columns].copy()
    
    # Save to CSV
    report_df.to_csv(output_path, index=False)
    
    return output_path

def generate_json_report(high_risk_df, risk_summary, output_path):
    """
    Generate a JSON report of high-risk patients with summary statistics.
    
    Args:
        high_risk_df (pandas.DataFrame): DataFrame with high-risk patient data
        risk_summary (dict): Dictionary with risk summary statistics
        output_path (str): Path to save the JSON report
        
    Returns:
        str: Path to the generated JSON file
    """
    # Create report structure
    report = {
        'report_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
        'summary': risk_summary,
        'high_risk_patients': high_risk_df.to_dict(orient='records')
    }
    
    # Save to JSON using the custom encoder
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, cls=NpEncoder)
    
    return output_path

def generate_visualizations(patients_with_risks_df, output_dir):
    """
    Generate visualizations of patient risk data.
    
    Args:
        patients_with_risks_df (pandas.DataFrame): DataFrame with patient risk data
        output_dir (str): Directory to save the visualizations
        
    Returns:
        list: Paths to the generated visualization files
    """
    output_paths = []
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Set style
    sns.set(style="whitegrid")
    
    # 1. Risk Category Distribution
    plt.figure(figsize=(10, 6))
    risk_counts = patients_with_risks_df['risk_category'].value_counts()
    ax = sns.barplot(x=risk_counts.index, y=risk_counts.values)
    plt.title('Distribution of Risk Categories')
    plt.xlabel('Risk Category')
    plt.ylabel('Number of Patients')
    for i, v in enumerate(risk_counts.values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    risk_dist_path = output_dir / 'risk_category_distribution.png'
    plt.tight_layout()
    plt.savefig(risk_dist_path)
    plt.close()
    output_paths.append(str(risk_dist_path))
    
    # 2. Age vs. HbA1c with risk highlighting
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        patients_with_risks_df['age'], 
        patients_with_risks_df['hba1c_value'],
        c=patients_with_risks_df['risk_score'],
        cmap='YlOrRd',
        alpha=0.7
    )
    plt.colorbar(scatter, label='Risk Score')
    plt.axhline(y=risk_scoring.DIABETES_HBA1C_THRESHOLD, color='red', linestyle='--', alpha=0.7)
    plt.title('Age vs. HbA1c with Risk Highlighting')
    plt.xlabel('Age')
    plt.ylabel('HbA1c Value')
    plt.grid(True, alpha=0.3)
    
    age_hba1c_path = output_dir / 'age_vs_hba1c.png'
    plt.tight_layout()
    plt.savefig(age_hba1c_path)
    plt.close()
    output_paths.append(str(age_hba1c_path))
    
    # 3. Age vs. Cholesterol with risk highlighting
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        patients_with_risks_df['age'], 
        patients_with_risks_df['cholesterol_value'],
        c=patients_with_risks_df['risk_score'],
        cmap='YlOrRd',
        alpha=0.7
    )
    plt.colorbar(scatter, label='Risk Score')
    plt.axhline(y=risk_scoring.CARDIOVASCULAR_CHOLESTEROL_THRESHOLD, color='red', linestyle='--', alpha=0.7)
    plt.title('Age vs. Cholesterol with Risk Highlighting')
    plt.xlabel('Age')
    plt.ylabel('Cholesterol Value')
    plt.grid(True, alpha=0.3)
    
    age_chol_path = output_dir / 'age_vs_cholesterol.png'
    plt.tight_layout()
    plt.savefig(age_chol_path)
    plt.close()
    output_paths.append(str(age_chol_path))
    
    return output_paths

def generate_reports(file_path=None, output_dir=None):
    """
    Main function to generate reports of high-risk patients.
    
    Args:
        file_path (str, optional): Path to the FHIR JSON file.
            If None, use default path.
        output_dir (str, optional): Directory to save the reports.
            If None, use default path.
            
    Returns:
        dict: Dictionary with paths to generated reports and statistics
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'outputs'
    else:
        output_dir = Path(output_dir)
    
    # Make sure output directory exists
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Score patient risks
    patients_with_risks_df, risk_summary = risk_scoring.score_patient_risks(file_path)
    
    # Filter for high-risk patients
    high_risk_df = filter_high_risk_patients(patients_with_risks_df)
    
    # Generate CSV report
    csv_path = output_dir / 'high_risk_report.csv'
    csv_report_path = generate_csv_report(high_risk_df, csv_path)
    
    # Generate JSON report
    json_path = output_dir / 'high_risk_report.json'
    json_report_path = generate_json_report(high_risk_df, risk_summary, json_path)
    
    # Generate visualizations
    viz_dir = output_dir / 'visualizations'
    viz_paths = generate_visualizations(patients_with_risks_df, viz_dir)
    
    # Return report information
    report_info = {
        'csv_report_path': str(csv_report_path),
        'json_report_path': str(json_report_path),
        'visualization_paths': viz_paths,
        'high_risk_count': len(high_risk_df),
        'total_patients': risk_summary['total_patients'],
        'risk_summary': risk_summary
    }
    
    return report_info

if __name__ == "__main__":
    # Generate reports
    report_info = generate_reports()
    
    print(f"Generated reports for {report_info['high_risk_count']} high-risk patients out of {report_info['total_patients']} total patients")
    print(f"CSV Report: {report_info['csv_report_path']}")
    print(f"JSON Report: {report_info['json_report_path']}")
    print(f"Visualizations: {report_info['visualization_paths']}")
    
    print("\nRisk Summary:")
    print(f"Diabetes Risk: {report_info['risk_summary']['diabetes_risk_count']} patients ({report_info['risk_summary']['diabetes_risk_percentage']:.1f}%)")
    print(f"Cardiovascular Risk: {report_info['risk_summary']['cardiovascular_risk_count']} patients ({report_info['risk_summary']['cardiovascular_risk_percentage']:.1f}%)")
    print(f"Risk Categories: {report_info['risk_summary']['risk_category_counts']}") 