import os
import json
import pickle
from tkinter import *
import datetime  # Make sure this is at the top of your file
from tkinter import messagebox, ttk
from config import load_config
from utils.helpers import initialize_app_environment, initialize_sensor

# ✅ Load configuration
config = load_config()
DATA_DIR = "data"
EMPLOYEE_FILE = os.path.join(DATA_DIR,"employees", "employees.json")
PKL_DIR = "employees_data"
ADMIN_PASSWORD = config.get("admin_password", "6965")
PORT = config.get("fingerprint_port", "COM6")


initialize_app_environment()


def log_employee_history(emp_id, name, action):
    log_file = os.path.join("data", "employee_history.json")
    
    # Load existing logs if available
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            history = json.load(f)
    else:
        history = {"logs": []}

    # Append new entry
    history["logs"].append({
        "emp_id": emp_id,
        "name": name,
        "action": action,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Save back to file
    with open(log_file, "w") as f:
        json.dump(history, f, indent=4)


def load_employees():
    if not os.path.exists(EMPLOYEE_FILE):
        return {}
    with open(EMPLOYEE_FILE, "r") as f:
        return json.load(f)

def save_employees(employees):
    with open(EMPLOYEE_FILE, "w") as f:
        json.dump(employees, f, indent=4)

def get_fingerprint_ids(emp_id):
    """Get fingerprint IDs list from .pkl"""
    try:
        pkl_file = os.path.join(PKL_DIR, f"{emp_id}.pkl")
        with open(pkl_file, "rb") as f:
            data = pickle.load(f)
        return data.get("fingerprint_ids") or [data.get("fingerprint_id")]
    except Exception as e:
        print(f"[Error loading .pkl] {e}")
        return []

def delete_fingerprints_from_sensor(positions):
    sensor = initialize_sensor(PORT)
    if not sensor:
        print("[ERROR] Sensor not detected.")
        return
    deleted = []
    for pos in positions:
        try:
            sensor.deleteTemplate(pos)
            deleted.append(pos)
        except Exception as e:
            print(f"[ERROR] Failed to delete position {pos}: {e}")
    print(f"[SENSOR] Deleted fingerprint positions: {deleted}")

def remove_employee(emp_id, win, password_entry):
    admin_input = password_entry.get().strip()
    if admin_input != ADMIN_PASSWORD:
        messagebox.showerror("Access Denied", "Invalid admin password.")
        return

    employees = load_employees()
    if emp_id not in employees:
        messagebox.showerror("Error", "Employee not found.")
        return

    emp_name = employees[emp_id]["name"]
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove {emp_name}?")
    if not confirm:
        return

    # Delete from employees.json
    del employees[emp_id]
    save_employees(employees)

    # Delete .pkl file
    pkl_file = os.path.join(PKL_DIR, f"{emp_id}.pkl")
    if os.path.exists(pkl_file):
        try:
            fingerprint_ids = get_fingerprint_ids(emp_id)
            delete_fingerprints_from_sensor(fingerprint_ids)
            os.remove(pkl_file)
            print(f"[FILE] Deleted {pkl_file}")
        except Exception as e:
            print(f"[ERROR] Failed to delete .pkl file: {e}")

    # 🗑️ Delete attendance JSON files
    # 🗑️ Delete attendance folder for employee
    att_dir = config.get("attendance_data_dir", "data/attendance")
    emp_att_dir = os.path.join(att_dir, emp_id)
    if os.path.exists(emp_att_dir):
        import shutil
        try:
            shutil.rmtree(emp_att_dir)
            print(f"[ATTENDANCE] Deleted folder: {emp_att_dir}")
        except Exception as e:
            print(f"[ERROR] Failed to delete attendance folder for {emp_id}: {e}")

    # 🗑️ Delete attendance PDFs (if used)
    att_pdf_dir = os.path.join("attendance_pdfs", emp_id)
    if os.path.exists(att_pdf_dir):
        import shutil
        try:
            shutil.rmtree(att_pdf_dir)
            print(f"[PDF] Deleted attendance_pdfs/{emp_id}")
        except Exception as e:
            print(f"[ERROR] Failed to delete attendance_pdfs/{emp_id}: {e}")

    log_employee_history(emp_id, emp_name, "removed")
    messagebox.showinfo("Success", f"{emp_name} removed successfully.")
    win.destroy()


    # Delete from employees.json
    del employees[emp_id]
    save_employees(employees)

    # Delete .pkl file
    pkl_file = os.path.join(PKL_DIR, f"{emp_id}.pkl")
    if os.path.exists(pkl_file):
        try:
            fingerprint_ids = get_fingerprint_ids(emp_id)
            delete_fingerprints_from_sensor(fingerprint_ids)
            os.remove(pkl_file)
            print(f"[FILE] Deleted {pkl_file}")
        except Exception as e:
            print(f"[ERROR] Failed to delete .pkl file: {e}")
            
    log_employee_history(emp_id, emp_name, "removed")
    messagebox.showinfo("Success", f"{emp_name} removed successfully.")
    win.destroy()

def open_remove_gui():
    win = Tk()
    win.title("🗑 Remove Employee")
    win.geometry("430x300")
    win.resizable(True,True)
    win.configure(bg="#f4faff")

    Label(win, text="Remove Registered Employee", font=("Segoe UI", 16, "bold"), bg="#f4faff").pack(pady=10)

    employees = load_employees()
    emp_ids = list(employees.keys())

    frame = Frame(win, bg="#f4faff")
    frame.pack(pady=5)

    Label(frame, text="Select Employee ID:", bg="#f4faff").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    emp_id_var = StringVar()
    emp_dropdown = ttk.Combobox(frame, textvariable=emp_id_var, values=emp_ids, state="readonly", width=25)
    emp_dropdown.grid(row=0, column=1, padx=10, pady=5)

    emp_name_var = StringVar()
    Label(frame, text="Employee Name:", bg="#f4faff").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    Label(frame, textvariable=emp_name_var, font=("Segoe UI", 10, "bold"), bg="#f4faff", fg="#003366").grid(row=1, column=1, sticky="w", padx=10)

    Label(frame, text="Admin Password:", bg="#f4faff").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    password_entry = Entry(frame, show="*", width=25)
    password_entry.grid(row=2, column=1, padx=10, pady=5)

    def on_select(event):
        emp_id = emp_id_var.get()
        if emp_id in employees:
            emp_name_var.set(employees[emp_id]["name"])
        else:
            emp_name_var.set("")

    emp_dropdown.bind("<<ComboboxSelected>>", on_select)

    Button(win, text="Remove Employee", bg="#dc3545", fg="white", width=20,
           command=lambda: remove_employee(emp_id_var.get(), win, password_entry)).pack(pady=20)

    win.mainloop()

if __name__ == "__main__":
    open_remove_gui()
