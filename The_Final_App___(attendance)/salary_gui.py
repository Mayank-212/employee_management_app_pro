import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from salary_calculator import calculate_salary_summary
from utils.helpers import load_json

EMPLOYEE_FILE = "data/employees/employees.json"
PKL_DIR = "employees_data"

def status_circle(status):
    return {
        "present": "🟢",
        "half": "🟡",
        "absent": "🔴"
    }.get(status, "⚪")

def save_pdf(summary, from_date, to_date):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    default_name = f"{summary['emp_id']}__{from_date}_to_{to_date}.pdf"
    path = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not path:
        return

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 11)

    c.drawString(50, height - 40, f"Salary Report for {summary['name']} (ID: {summary['emp_id']})")
    y = height - 60
    c.drawString(50, y, "Date        Status        Salary Received     Entry Time     Exit Time")
    y -= 15

    for record in summary["summary_data"]:
        date = record["date"]
        status = record["status"]
        emoji = {
            "present": "🟢",
            "half": "🟡",
            "absent": "🔴"
        }.get(status, "⚪")
        day_salary = record.get("day_salary", 0)
        entry = record["entry"]
        exit_ = record["exit"]
        line = f"{date}    {status} {emoji}         ₹{int(day_salary)}            {entry}         {exit_}"
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40

    y -= 20
    c.drawString(50, y, f"Full Days: {summary['full_days']}   Half Days: {summary['half_days']}   Absent Days: {summary['absent_days']}")
    y -= 15
    c.drawString(50, y, f"Sunday Bonus: ₹{summary['sunday_bonus']}   Total Salary: ₹{summary['total_salary']}")
    c.save()
    messagebox.showinfo("Saved", f"PDF saved to:\n{path}")

def save_excel(summary, from_date, to_date):
    default_name = f"{summary['emp_id']}__{from_date}_to_{to_date}.xlsx"
    path = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if not path:
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Salary Report"

    ws.append(["Date", "Status", "Salary (this day)", "Entry Time", "Exit Time"])
    for record in summary["summary_data"]:
        status = record["status"]
        emoji = {
            "present": "🟢",
            "half": "🟡",
            "absent": "🔴"
        }.get(status, "⚪")
        ws.append([
            record["date"],
            f"{status} {emoji}",
            int(record.get("day_salary", 0)),
            record["entry"],
            record["exit"]
        ])

    ws.append([])
    ws.append(["Full Days", summary["full_days"]])
    ws.append(["Half Days", summary["half_days"]])
    ws.append(["Absent Days", summary["absent_days"]])
    ws.append(["Sunday Bonus", summary["sunday_bonus"]])
    ws.append(["Total Salary", summary["total_salary"]])
    wb.save(path)
    messagebox.showinfo("Saved", f"Excel saved to:\n{path}")

def show_salary_gui():
    root = tk.Tk()
    root.title("💰 Salary Summary Dashboard")
    root.geometry("1150x560")
    root.configure(bg="#e6f2ff")
    root.resizable(True, True)

    tk.Label(root, text="From Date:", bg="#e6f2ff", font=("Arial", 10)).place(x=20, y=15)
    from_date = DateEntry(root, width=12, background='blue', foreground='white', date_pattern='yyyy-mm-dd')
    from_date.place(x=100, y=15)

    tk.Label(root, text="To Date:", bg="#e6f2ff", font=("Arial", 10)).place(x=250, y=15)
    to_date = DateEntry(root, width=12, background='blue', foreground='white', date_pattern='yyyy-mm-dd')
    to_date.place(x=310, y=15)

    columns = ("ID", "Name", "Full", "Half", "Absent", "Bonus", "Total", "PDF", "Excel")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    column_widths = {
        "ID": 100, "Name": 160, "Full": 80, "Half": 80, "Absent": 80,
        "Bonus": 100, "Total": 100, "PDF": 70, "Excel": 70
    }
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=column_widths.get(col, 100))
    tree.place(x=20, y=70, width=1100, height=420)

    def generate():
        tree.delete(*tree.get_children())
        employees = load_json(EMPLOYEE_FILE)
        for emp_id, emp in employees.items():
            if not os.path.exists(os.path.join(PKL_DIR, f"{emp_id}.pkl")):
                continue
            f_date = datetime.strptime(from_date.get(), "%Y-%m-%d")
            t_date = datetime.strptime(to_date.get(), "%Y-%m-%d")
            summary = calculate_salary_summary(emp_id, f_date, t_date)
            if summary:
                tree.insert("", "end", values=(
                    emp_id,
                    summary["name"],
                    summary["full_days"],
                    summary["half_days"],
                    summary["absent_days"],
                    f"₹{summary['sunday_bonus']}",
                    f"₹{summary['total_salary']}",
                    "PDF",
                    "Excel"
                ), tags=(emp_id,))

    def on_click(event):
        item = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if not item:
            return
        emp_id = tree.item(item, "tags")[0]
        f_date_str = from_date.get()
        t_date_str = to_date.get()
        f_date = datetime.strptime(f_date_str, "%Y-%m-%d")
        t_date = datetime.strptime(t_date_str, "%Y-%m-%d")
        summary = calculate_salary_summary(emp_id, f_date, t_date)

        if col == '#8':
            save_pdf(summary, f_date_str, t_date_str)
        elif col == '#9':
            save_excel(summary, f_date_str, t_date_str)

    tree.bind("<Button-1>", on_click)

    tk.Button(root, text="Generate Report", bg="#007acc", fg="white", font=("Arial", 10, "bold"), command=generate).place(x=460, y=10)

    root.mainloop()

if __name__ == "__main__":
    show_salary_gui()