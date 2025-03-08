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
        try:
            self.egfr_date, self.egfr, self.egfr_unit, self.egfr_note = self.get_egfr()
        except MeasurementError as e:
            self.egfr, self.egfr_date, self.egfr_unit, self.egfr_note = None, None, None, None
            print(e)
        try:
            self.uacr, self.uacr_date, self.uacr_unit, self.uacr_note = self.get_uacr()
        except MeasurementError as e:
            self.uacr, self.uacr_date, self.uacr_unit, self.uacr_note = None, None, None, None
            print(e)
        self.gfr_category = self.calculate_gfr_category()
        self.uacr_category = self.calculate_albuminua_category()
        self.ckd_stage = self.calculate_ckd_stage()

    def calculate_gfr_category(self):
        if self.egfr is not None:
            if self.egfr >= 90:
                return 1
            elif self.egfr >= 60:
                return 2
            elif self.egfr >= 45:
                return 3
            elif self.egfr >= 30:
                return 4
            elif self.egfr >= 15:
                return 5
            return 6
        else:
            return None

    def calculate_albuminua_category(self):
        if self.uacr is not None:
            if self.uacr < 3:
                return 1
            elif self.uacr < 30:
                return 2
            return 3
        else:
            return None

    def calculate_ckd_stage(self):
        if self.uacr_category is not None and self.gfr_category is not None:
            if self.gfr_category > 4:
                return 3
            elif self.gfr_category == 4:
                if self.uacr_category == 1:
                    return 2
                return 3
            elif self.gfr_category == 3:
                if self.uacr_category == 1:
                    return 1
                elif self.uacr_category == 2:
                    return 2
                return 3
            elif self.gfr_category < 3:
                if self.uacr_category == 1:
                    return 0
                elif self.uacr_category == 2:
                    return 1
                return 2
        return None





    def get_uacr(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
                    FROM labs
                    WHERE Patient = ? AND analyte = 'UACR' 
                    ORDER BY EntryDate DESC;
                """, (self.patient_id,))
        row = cur.fetchone()
        if row is None:
            raise MeasurementError("Pacient nemá provedené žádné měření UACR")
        if row[2] is None:
            raise MeasurementError(f"Poslední měření UACR je neúplné {row[3]}")
        if row[4] != 'g/mol':
            raise MeasurementError("Jednotka UACR není g/mol")
        return row[0], row[2], "g/mol", row[3]

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
    patient = Patient(9150)
    print(patient.__dict__)