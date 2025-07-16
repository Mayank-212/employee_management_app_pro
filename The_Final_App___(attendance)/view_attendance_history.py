import os
import json
import datetime
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from config import load_config
from utils.helpers import get_attendance_folder, get_attendance_file_path

# Load attendance for given date
def load_attendance_by_date(selected_date):
    attendance_data = []
    base_dir = get_attendance_folder()  # This points to 'data/attendance'

    if not os.path.exists(base_dir):
        return []

    for emp_id in os.listdir(base_dir):
        emp_dir = os.path.join(base_dir, emp_id)
        if not os.path.isdir(emp_dir):
            continue

        file_path = os.path.join(emp_dir, f"{selected_date}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                attendance_data.append({
                    "emp_id": emp_id,
                    "name": data.get("name", ""),
                    "entry_time": data.get("entry_time", "-"),
                    "exit_time": data.get("exit_time", "-")
                })
            except:
                continue

    return attendance_data

# GUI Window
def show_attendance_history():
    win = Tk()
    win.title("📅 Attendance History Viewer")
    win.geometry("750x480")
    win.resizable(True,True)
    win.configure(bg="#f4f9ff")

    Label(win, text="View Attendance by Date", font=("Segoe UI", 16, "bold"), bg="#f4f9ff").pack(pady=10)

    # Date Picker
    date_frame = Frame(win, bg="#f4f9ff")
    date_frame.pack(pady=10)

    Label(date_frame, text="Select Date:", bg="#f4f9ff", font=("Segoe UI", 12)).pack(side=LEFT, padx=10)
    cal = DateEntry(date_frame, width=12, background='darkblue',
                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    cal.pack(side=LEFT, padx=5)

    tree = ttk.Treeview(win, columns=("ID", "Name", "Entry", "Exit"), show="headings", height=15)
    tree.heading("ID", text="Employee ID")
    tree.heading("Name", text="Name")
    tree.heading("Entry", text="Entry Time")
    tree.heading("Exit", text="Exit Time")

    tree.column("ID", width=100, anchor=CENTER)
    tree.column("Name", width=200, anchor=W)
    tree.column("Entry", width=150, anchor=CENTER)
    tree.column("Exit", width=150, anchor=CENTER)

    tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

    def load_and_display():
        selected_date = cal.get_date().strftime("%Y-%m-%d")
        tree.delete(*tree.get_children())
        records = load_attendance_by_date(selected_date)
        if not records:
            tree.insert("", END, values=("No records", "", "", ""))
        else:
            for rec in records:
                tree.insert("", END, values=(
                    rec["emp_id"],
                    rec["name"],
                    rec["entry_time"],
                    rec["exit_time"]
                ))

    Button(win, text="🔍 Load Attendance", command=load_and_display, bg="#007acc", fg="white", font=("Segoe UI", 11)).pack(pady=5)

    win.mainloop()

if __name__ == "__main__":
    show_attendance_history()
