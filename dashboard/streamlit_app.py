#!/usr/bin/env python3
"""
Streamlit dashboard for viewing clinical risk reports.
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Add the project root directory to the Python path
# Get the absolute path of the project root directory (parent of the current script's directory)
project_root = Path(__file__).resolve().parent.parent
# Add the project root to the sys.path if it's not already there, prioritizing it
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the modules directly using package notation
import scripts.load_data as load_data
import scripts.process_patients as process_patients
import scripts.risk_scoring as risk_scoring
import scripts.generate_report as generate_report

# Set page configuration
st.set_page_config(
    page_title="Clinical Risk Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define paths (using project_root for consistency)
DATA_PATH = project_root / 'data' / 'fhir_sample_data.json'
CSV_REPORT_PATH = project_root / 'outputs' / 'high_risk_report.csv'
JSON_REPORT_PATH = project_root / 'outputs' / 'high_risk_report.json'

@st.cache_data
def load_report_data():
    """Load and return report data."""
    # Check if reports exist, if not generate them
    if not CSV_REPORT_PATH.exists() or not JSON_REPORT_PATH.exists():
        st.info("Generating reports... This may take a moment.")
        # Ensure generate_reports uses the correct file path if needed
        report_info = generate_report.generate_reports(file_path=DATA_PATH)
        st.success("Reports generated!")
    
    # Load CSV report
    high_risk_df = pd.read_csv(CSV_REPORT_PATH)
    
    # Load JSON report for summary
    with open(JSON_REPORT_PATH, 'r') as f:
        report_json = json.load(f)
    
    return high_risk_df, report_json

def main():
    """Main Streamlit application."""
    # Header
    st.title("🏥 Clinical Risk Dashboard for Chronic Disease Monitoring")
    st.markdown("---")
    
    # Load data
    high_risk_df, report_json = load_report_data()
    
    # Sidebar
    st.sidebar.title("Filters")
    
    # Risk category filter
    risk_categories = ['All'] + sorted(high_risk_df['risk_category'].unique().tolist())
    selected_risk = st.sidebar.selectbox("Risk Category", risk_categories)
    
    # Age range filter
    min_age = int(high_risk_df['age'].min())
    max_age = int(high_risk_df['age'].max())
    age_range = st.sidebar.slider("Age Range", min_age, max_age, (min_age, max_age))
    
    # Apply filters
    filtered_df = high_risk_df.copy()
    if selected_risk != 'All':
        filtered_df = filtered_df[filtered_df['risk_category'] == selected_risk]
    filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]
    
    # Main dashboard
    col1, col2 = st.columns([1, 2])
    
    # Summary metrics
    with col1:
        st.subheader("Risk Summary")
        
        summary = report_json['summary']
        
        # Display metrics
        total_patients = summary['total_patients']
        diabetes_count = summary['diabetes_risk_count']
        diabetes_pct = summary['diabetes_risk_percentage']
        cardio_count = summary['cardiovascular_risk_count']
        cardio_pct = summary['cardiovascular_risk_percentage']
        
        st.metric("Total Patients", total_patients)
        st.metric("Diabetes Risk", f"{diabetes_count} ({diabetes_pct:.1f}%)")
        st.metric("Cardiovascular Risk", f"{cardio_count} ({cardio_pct:.1f}%)")
        
        # Risk categories
        st.subheader("Risk Categories")
        risk_data = pd.DataFrame({
            'Category': list(summary['risk_category_counts'].keys()),
            'Count': list(summary['risk_category_counts'].values())
        })
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(5, 3))
        colors = ['green', 'orange', 'red'] # Assuming Low, Moderate, High order
        # Ensure correct order for colors if needed
        ordered_categories = ['Low Risk', 'Moderate Risk', 'High Risk'] 
        risk_data = risk_data.set_index('Category').reindex(ordered_categories).reset_index()
        risk_data = risk_data.dropna() # Remove categories not present
        
        bars = ax.barh(risk_data['Category'], risk_data['Count'], color=colors[:len(risk_data)])
        ax.set_title('Patient Risk Categories')
        ax.set_xlabel('Number of Patients')
        
        # Add counts as labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            label_x_pos = width + 0.5
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                    va='center')
        
        st.pyplot(fig)
    
    # Patient data table
    with col2:
        st.subheader(f"High-Risk Patients ({len(filtered_df)} patients)")
        
        # Patient detail expander
        if not filtered_df.empty:
            # Create display columns
            display_df = filtered_df[[
                'patient_id', 'full_name', 'age', 'gender', 
                'risk_category', 'hba1c_value', 'cholesterol_value', 'risk_reasons'
            ]].copy()
            
            # Rename columns for display
            display_df.columns = [
                'ID', 'Name', 'Age', 'Gender', 'Risk Category', 
                'HbA1c', 'Cholesterol', 'Risk Reasons'
            ]
            
            # Display the table
            st.dataframe(display_df, height=400)
            
            # Select a patient for detailed view
            selected_patient_idx = st.selectbox(
                "Select a patient for detailed view:",
                options=range(len(filtered_df)),
                format_func=lambda i: f"{filtered_df.iloc[i]['full_name']} (ID: {filtered_df.iloc[i]['patient_id']})"
            )
            
            if selected_patient_idx is not None:
                patient = filtered_df.iloc[selected_patient_idx]
                
                # Patient details expander
                with st.expander(f"Details for {patient['full_name']}", expanded=True):
                    # Create two columns
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Patient Information**")
                        st.write(f"**ID:** {patient['patient_id']}")
                        st.write(f"**Name:** {patient['full_name']}")
                        st.write(f"**Age:** {patient['age']}")
                        st.write(f"**Gender:** {patient['gender']}")
                    
                    with detail_col2:
                        st.markdown("**Risk Assessment**")
                        st.write(f"**Risk Category:** {patient['risk_category']}")
                        st.write(f"**Risk Score:** {patient['risk_score']}")
                        st.write(f"**Risk Reasons:** {patient['risk_reasons']}")
                    
                    # Lab values
                    st.markdown("**Lab Values**")
                    
                    # Create a mini chart for lab values
                    fig_labs, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))
                    
                    # HbA1c
                    hba1c_val = patient['hba1c_value']
                    ax1.bar(['HbA1c'], [hba1c_val] if pd.notna(hba1c_val) else [0], color='skyblue')
                    ax1.axhline(y=risk_scoring.DIABETES_HBA1C_THRESHOLD, color='red', linestyle='--')
                    ax1.text(0, risk_scoring.DIABETES_HBA1C_THRESHOLD + 0.1, 'Threshold (6.5)', color='red')
                    ax1.set_ylim(0, max(10, hba1c_val + 1 if pd.notna(hba1c_val) else 10))
                    ax1.set_title('HbA1c Value')
                    
                    # Cholesterol
                    chol_val = patient['cholesterol_value']
                    ax2.bar(['Cholesterol'], [chol_val] if pd.notna(chol_val) else [0], color='lightgreen')
                    ax2.axhline(y=risk_scoring.CARDIOVASCULAR_CHOLESTEROL_THRESHOLD, color='red', linestyle='--')
                    ax2.text(0, risk_scoring.CARDIOVASCULAR_CHOLESTEROL_THRESHOLD + 5, 'Threshold (240)', color='red')
                    ax2.set_ylim(0, max(250, chol_val + 10 if pd.notna(chol_val) else 250))
                    ax2.set_title('Cholesterol Value')
                    
                    plt.tight_layout()
                    st.pyplot(fig_labs)
        else:
            st.info("No patients match the selected filters.")
    
    # Visualizations section
    st.markdown("---")
    st.subheader("Risk Visualizations")
    
    # Get all patients with risk data for visualizations
    patients_with_risks_df, _ = risk_scoring.score_patient_risks(file_path=DATA_PATH)
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Age vs. Risk", "Lab Values Distribution", "Medication Analysis"])
    
    with tab1:
        # Age vs. Risk Score scatter plot
        fig_scatter, ax_scatter = plt.subplots(figsize=(10, 6))
        scatter = ax_scatter.scatter(
            patients_with_risks_df['age'],
            patients_with_risks_df['risk_score'],
            c=patients_with_risks_df['risk_score'],
            cmap='YlOrRd',
            alpha=0.7,
            s=100
        )
        
        plt.colorbar(scatter, label='Risk Score')
        ax_scatter.set_title('Age vs. Risk Score')
        ax_scatter.set_xlabel('Age')
        ax_scatter.set_ylabel('Risk Score')
        ax_scatter.grid(True, alpha=0.3)
        
        st.pyplot(fig_scatter)
    
    with tab2:
        # Create columns for HbA1c and Cholesterol distributions
        dist_col1, dist_col2 = st.columns(2)
        
        with dist_col1:
            # HbA1c distribution
            fig_hba1c, ax_hba1c = plt.subplots(figsize=(8, 6))
            sns.histplot(patients_with_risks_df['hba1c_value'].dropna(), bins=15, kde=True, ax=ax_hba1c)
            ax_hba1c.axvline(x=risk_scoring.DIABETES_HBA1C_THRESHOLD, color='red', linestyle='--')
            ax_hba1c.text(risk_scoring.DIABETES_HBA1C_THRESHOLD + 0.1, ax_hba1c.get_ylim()[1] * 0.9, 'Threshold (6.5)', color='red')
            ax_hba1c.set_title('HbA1c Distribution')
            ax_hba1c.set_xlabel('HbA1c Value')
            ax_hba1c.set_ylabel('Count')
            st.pyplot(fig_hba1c)
        
        with dist_col2:
            # Cholesterol distribution
            fig_chol, ax_chol = plt.subplots(figsize=(8, 6))
            sns.histplot(patients_with_risks_df['cholesterol_value'].dropna(), bins=15, kde=True, ax=ax_chol)
            ax_chol.axvline(x=risk_scoring.CARDIOVASCULAR_CHOLESTEROL_THRESHOLD, color='red', linestyle='--')
            ax_chol.text(risk_scoring.CARDIOVASCULAR_CHOLESTEROL_THRESHOLD + 5, ax_chol.get_ylim()[1] * 0.9, 'Threshold (240)', color='red')
            ax_chol.set_title('Cholesterol Distribution')
            ax_chol.set_xlabel('Cholesterol Value')
            ax_chol.set_ylabel('Count')
            st.pyplot(fig_chol)
    
    with tab3:
        st.write("This tab will contain medication adherence analysis in a future update.")

    # Footer
    st.markdown("---")
    st.caption("© 2023 Clinical Risk Dashboard | Data is simulated for demonstration purposes.")

if __name__ == "__main__":
    main() 