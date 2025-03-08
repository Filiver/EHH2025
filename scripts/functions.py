from pathlib import Path
import pandas as pd


def resave_data():
    LABS.to_csv(DATA_DIR / 'labs.csv', index=False)
    MEDS.to_csv(DATA_DIR / 'medications.csv', index=False)
    REPORTS.to_csv(DATA_DIR / 'reports.csv', index=False)
    TRANSPLATATIONS.to_csv(DATA_DIR / 'transplantations.csv', index=False)
    PATIENTS.to_csv(DATA_DIR / 'patients.csv', index=False)


DATA_DIR = Path("../data")
LABS = pd.read_csv(DATA_DIR / 'labs.csv')
MEDS = pd.read_csv(DATA_DIR / 'medications.csv')
REPORTS = pd.read_csv(DATA_DIR / 'reports.csv')
TRANSPLATATIONS = pd.read_csv(DATA_DIR / 'transplantations.csv')
PATIENTS = pd.read_csv(DATA_DIR / 'patients.csv')
DIAGNOSES = pd.read_csv(DATA_DIR / 'diagnoses.csv')
ALL_TABLES = [LABS, MEDS, REPORTS, TRANSPLATATIONS, PATIENTS, DIAGNOSES]
TABLE_NAMES = ['labs',
               'medications',
               'reports',
               'transplantations',
               'patients', "diagnoses"]


def resave_data():
    LABS.to_csv(DATA_DIR / 'labs.csv', index=False)
    MEDS.to_csv(DATA_DIR / 'medications.csv', index=False)
    REPORTS.to_csv(DATA_DIR / 'reports.csv', index=False)
    TRANSPLATATIONS.to_csv(DATA_DIR / 'transplantations.csv', index=False)
    PATIENTS.to_csv(DATA_DIR / 'patients.csv', index=False)


def show_all_data():
    # DIAGNOSES = pd.read_csv(DATA_DIR/'diagnoses.csv')

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    # print("DIAGNOSES")
    # display(DIAGNOSES.head())
    for table_name, table in zip(TABLE_NAMES, ALL_TABLES):
        print(table_name.upper())
        display(table.head())
