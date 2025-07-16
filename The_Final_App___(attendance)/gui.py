# gui.py

import os
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
from settings_gui import run_settings_gui
from utils.helpers import verify_admin_password
from config_handler import load_config
from subprocess import Popen

config = load_config()

def launch_script(script, args=None):
    try:
        script_path = os.path.join(os.getcwd(), script)
        if args:
            subprocess.Popen(["python", script_path] + args)
        else:
            subprocess.Popen(["python", script_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch {script}: {str(e)}")


def run_gui():
    root = Tk()
    root.title("📌 Attendance Dashboard")
    root.geometry("400x600")
    root.resizable(True,True)
    root.minsize(700, 500)
    root.configure(bg="#eaf4fc")

    # Header frame
    top_frame = Frame(root, bg="#eaf4fc")
    top_frame.pack(fill=X, padx=10, pady=10)

    Label(top_frame, text="Employee  Manager", font=("Arial", 22, "bold"), bg="#eaf4fc", fg="#003366" ,).pack(side=LEFT, padx=(20))

    # Load settings icon
    gear_img = Image.open("assets/gear.png").resize((30, 30))
    gear_photo = ImageTk.PhotoImage(gear_img)

    def open_settings():
        if verify_admin_password(config):
            run_settings_gui()

    gear_btn = Button(top_frame, image=gear_photo, command=open_settings, bd=0, bg="#eaf4fc", activebackground="#eaf4fc")
    gear_btn.image = gear_photo
    gear_btn.pack(side=RIGHT, padx=10)

    # Buttons frame
    button_frame = Frame(root, bg="#eaf4fc")
    button_frame.pack(pady=30)

    btn_style = {"width": 30, "height": 2, "bg": "#4a90e2", "fg": "white", "activebackground": "#357abd", "font": ("Arial", 12)}

    Button(button_frame, text="📌 Mark Attendance", command=lambda: launch_script("mark_attendance.pyw", ["--manual"]), **btn_style).grid(row=1, column=1, padx=10, pady=10)
    Button(button_frame, text="➕ Register Employee", command=lambda:verify_admin_password(config) and launch_script("register_employee.py"), **btn_style).grid(row=1, column=0, pady=10)
    Button(button_frame, text="✏️ Edit Employee Salary", command=lambda:verify_admin_password(config) and launch_script("edit_employee.py"), **btn_style).grid(row=2, column=0, pady=10)
    Button(button_frame, text="🗑 Remove Employee", command=lambda:verify_admin_password(config) and launch_script("remove_employee.py"), **btn_style).grid(row=3, column=0, pady=10)
    Button(button_frame, text="🧽 Remove Attendance", command=lambda:verify_admin_password(config) and launch_script("remove_attendance.py"), **btn_style).grid(row=4, column=0, pady=10)
    Button(button_frame, text="💰 View Salary Summary", command=lambda:verify_admin_password(config) and launch_script("salary_gui.py"), **btn_style).grid(row=5, column=0, pady=10)
    Button(button_frame, text="📋 View All Employees", command=lambda: launch_script("view_employees.py"), **btn_style).grid(row=6, column=0, pady=10)
    Button(button_frame, text="📖 Employee History", command=lambda: launch_script("view_employee_history.py"), **btn_style).grid(row=2, column=1, padx=10, pady=10)
    Button(button_frame, text="📅 Attendance History", command=lambda: launch_script("view_attendance_history.py"), **btn_style).grid(row=3, column=1, padx=10, pady=10)
    Button(button_frame, text="📁 Employee Documents", command=lambda: Popen(["python", "employee_documents_gui.py"]), **btn_style).grid(row=4, column=1, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
