from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    dashboard = []
    daily_tables = []
    new_emp_tables = []

    if request.method == "POST":
        files = request.files.getlist("files")
        daily_reports = []
        new_employees = []

        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            if filename.startswith("Daily report_"):
                df = pd.read_excel(filepath)
                parts = filename.replace(".xls", "").replace(".xlsx", "").split("_")
                df["Team Member"] = parts[-2] + " " + parts[-1]
                daily_reports.append(df)
                daily_tables.append(df)
            elif filename.startswith("New Employee_"):
                df = pd.read_excel(filepath)
                new_employees.append(df)
                new_emp_tables.append(df)

        if daily_reports and new_employees:
            new_emps = pd.concat(new_employees, ignore_index=True)
            mapped = []
            for df in daily_reports:
                for _, row in df.iterrows():
                    match = new_emps[new_emps['Employee Name'] == row['Candidate Name']]
                    if not match.empty:
                        for _, emp in match.iterrows():
                            mapped.append({
                                'Employee Name': emp['Employee Name'],
                                'Join Date': emp['Join Date'],
                                'Role': emp['Role'],
                                'Team Member': row['Team Member']
                            })
            dashboard = mapped

    return render_template("index.html", daily_tables=daily_tables, new_emp_tables=new_emp_tables, dashboard=dashboard)
