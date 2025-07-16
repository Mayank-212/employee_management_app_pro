import os
import json
from tkinter import *
from tkinter import ttk
from config import load_config
from utils.helpers import initialize_app_environment

# Load config
config = load_config()

# Correct path to employees.json
EMPLOYEE_FILE = os.path.join(config["data_directory"],"employees", "employees.json")

# Ensure folders exist
initialize_app_environment()

def load_employees():
    if not os.path.exists(EMPLOYEE_FILE):
        return {}
    with open(EMPLOYEE_FILE, "r") as f:
        return json.load(f)

def show_employees_gui():
    win = Tk()
    win.title("👥 Registered Employees")
    win.geometry("500x400")
    win.resizable(True,True)
    win.configure(bg="#f4faff")

    Label(win, text="Registered Employees", font=("Segoe UI", 16, "bold"), bg="#f4faff", fg="#003366").pack(pady=20)

    columns = ("ID", "Name", "Salary")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)
    tree.heading("ID", text="Employee ID")
    tree.heading("Name", text="Name")
    tree.heading("Salary", text="Salary ₹")

    tree.column("ID", anchor=CENTER, width=100)
    tree.column("Name", anchor=W, width=200)
    tree.column("Salary", anchor=CENTER, width=100)

    employees = load_employees()
    for emp_id, info in employees.items():
        tree.insert("", END, values=(
    emp_id,
    info.get("name", "N/A"),
    info.get("salary", "N/A")
))


    tree.pack(pady=10, padx=10, fill=BOTH, expand=True)
    win.mainloop()

if __name__ == "__main__":
    show_employees_gui()
