from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('files')
    daily_reports = {}
    new_employees_data = []

    for file in uploaded_files:
        filename = secure_filename(file.filename)
        content = file.read()
        df = pd.read_excel(BytesIO(content))

        if filename.startswith("Daily report_"):
            parts = filename.replace('.xls', '').replace('.xlsx', '').split('_')
            team_member = parts[-2] + ' ' + parts[-1]
            df['Team Member'] = team_member
            daily_reports[filename] = df
        elif filename.startswith("New Employee_"):
            new_employees_data.append(df)

    if not new_employees_data:
        return jsonify({"error": "No New Employee files found"}), 400
    if not daily_reports:
        return jsonify({"error": "No Daily Report files found"}), 400

    new_employees = pd.concat(new_employees_data, ignore_index=True)

    mapped_data = []
    for file, df in daily_reports.items():
        for _, row in df.iterrows():
            matched = new_employees[new_employees['Employee Name'] == row.get('Candidate Name')]
            for _, emp in matched.iterrows():
                mapped_data.append({
                    "Employee Name": emp["Employee Name"],
                    "Join Date": str(emp["Join Date"]),
                    "Role": emp["Role"],
                    "Team Member": row["Team Member"]
                })

    return jsonify(mapped_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)