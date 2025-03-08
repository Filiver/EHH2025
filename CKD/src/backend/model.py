import sqlite3
import numpy as np
import os
import datetime
from constants import *

class MeasurementError(ValueError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.sex, self.dob, self.age = self.get_patient_info()
        self.egfr = None
        self.egfr_date = None
        self.egfr_unit = None
        self.egfr_note = None

    def get_patient_info(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT DateOfBirth, Sex
                    FROM patients
                    WHERE Patient = ?
            """, (self.patient_id,))
        patient_data = cur.fetchone()
        if patient_data is None:
            raise MeasurementError("Nelze spočítat bez dat o pacientovi")
        dob = datetime.datetime.strptime(patient_data[0], '%Y-%m-%d')
        return int(patient_data[1] == "F"), dob, datetime.datetime.now().year - dob.year


    def get_egfr(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        # print(os.listdir(f"{os.curdir}/../../data/"))
        cur.execute("""
            SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
            FROM labs
            WHERE Patient = ? AND analyte = 'CKD-EPI' 
            ORDER BY EntryDate DESC;
        """, (self.patient_id,))
        row = cur.fetchone()

        if row is not None:
            if row[2] is None:
                raise MeasurementError(f"Poslední měření eGFR je neúplné {row[3]}")
            if row[4] != "ml/s/1,73 m2":
                raise MeasurementError("Jednotka eGFR není ml/s/1,73 m2")
            return row[0], row[2] * 60, "ml/min/1,73 m2", row[3]
        else:
            return self.get_egfr_from_s_kreatinin()

    def get_egfr_from_s_kreatinin(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
                    FROM labs
                    WHERE Patient = ? AND analyte = 's_kreatinin' 
                    ORDER BY EntryDate DESC;
                """, (self.patient_id,))
        row = cur.fetchone()
        if row is None:
            raise MeasurementError("Žádná laboratorní data")

        if row[2] is None:
            raise MeasurementError(f"Poslední měření kreatininu je neúplné {row[3]}")
        if row[4] != 'µmol/l':
            raise MeasurementError("Jednotka kreatininu není µmol/l")
        s_kreatinin = umol_l_to_mg_dl(row[2])
        if self.sex == 'M':
            sex = 0
        else:
            sex = 1

        value = round(EGFR_COEF[sex][0] * min(s_kreatinin / EGFR_BOUNDARY[sex], 1) ** EGFR_COEF[sex][1]
                      * max(s_kreatinin / EGFR_BOUNDARY[sex], 1) ** (EGFR_COEF[sex][2]) *
                      (0.993 ** self.age), 1)

        return row[0], value, "ml/min/1,73 m2", row[3]

DB = "../../data/CKD_train.db"

def mg_dl_to_umol_l(mg_dl):
    return mg_dl / KREATININ_MOLAR_MASS * 10000

def umol_l_to_mg_dl(umol_l):
    return umol_l * KREATININ_MOLAR_MASS / 10000


def calculate_egfr(patient_id):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        """
                SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
                FROM labs
                WHERE Patient = ? AND analyte = 's_kreatinin' 
                ORDER BY EntryDate DESC;
            """, (patient_id,))
    row = cur.fetchone()
    if row is None:
        raise MeasurementError("Žádná laboratorní data")

    cur.execute(
        """
                SELECT DateOfBirth, Sex
                FROM patients
                WHERE Patient = ?
        """, (patient_id,))
    patient_data = cur.fetchone()
    if patient_data is None:
        raise MeasurementError("Nelze spočítat bez dat o pacientovi")
    dob = datetime.datetime.strptime(patient_data[0], '%Y-%m-%d')
    sex = patient_data[1]
    if row[2] is None:
        raise MeasurementError(f"Poslední měření kreatininu je neúplné {row[3]}")
    if row[4] != 'µmol/l':
        raise MeasurementError("Jednotka kreatininu není µmol/l")
    s_kreatinin = umol_l_to_mg_dl(row[2])
    if sex == 'M':
        sex = 0
    else:
        sex = 1

    value = round(EGFR_COEF[sex][0] * min(s_kreatinin / EGFR_BOUNDARY[sex], 1) ** EGFR_COEF[sex][1]
             * max(s_kreatinin / EGFR_BOUNDARY[sex], 1) ** (EGFR_COEF[sex][2]) *
             (0.993 ** (datetime.datetime.now().year - dob.year)), 1)

    return row[0], value, "ml/min/1,73 m2", row[3]


if __name__ == '__main__':
    print(calculate_egfr(9150), get_egfr(9150))