import os
import json
from tkinter import *
from tkinter import ttk
from utils.helpers import ensure_folder_exists

# Path to history file
HISTORY_FILE = os.path.join("data", "employee_history.json")
ensure_folder_exists("data")

# Load history logs
def load_employee_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)
        return data.get("logs", [])

# GUI Window
def show_employee_history():
    history = load_employee_history()

    win = Tk()
    win.title("📜 Employee Registration & Removal History")
    win.geometry("700x450")
    win.resizable(True,True)
    win.configure(bg="#f0f9ff")

    Label(win, text="Employee History", font=("Segoe UI", 16, "bold"), bg="#f0f9ff").pack(pady=10)

    columns = ("emp_id", "name", "action", "timestamp")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=15)

    tree.heading("emp_id", text="Employee ID")
    tree.heading("name", text="Name")
    tree.heading("action", text="Action")
    tree.heading("timestamp", text="Timestamp")

    tree.column("emp_id", anchor=CENTER, width=100)
    tree.column("name", anchor=W, width=180)
    tree.column("action", anchor=CENTER, width=100)
    tree.column("timestamp", anchor=W, width=250)

    for log in reversed(history):  # Most recent first
        tree.insert("", END, values=(
            log["emp_id"],
            log["name"],
            log["action"].capitalize(),
            log["timestamp"]
        ))

    tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

    win.mainloop()

if __name__ == "__main__":
    show_employee_history()
