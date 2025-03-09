from flask import render_template, Flask, jsonify, send_from_directory
import json
from pathlib import Path

app = Flask(__name__)
app.config["DEBUG"] = True  # Enable Debug Mode

ROOT_DIR = Path(__file__).resolve().parent


@app.route('/')
def start():
    return render_template('index.html')


@app.route('/api/data', methods=['GET'])
def get_data():
    return send_from_directory(ROOT_DIR / 'dummies', 'patient.json')
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
