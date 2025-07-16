import os
import json
from tkinter import *
from tkinter import messagebox, ttk
from config import load_config
from utils.helpers import initialize_app_environment

# Load configuration
config = load_config()
EMPLOYEE_FILE = os.path.abspath(os.path.join(config["data_directory"] ,"employees", "employees.json"))

# Ensure folders exist
initialize_app_environment()

def load_employees():
    if not os.path.exists(EMPLOYEE_FILE):
        return {}
    try:
        with open(EMPLOYEE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_employees(employees):
    os.makedirs(os.path.dirname(EMPLOYEE_FILE), exist_ok=True)
    with open(EMPLOYEE_FILE, "w") as f:
        json.dump(employees, f, indent=4)

def edit_salary(emp_id, new_salary, win):
    employees = load_employees()

    if emp_id in employees:
        try:
            new_salary = float(new_salary)
        except ValueError:
            messagebox.showerror("Invalid Input", "Salary must be a number.")
            return

        employees[emp_id]["salary"] = new_salary
        save_employees(employees)
        messagebox.showinfo("Success", f"Salary updated for {employees[emp_id]['name']}.")
        win.destroy()
    else:
        messagebox.showerror("Error", "Employee not found.")

def open_edit_salary_gui():
    employees = load_employees()
    emp_ids = list(employees.keys())

    if not emp_ids:
        messagebox.showwarning("No Employees", "No registered employees found.")
        return

    win = Tk()
    win.title("📝 Edit Employee Salary")
    win.geometry("440x320")
    win.configure(bg="#f4faff")

    Label(win, text="Edit Employee Salary", font=("Segoe UI", 16, "bold"), bg="#f4faff", fg="#003366").pack(pady=20)

    frame = Frame(win, bg="#f4faff")
    frame.pack(pady=10)

    emp_id_var = StringVar()
    emp_dropdown = ttk.Combobox(frame, textvariable=emp_id_var, values=emp_ids, state="readonly", width=28)
    emp_dropdown.grid(row=0, column=1, pady=5)
    Label(frame, text="Employee ID:", bg="#f4faff").grid(row=0, column=0, sticky="w", padx=10, pady=5)

    name_var = StringVar()
    salary_var = StringVar()

    Label(frame, text="Name:", bg="#f4faff").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    Label(frame, textvariable=name_var, bg="#f4faff", font=("Segoe UI", 10, "bold")).grid(row=1, column=1, sticky="w", padx=10)

    Label(frame, text="Current Salary:", bg="#f4faff").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    Label(frame, textvariable=salary_var, bg="#f4faff", font=("Segoe UI", 10, "bold")).grid(row=2, column=1, sticky="w", padx=10)

    Label(frame, text="New Salary (₹):", bg="#f4faff").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    new_salary_entry = Entry(frame, width=25)
    new_salary_entry.grid(row=3, column=1, pady=5)

    def on_select(event):
        emp_id = emp_id_var.get()
        if emp_id in employees:
            name_var.set(employees[emp_id]["name"])
            salary_var.set(str(employees[emp_id]["salary"]))
        else:
            name_var.set("")
            salary_var.set("")

    emp_dropdown.bind("<<ComboboxSelected>>", on_select)

    Button(win, text="Update Salary", command=lambda: edit_salary(emp_id_var.get(), new_salary_entry.get(), win),
           bg="#007acc", fg="white", font=("Segoe UI", 10), width=20).pack(pady=20)

    win.mainloop()

if __name__ == "__main__":
    open_edit_salary_gui()
