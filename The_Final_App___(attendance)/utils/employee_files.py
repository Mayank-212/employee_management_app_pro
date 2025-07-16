# utils/employee_files.py

import os
import pandas as pd
from config_handler import load_config

def load_employees():
    path = os.path.join("database", "employees.pkl")
    return pd.read_pickle(path) if os.path.exists(path) else {}

def save_employees(data):
    path = os.path.join("database", "employees.pkl")
    pd.to_pickle(data, path)

def save_to_employee_excel(emp_id, entry_time, exit_time, salary_paid):
    config = load_config()
    file_path = config["employee_excel_file_template"].replace("<ID>", emp_id)

    data = {
        "Date": [pd.Timestamp.today().strftime("%Y-%m-%d")],
        "Entry": [entry_time],
        "Exit": [exit_time],
        "Salary Paid": [salary_paid]
    }

    df = pd.DataFrame(data)

    if os.path.exists(file_path):
        existing = pd.read_excel(file_path)
        df = pd.concat([existing, df], ignore_index=True)

    df.to_excel(file_path, index=False)
