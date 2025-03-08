from pathlib import Path
import pandas as pd
from typing import TypedDict
from ipykernel import *


class PatientData(TypedDict):
    labs: pd.DataFrame
    reports: pd.DataFrame
    transplantations: pd.DataFrame
    patients: pd.DataFrame
    diagnoses: pd.DataFrame


DATA_DIR = Path("../../data")
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


def get_patient_data(patient_id):
    p_labs = LABS[LABS['Patient'] == patient_id]
    p_reports = REPORTS[REPORTS['Patient'] == patient_id]
    # p_meds = MEDS[MEDS['Patient'] == patient_id]
    p_reports = REPORTS[REPORTS['Patient'] == patient_id]
    p_transplantations = TRANSPLATATIONS[TRANSPLATATIONS['Patient'] == patient_id]
    p_patients = PATIENTS[PATIENTS['Patient'] == patient_id]
    p_diagnoses = DIAGNOSES[DIAGNOSES['Patient'] == patient_id]
    ret: PatientData = {
        'labs': p_labs,
        'reports': p_reports,
        # 'meds': p_meds,
        'transplantations': p_transplantations,
        'patients': p_patients,
        'diagnoses': p_diagnoses

    }
    return ret


class Patient:
    def __init__(self, patient_data):
        self.personal = patient_data['patients']
        self.labs = patient_data['labs'].sort_values('EntryDate')
        self.reports = patient_data['reports'].sort_values('EntryDate')
        self.transplantations = patient_data['transplantations'].sort_values(
            'EntryDate')

    @property
    def ckd_date(self):
        ckd_date = None
        for _, row in self.reports.iterrows():
            print(row)
            if row['CKD_mild'] == 1:
                ckd_date = row['EntryDate']
                break

    def get_uacr(self):
        uacr = self.labs[self.labs['Analyte'] == 'UACR']
        return uacr

    def get_CKD_EPI(self):
        ckd_epi = self.labs[self.labs['Analyte'] == 'CKD-EPI']
        return ckd_epi
