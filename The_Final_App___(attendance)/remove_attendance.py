import os
import json
import shutil
from tkinter import *
from tkinter import ttk, messagebox
from config import load_config
from utils.helpers import initialize_app_environment

# Load config
config = load_config()
DATA_DIR = config["data_directory"]
ATTENDANCE_DIR = os.path.join(DATA_DIR, "attendance")
ATTENDANCE_PDF_DIR = os.path.join(DATA_DIR, "attendance_pdfs")
EMPLOYEE_FILE = os.path.join(DATA_DIR, "employees", "employees.json")

# Initialize environment
initialize_app_environment()

# Load employees
def load_employees():
    if not os.path.exists(EMPLOYEE_FILE):
        return {}
    with open(EMPLOYEE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# ✅ Fixed: List available .json attendance files (not .csv)
def list_attendance_dates(emp_id):
    emp_dir = os.path.join(ATTENDANCE_DIR, emp_id)
    dates = []

    if not os.path.exists(emp_dir):
        return []

    for f in os.listdir(emp_dir):
        if f.endswith(".json"):
            try:
                date_part = f.replace(".json", "")
                dates.append(date_part)
            except Exception:
                continue

    return dates

# Delete attendance files
def delete_attendance(emp_id, date, win):
    json_file = os.path.join(ATTENDANCE_DIR, emp_id, f"{date}.json")

    if os.path.exists(json_file):
        os.remove(json_file)
        messagebox.showinfo("✅ Success", f"Attendance for {emp_id} on {date} deleted.")
        win.destroy()
    else:
        messagebox.showerror("❌ Not Found", "No attendance file found for selected date.")

# GUI Window
def open_remove_attendance_gui():
    win = Tk()
    win.title("🧽 Remove Attendance Record")
    win.geometry("480x300")
    win.configure(bg="#f4faff")

    Label(win, text="Remove Attendance Record", font=("Segoe UI", 16, "bold"), bg="#f4faff").pack(pady=20)

    employees = load_employees()
    emp_ids = list(employees.keys())

    frame = Frame(win, bg="#f4faff")
    frame.pack(pady=10)

    emp_var = StringVar()
    date_var = StringVar()

    Label(frame, text="Employee ID:", bg="#f4faff").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    emp_dropdown = ttk.Combobox(frame, textvariable=emp_var, values=emp_ids, state="readonly", width=25)
    emp_dropdown.grid(row=0, column=1, pady=5)

    Label(frame, text="Select Date:", bg="#f4faff").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    date_dropdown = ttk.Combobox(frame, textvariable=date_var, values=[], state="readonly", width=25)
    date_dropdown.grid(row=1, column=1, pady=5)

    def on_emp_select(event):
        emp_id = emp_var.get()
        dates = list_attendance_dates(emp_id)
        date_dropdown['values'] = dates
        date_var.set(dates[0] if dates else "")

    emp_dropdown.bind("<<ComboboxSelected>>", on_emp_select)

    Button(win, text="Remove Attendance", command=lambda: delete_attendance(emp_var.get(), date_var.get(), win),
           bg="#dc3545", fg="white", width=25).pack(pady=20)

    win.mainloop()

if __name__ == "__main__":
    open_remove_attendance_gui()