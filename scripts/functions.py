from pathlib import Path
import pandas as pd

DATA_DIR = Path("../data")
LABS = pd.read_csv(DATA_DIR / 'labs.csv')
MEDS = pd.read_csv(DATA_DIR / 'medications.csv')
REPORTS = pd.read_csv(DATA_DIR / 'reports.csv')
TRANSPLATATIONS = pd.read_csv(DATA_DIR / 'transplantations.csv')


def resave_data():
    LABS.to_csv(DATA_DIR / 'labs.csv', index=False)
    MEDS.to_csv(DATA_DIR / 'medications.csv', index=False)
    REPORTS.to_csv(DATA_DIR / 'reports.csv', index=False)
    TRANSPLATATIONS.to_csv(DATA_DIR / 'transplantations.csv', index=False)


def show_all_data():
    # DIAGNOSES = pd.read_csv(DATA_DIR/'diagnoses.csv')

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    # print("DIAGNOSES")
    # display(DIAGNOSES.head())
    print("LABS")
    display(LABS.head())
    display("MEDS")
    display(MEDS.head())
    display("REPORTS")
    display(REPORTS.head())
    print("TRANSPLATATIONS")
    display(TRANSPLATATIONS.head())
