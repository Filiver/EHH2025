import pandas as pd
import datetime
import numpy as np
from pathlib import Path
from constants import *

# Load all data at once

DATA_DIR = Path("./CKD/data/")
print(DATA_DIR.resolve())
DB_PATH = DATA_DIR / "CKD_train.db"

def load_all_data():
    """Load all tables from database into pandas DataFrames"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    
    labs = pd.read_sql("SELECT * FROM labs", conn)
    patients = pd.read_sql("SELECT * FROM patients", conn)
    reports = pd.read_sql("SELECT * FROM reports", conn)
    transplantations = pd.read_sql("SELECT * FROM transplantations", conn)
    
    conn.close()
    return labs, patients, reports, transplantations

def process_all_patients(date=None, period=365):
    """Process all patients data at once using pandas operations"""
    date = date if date is not None else datetime.date.today()
    labs, patients, reports, transplantations = load_all_data()
    
    # Convert date strings to datetime objects
    labs['EntryDate'] = pd.to_datetime(labs['EntryDate'])
    reports['EntryDate'] = pd.to_datetime(reports['EntryDate'])
    transplantations['EntryDate'] = pd.to_datetime(transplantations['EntryDate'])
    patients['DateOfBirth'] = pd.to_datetime(patients['DateOfBirth'])
    
    # Filter by date
    labs = labs[labs['EntryDate'] <= date]
    
    # Calculate patient info (age, sex)
    patients['Sex_Binary'] = (patients['Sex'] == 'F').astype(int)
    patients['Age'] = ((date - patients['DateOfBirth']).dt.days / 365.25).astype(int)
    
    # Get latest egfr values for all patients
    egfr_data = get_latest_lab_values(labs, 'CKD-EPI', date, period)
    
    # Process other lab values similarly
    # ...
    
    # Create a results dataframe with all needed features
    results = patients[['Patient', 'Sex_Binary', 'Age']].copy()
    
    # Add all the calculated features
    # ...
    
    return results

def get_latest_lab_values(labs, analyte, date, period):
    """Get the latest lab values for a specific analyte for all patients"""
    # Filter labs for the specific analyte
    analyte_labs = labs[labs['analyte'] == analyte].copy()
    
    # Group by patient and get the latest entry
    latest = analyte_labs.sort_values('EntryDate', ascending=False).groupby('Patient').first()
    
    # Calculate average over period
    min_date = date - datetime.timedelta(days=period)
    period_labs = analyte_labs[analyte_labs['EntryDate'] >= min_date]
    avg_values = period_labs.groupby('Patient')['ValueNumber'].mean()
    
    return latest.merge(avg_values.to_frame('average_value'), left_index=True, right_index=True, how='left')

if __name__ == '__main__':
    results = process_all_patients()
    print(results.head())
    print(results.describe())
    print(results.info())
    print(results.isnull().sum())
