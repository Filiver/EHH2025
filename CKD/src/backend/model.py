import sqlite3
import numpy as np
import os
import datetime

from numpy.ma.extras import average

from constants import *

class MeasurementError(ValueError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Alert:
    def __init__(self, message, source, severity = 3):
        """
        :param message: Text of the alert
        :param severity: 1 - low, 5 - high
        """
        self.message = message
        self.severity = severity
        self.source = source

    def __str__(self):
        return f"{self.severity}-{self.source}: {self.message}"

    def __repr__(self):
        return f"{self.severity}-{self.source}: {self.message}"


class Patient:
    def __init__(self, patient_id, date=None, period=datetime.timedelta(days=365)):
        self.patient_id = int(patient_id)
        self.date = date if date is not None else datetime.date.today()
        self.period = period
        self.sex, self.dob, self.age = self.get_patient_info()

        self.egfr_date, self.egfr, self.egfr_unit, self.egfr_note, self.average_egfr, self.all_egfr, self.dates_egfr = self.get_egfr()
        self.uacr_date, self.uacr, self.uacr_unit, self.uacr_note, self.average_uacr, self.all_uacr, self.dates_uacr = self.get_lab("UACR")
        self.pu_date, self.pu, self.pu_unit, self.pu_note, self.average_pu, self.all_pu, self.dates_pu = self.get_lab("PU")
        self.upcr_date, self.upcr, self.upcr_unit, self.upcr_note, self.average_upcr, self.all_upcr, self.dates_upcr = self.get_lab("UPCR")
        self.s_kreatinin_date, self.s_kreatinin, self.s_kreatinin_unit, self.s_kreatinin_note, self.average_s_kreatinin, self.all_s_kreatinin, self.dates_s_kreatinin = self.get_lab("s_kreatinin")

        self.transplants = self.get_transplants()
        self.diagnoses = self.get_diagnoses()

        self.gfr_category = self.calculate_gfr_category()
        self.uacr_category = self.calculate_albuminua_category()
        self.ckd_stage = self.calculate_ckd_stage()
        self.last_nefrology_visit, self.in_nefrology_care = self.is_in_nefrology_care()
        self.alerts = self.generate_alerts()


    def generate_alerts(self):
        alerts = []
        if self.ckd_stage == 3 and (self.date - self.last_nefrology_visit).days >= LAST_NEFROLOGY_VISIT_SILENCER:
           alerts.append(Alert("Velmi vysoké riziko CKD - doporučení k dalšímu vyšetření", "KDIGO", 5))
        elif self.ckd_stage == 2 and (self.date - self.last_nefrology_visit).days >= LAST_NEFROLOGY_VISIT_SILENCER:
            alerts.append(Alert("Vysoké riziko CKD - doporučení k dalšímu vyšetření", "KDIGO", 4))
        elif self.ckd_stage == 1 and (self.date - self.last_nefrology_visit).days >= LAST_NEFROLOGY_VISIT_SILENCER:
            alerts.append(Alert("Střední riziko CKD - doporučení k dalšímu vyšetření", "KDIGO", 2))
        elif self.gfr_category is not None and 4 > self.gfr_category > 1:
            alerts.append(Alert("Riziko CKD - doporučení odběrů UACR", "eGFR", 1 if self.gfr_category == 2 else 3))
        elif self.gfr_category is not None and self.gfr_category > 4 and (self.date - self.last_nefrology_visit).days >= LAST_NEFROLOGY_VISIT_SILENCER:
            alerts.append(Alert("Velmi vysoké riziko CKD - doporučení odběrů UACR a dalšího vyšetření", "eGFR", 5))
        elif self.gfr_category is not None and self.gfr_category > 4:
            alerts.append(Alert("Velmi vysoké riziko CKD - doporučení odběrů UACR", "eGFR", 4))
        elif self.uacr_category == 3 and (self.date - self.last_nefrology_visit).days >= LAST_NEFROLOGY_VISIT_SILENCER:
            alerts.append(Alert("Vysoké až velmi vysoké riziko CKD - doporučení odběrů eGFR a doporučení k dalšímu vyšetření", "UACR", 5))
        elif self.uacr_category == 3:
            alerts.append(Alert("Vysoké až velmi vysoké riziko CKD - doporučení odběrů eGFR", "UACR", 4))
        elif self.uacr_category == 2:
            alerts.append(Alert("Střední riziko CKD - doporučení odběrů eGFR", "UACR", 3))
        return alerts

    def get_diagnoses(self, date=None):
        date = date if date is not None else self.date
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT reports.EntryDate, E10_Diabetes_I, E11_Diabetes_II, E_Diabetes_other, Obesity, Hypertension, Aldosteronism, Hyperuricemia, CKD_mild, CKD, kidney_failure_not_CKD, kidney_transplant, dialysis
            FROM diagnoses JOIN reports ON diagnoses.ReportID = reports.ReportId
            WHERE diagnoses.Patient = ? AND EntryDate <= ?
            """, (self.patient_id, date.strftime("%Y-%m-%d")))
        rows = cur.fetchall()
        diagnoses = np.zeros(12, dtype=int)
        for row in rows:
            current_diagnoses = np.array(row[1:], dtype=int)
            diagnoses += current_diagnoses
        return np.where(diagnoses > 0, 1, 0)

    def get_transplants(self, date=None):
        date = date if date is not None else self.date
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM transplantations
            WHERE Patient = ? AND EntryDate <= ?
            """, (self.patient_id, date.strftime("%Y-%m-%d")))
        rows = cur.fetchall()
        transplants = np.zeros(8, dtype=int)
        for row in rows:
            cur_transplants = np.array(row[3:], dtype=int)
            transplants += cur_transplants
        return transplants

    def is_in_nefrology_care(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT EntryDate
            FROM reports
            WHERE Patient = ? AND (reports.EntryDate <= ? AND clinic = 'KN')
            """, (self.patient_id, self.date.strftime("%Y-%m-%d")))
        row = cur.fetchone()
        return datetime.datetime.strptime(row[0], "%Y-%m-%d").date() if row is not None else datetime.date(year=1900, month=1, day=1), row is not None

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


    def get_lab(self, analyte, date=None, period=None):
        date = date if date is not None else self.date
        period = period if period is not None else self.period
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
                    FROM labs
                    WHERE Patient = ? AND analyte = ? AND EntryDate <= ?
                    ORDER BY EntryDate DESC;
                """, (self.patient_id, analyte, date.strftime("%Y-%m-%d")))
        rows = cur.fetchall()
        values = []
        if len(rows) == 0:
            return None, None, None, None, None, [], []
        last_measurement_date = datetime.datetime.strptime(rows[0][0], "%Y-%m-%d").date()
        minimum_date = last_measurement_date - period
        values_sum = 0
        values_count = 0
        values_dates = []
        for row in rows:
            current_date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
            if current_date < minimum_date:
                break
            if row is None or row[2] is None or row[4] != TYPICAL_UNIT[analyte]:
                continue
            values_sum += row[2]
            values_count += 1
            values.append(row[2])
            values_dates.append(current_date)

        if len(rows) != 0:
            row = rows[0]
            if row is None or row[2] is None or row[4] != TYPICAL_UNIT[analyte]:
                value = None
                note = None
            else:
                value = row[2]
                note = row[3]
        else:
            value = None
            note = None

        values_average = values_sum / values_count if values_count > 0 else None

        return last_measurement_date, value, TYPICAL_UNIT[analyte], note, values_average, values, values_dates

    def get_patient_info(self, date=None):
        date = date if date is not None else self.date
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
            raise MeasurementError("Pacient nebyl nalezen v databázi")
        if patient_data[0] is not None:
            dob = datetime.datetime.strptime(patient_data[0], '%Y-%m-%d')
            age = date.year - dob.year
        else:
            dob = None
            age = None
        if patient_data[1] is not None:
            sex = int(patient_data[1] == "F")
        else:
            sex = None
        return sex, dob, age


    def get_egfr(self, date=None, period=None):
        date = date if date is not None else self.date
        period = period if period is not None else self.period
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        # print(os.listdir(f"{os.curdir}/../../data/"))
        cur.execute("""
            SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
            FROM labs
            WHERE Patient = ? AND analyte = 'CKD-EPI' AND EntryDate <= ?
            ORDER BY EntryDate DESC;
        """, (self.patient_id, date.strftime("%Y-%m-%d")))
        rows = cur.fetchall()

        if len(rows) != 0:
            row = rows[0]
            last_measurement_date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
            minimum_date = last_measurement_date - period

            if row[2] is None or (row[4] != "ml/s/1,73 m2" and row[4] != "ml/s/spt"):
                value = None
                note = None
            else:
                value = row[2] * 60
                note = row[3]
            # print("CKD-EPI data")
            average_egfr = 0
            count_egfr = 0
            all_egfr = []
            values_dates = []
            for r in rows:
                current_date = datetime.datetime.strptime(r[0], "%Y-%m-%d").date()
                if current_date < minimum_date:
                    break
                if r[2] is None or (row[4] != "ml/s/1,73 m2" and row[4] != "ml/s/spt"):
                    continue
                average_egfr += r[2] * 60
                count_egfr += 1
                all_egfr.append(r[2] * 60)
                values_dates.append(current_date)
            average_egfr = average_egfr / count_egfr if count_egfr != 0 else None
            return last_measurement_date, value, "ml/min/1,73 m2", note, average_egfr, all_egfr, values_dates
        else:
            return self.get_egfr_from_s_kreatinin(date, period)

    def get_egfr_from_s_kreatinin(self, date=None, period=None):
        date = date if date is not None else self.date
        period = period if period is not None else self.period
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            """
                    SELECT EntryDate, analyte, ValueNumber, ValueText, unit 
                    FROM labs
                    WHERE Patient = ? AND analyte = 's_kreatinin' AND EntryDate <= ?
                    ORDER BY EntryDate DESC;
                """, (self.patient_id, date.strftime("%Y-%m-%d")))
        rows = cur.fetchall()
        if len(rows) == 0:
            return None, None, None, None, None, [], []

        values = []
        last_measurement_date = datetime.datetime.strptime(rows[0][0], "%Y-%m-%d").date()
        minimum_date = last_measurement_date - period

        values_sum = 0
        values_count = 0
        values_dates = []

        for row in rows:
            current_date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
            if current_date < minimum_date:
                break
            if self.sex is not None and self.age is not None and row[2] is not None and \
                row[4] == 'µmol/l':
                s_kreatinin = umol_l_to_mg_dl(row[2])
                values.append(
                    round(EGFR_COEF[self.sex][0] * min(s_kreatinin / EGFR_BOUNDARY[self.sex], 1) ** EGFR_COEF[self.sex][1]
                      * max(s_kreatinin / EGFR_BOUNDARY[self.sex], 1) ** (EGFR_COEF[self.sex][2]) *
                      (0.993 ** self.age), 1))
                values_sum += values[-1]
                values_count += 1
                values_dates.append(current_date)

        row = rows[0]
        if row[2] is None or row[4] != 'µmol/l' or self.sex is None or self.age is None:
            value = None
            note = None
        else:
            s_kreatinin = umol_l_to_mg_dl(row[2])
            value = round(EGFR_COEF[self.sex][0] * min(s_kreatinin / EGFR_BOUNDARY[self.sex], 1) ** EGFR_COEF[self.sex][1]
                          * max(s_kreatinin / EGFR_BOUNDARY[self.sex], 1) ** (EGFR_COEF[self.sex][2]) *
                          (0.993 ** self.age), 1)
            note = row[3]
        values_average = values_sum / values_count if values_count != 0 else None
        return last_measurement_date, value, "ml/min/1,73 m2", note, values_average, values, values_dates

DB = "../../data/CKD_train.db"

def mg_dl_to_umol_l(mg_dl):
    return mg_dl / KREATININ_MOLAR_MASS * 10000

def umol_l_to_mg_dl(umol_l):
    return umol_l * KREATININ_MOLAR_MASS / 10000


if __name__ == '__main__':
    patient = Patient(1215860, datetime.date(year=2025, month=1, day=1), period=datetime.timedelta(days=5000))
    # patient = Patient(840, datetime.date(year=2021, month=1, day=1))
    # patient = Patient(4030, datetime.date(year=2021, month=1, day=1))
    print(patient.__dict__)
    print(patient.alerts)
