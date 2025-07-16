# utils/export.py

import os
import json
import pandas as pd
from fpdf import FPDF

def export_to_excel_pdf(emp_id):
    attendance_file = f"data/attendance/{emp_id}.json"
    salary_file = f"data/salary_summary/{emp_id}.json"
    export_dir = f"exports/{emp_id}"
    os.makedirs(export_dir, exist_ok=True)

    # Excel export
    data = []
    if os.path.exists(attendance_file):
        with open(attendance_file, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df.to_excel(f"{export_dir}/attendance.xlsx", index=False)

    # PDF export for salary
    if os.path.exists(salary_file):
        with open(salary_file, "r") as f:
            salary_data = json.load(f)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Salary Summary for {emp_id}", ln=True, align="C")

        for date, values in salary_data.items():
            line = f"{date}: Entry - {values['entry']}, Exit - {values['exit']}, Salary - ₹{values['amount']}"
            pdf.cell(200, 10, txt=line, ln=True)

        pdf.output(f"{export_dir}/salary_summary.pdf")
