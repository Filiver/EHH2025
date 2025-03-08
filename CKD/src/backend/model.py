import sqlite3
import numpy as np

def calculate_egfr(patient_id):
    try:
        conn = sqlite3.connect('../data/CKD_train.db')
        cur = conn.cursor()
        cur.execute(f"""
            SELECT entry_date, analyte, value_number, value_text, unit FROM lab_results
            WHERE patient_id = {patient_id} AND analyte = 'CKD_EPI' ORDER BY entry_date DESC;
        """)
        row = cur.fetchone()
        print(row)
    except sqlite3.OperationalError:
        print("Error: Could not connect to database.")
        return None

if __name__ == '__main__':
    calculate_egfr(9150)