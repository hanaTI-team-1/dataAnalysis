from flask import Flask, jsonify, request
import subprocess
import json
import re
import logging
import os

app = Flask(__name__)

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

# Function to delete logs.log file if it exists
def delete_log_file():
    log_file = 'logs.log'
    if os.path.exists(log_file):
        os.remove(log_file)

@app.route('/run-a', methods=['POST'])
def run_a():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Convert JSON data to string
        json_data_str = json.dumps(json_data)

        # Run a.py and capture the output
        result = subprocess.run(
            ['python3', 'a.py'],
            input=json_data_str,
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        error_output = result.stderr.strip()

        # Extract JSON part from the output using regex
        match = re.search(r'{.*}', output, re.DOTALL)
        if match:
            json_output = match.group(0)
            delete_log_file()
            return jsonify(json.loads(json_output)), 200
        else:
            delete_log_file()
            return jsonify({"result": output, "stderr": error_output}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e), "output": e.output, "stderr": e.stderr}), 500

@app.route('/run-b', methods=['POST'])
def run_b():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Convert JSON data to string
        json_data_str = json.dumps(json_data)

        # Run a.py and capture the output
        result = subprocess.run(
            ['python3', 'b.py'],
            input=json_data_str,
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        error_output = result.stderr.strip()

        # Extract JSON part from the output using regex
        match = re.search(r'{.*}', output, re.DOTALL)
        if match:
            json_output = match.group(0)
            return jsonify(json.loads(json_output)), 200
        else:
            return jsonify({"result": output, "stderr": error_output}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e), "output": e.output, "stderr": e.stderr}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
