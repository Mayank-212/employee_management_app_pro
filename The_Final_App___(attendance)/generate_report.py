# generate_report.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from fpdf import FPDF
import pandas as pd
from config import ATTENDANCE_FOLDER, REPORT_FOLDER, COMPANY_NAME
from utils.helpers import ensure_folder

def generate_report_gui():
    ensure_folder(REPORT_FOLDER)

    # Ask user to select an attendance Excel file
    file_path = filedialog.askopenfilename(title="Select Attendance Excel File",
                                           filetypes=[("Excel files", "*.xlsx")],
                                           initialdir=ATTENDANCE_FOLDER)
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)
        date = os.path.basename(file_path).replace(".xlsx", "")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, COMPANY_NAME, ln=True, align='C')
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, f"Attendance Report - {date}", ln=True, align='C')
        pdf.ln(10)

        # Table header
        pdf.set_font("Arial", "B", 10)
        headers = ["ID", "Name", "Time", "Status", "Is Sunday"]
        for header in headers:
            pdf.cell(38, 10, header, border=1)
        pdf.ln()

        # Table rows
        pdf.set_font("Arial", "", 10)
        for _, row in df.iterrows():
            pdf.cell(38, 10, str(row["ID"]), border=1)
            pdf.cell(38, 10, str(row["Name"]), border=1)
            pdf.cell(38, 10, str(row["Time"]), border=1)
            pdf.cell(38, 10, str(row["Status"]), border=1)
            pdf.cell(38, 10, str(row["Is Sunday"]), border=1)
            pdf.ln()

        # Save PDF
        save_path = os.path.join(REPORT_FOLDER, f"report_{date}.pdf")
        pdf.output(save_path)

        messagebox.showinfo("Success", f"Report generated successfully:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate report:\n{e}")
 
