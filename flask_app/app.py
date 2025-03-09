from flask import render_template, Flask, jsonify, send_from_directory
import json
from pathlib import Path
import sys
from datetime import datetime as my_type, date, timedelta

ROOT_DIR = Path(__file__).resolve().parent
# For presentation
CKD_DIR = ROOT_DIR.parent / 'CKD'
SRC_DIR = CKD_DIR / 'src' / 'backend'

DB = CKD_DIR / "data" / "CKD_train.db"
print(SRC_DIR)
sys.path.append(str(SRC_DIR))
from model import Patient, change_db, Alert, change_ml_models
change_db(str(DB))
change_ml_models(SRC_DIR.parent / 'ML_models')


app = Flask(__name__)
app.config["DEBUG"] = True  # Enable Debug Mode


def default(o):
    if isinstance(o, (date, my_type)):
        return o.isoformat()
    if isinstance(o, timedelta):
        return str(o)
    if isinstance(o, Alert):
        return o.toJSON()
    return o


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/api/data/<int:patient_id>', methods=['GET'])
def get_data(patient_id):
    # try:
    patient = Patient(patient_id, risk_assesment=True)
    data = patient.toJSON()
    print(data)
    # print(jsonify(patient))
    return json.dumps(data)
    # except Exception as e:
    #     print(e)
    #     return jsonify({'error': str(e)}), 404
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
