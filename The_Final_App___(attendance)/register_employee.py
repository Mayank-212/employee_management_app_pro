import os
import pickle
import tkinter as tk
from tkinter import messagebox
from utils.helpers import (
    initialize_sensor,
    speak,
    save_json,
    load_json,
    get_employee_file_path,
    initialize_app_environment,
    ensure_folder_exists
)
import json

import datetime  # Make sure this is at the top of your file

def log_employee_history(emp_id, name, action):
    log_file = os.path.join("data", "employee_history.json")
    
    # Load existing logs if available
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            print("[WARN] employee_history.json is corrupted or empty. Resetting.")
            history = {"logs": []}
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

# Initialize folders
initialize_app_environment()

# Load config
config = load_json("config.json")
sensor_port = config.get("fingerprint_port", "COM6")
sensor = initialize_sensor(sensor_port)

if not sensor:
    speak("Fingerprint sensor not detected.")
    messagebox.showerror("Error", "Fingerprint sensor not found.")
    exit()

# GUI Setup
root = tk.Tk()
root.title("Register New Employee")
root.geometry("400x400")
root.configure(bg="#e6f2ff")

tk.Label(root, text="Enter Employee Name", font=("Arial", 12), bg="#e6f2ff").pack(pady=5)
name_entry = tk.Entry(root, font=("Arial", 12))
name_entry.pack(pady=5)

tk.Label(root, text="Enter Employee ID", font=("Arial", 12), bg="#e6f2ff").pack(pady=5)
id_entry = tk.Entry(root, font=("Arial", 12))
id_entry.pack(pady=5)

tk.Label(root, text="Enter Salary", font=("Arial", 12), bg="#e6f2ff").pack(pady=5)
salary_entry = tk.Entry(root, font=("Arial", 12))
salary_entry.pack(pady=5)

def register():
    name = name_entry.get().strip()
    emp_id = id_entry.get().strip()
    salary = salary_entry.get().strip()

    if not name or not emp_id or not salary:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    try:
        salary = float(salary)
    except ValueError:
        messagebox.showerror("Input Error", "Salary must be a number.")
        return

    employee_file = get_employee_file_path(emp_id)
    json_path = os.path.join("data", "employees", "employees.json")
    employees = load_json(json_path)
    if emp_id in employees or os.path.exists(employee_file):
        messagebox.showwarning("Duplicate", "Employee already registered.")
        return

    fingerprint_ids = []

    try:
        for i in range(5):  # Capture 5 fingerprint scans
            messagebox.showinfo("Scan", f"Place the same finger for scan {i+1}/5")
            while not sensor.readImage():
                pass
            sensor.convertImage(0x01)
            position = sensor.storeTemplate()
            fingerprint_ids.append(position)
            print(f"[REGISTER] Stored fingerprint at position: {position}")
    except Exception as e:
        messagebox.showerror("Error", f"Fingerprint registration failed: {str(e)}")
        return

    emp_data = {
        "id": emp_id,
        "name": name,
        "salary": salary,
        "fingerprint_ids": fingerprint_ids
    }

    with open(employee_file, "wb") as f:
        pickle.dump(emp_data, f)

    # Also update employees.json
    json_path = os.path.join("data", "employees", "employees.json")
    ensure_folder_exists(os.path.dirname(json_path))
    employees = load_json(json_path)
    employees[emp_id] = {"name": name, "salary": salary}
    save_json(json_path, employees)
    log_employee_history(emp_id, name, "registered")
    speak(f"Employee {name} registered successfully.")
    messagebox.showinfo("Success", f"Employee {name} registered successfully.")

    # Clear fields
    name_entry.delete(0, tk.END)
    id_entry.delete(0, tk.END)
    salary_entry.delete(0, tk.END)

tk.Button(root, text="Register", command=register, font=("Arial", 12), bg="#007acc", fg="white").pack(pady=20)

root.mainloop()
