# settings_gui.py

from tkinter import *
from tkinter import messagebox
from config_handler import load_config, save_config
import subprocess
import os

def create_auto_task(task_name, start_time):
    bat_path = os.path.abspath("autorun/schedule_attendance.bat")
    if not os.path.exists(bat_path):
        messagebox.showerror("Error", "Bat file not found for scheduling.")
        return

    try:
        subprocess.run([
            "schtasks", "/Create",
            "/SC", "DAILY",
            "/TN", task_name,
            "/TR", f'"{bat_path}"',
            "/ST", start_time,
            "/F"
        ], check=True)
        print(f"[Task Scheduler] Task '{task_name}' created for {start_time}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Scheduler Error", f"Failed to create scheduled task:\n{e}")

def run_settings_gui():
    config = load_config()
    
    root = Toplevel()
    root.title("⚙ Settings")
    root.geometry("460x500")
    root.resizable(True,True)

    # Canvas + Scrollable Frame
    canvas = Canvas(root, borderwidth=0, background="#f4f4f4")
    frame = Frame(canvas, background="#f4f4f4")
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_frame_config(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_frame_config)

    def create_label_entry(parent, label_text, default_value):
        Label(parent, text=label_text, bg="#f4f4f4", font=("Arial", 12)).pack(pady=6)
        entry = Entry(parent, width=30)
        entry.insert(0, default_value)
        entry.pack()
        return entry

    # Admin password
    Label(frame, text="Admin Password:", bg="#f4f4f4", font=("Arial", 12)).pack(pady=5)
    admin_pass_entry = Entry(frame, show="*", width=30)
    admin_pass_entry.insert(0, config.get("admin_password", ""))
    admin_pass_entry.pack()

    show_pass_var = BooleanVar()
    def toggle_password():
        admin_pass_entry.config(show="" if show_pass_var.get() else "*")

    Checkbutton(frame, text="Show Password", variable=show_pass_var, command=toggle_password, bg="#f4f4f4").pack()

    # All config entries
    auto_start_time = create_label_entry(frame, "Auto Start Time (HH:MM)", config.get("auto_start_time", "09:00"))

    auto_start_var = BooleanVar(value=config.get("auto_start_enabled", False))
    Checkbutton(frame, text="Enable Auto Start", variable=auto_start_var, bg="#f4f4f4").pack(pady=5)

    fingerprint_port = create_label_entry(frame, "Fingerprint Port", config.get("fingerprint_port", "COM3"))
    entry_cutoff = create_label_entry(frame, "Entry Cutoff Time", config.get("entry_cutoff_time", "10:00"))
    exit_cutoff = create_label_entry(frame, "Exit Cutoff Time", config.get("exit_cutoff_time", "17:00"))
    data_dir = create_label_entry(frame, "Data Directory", config.get("data_directory", "data"))

    Label(frame, text="Entry Scan Time Window", bg="#f4f4f4", font=("Arial", 13, "bold")).pack(pady=10)
    auto_entry_start = create_label_entry(frame, "Auto Entry Start", config.get("auto_start_entry", "08:00"))
    auto_entry_off = create_label_entry(frame, "Auto Entry Off", config.get("auto_off_entry", "10:00"))

    Label(frame, text="Exit Scan Time Window", bg="#f4f4f4", font=("Arial", 13, "bold")).pack(pady=10)
    auto_exit_start = create_label_entry(frame, "Auto Exit Start", config.get("auto_start_exit", "17:00"))
    auto_exit_off = create_label_entry(frame, "Auto Exit Off", config.get("auto_off_exit", "19:00"))

    def save_settings():
        updated = {
            "admin_password": admin_pass_entry.get(),
            "auto_start_time": auto_start_time.get(),
            "auto_start_enabled": auto_start_var.get(),
            "fingerprint_port": fingerprint_port.get(),
            "entry_cutoff_time": entry_cutoff.get(),
            "exit_cutoff_time": exit_cutoff.get(),
            "data_directory": data_dir.get(),
            "auto_start_entry": auto_entry_start.get(),
            "auto_off_entry": auto_entry_off.get(),
            "auto_start_exit": auto_exit_start.get(),
            "auto_off_exit": auto_exit_off.get()
        }
        save_config(updated)

        if auto_start_var.get():
            # Create separate tasks for Entry and Exit auto attendance
            create_auto_task("AttendanceAutoStartEntry", auto_entry_start.get())
            create_auto_task("AttendanceAutoStartExit", auto_exit_start.get())
        else:
            # Auto-start disabled → remove tasks
            subprocess.run(["schtasks", "/Delete", "/TN", "AttendanceAutoStartEntry", "/F"], stderr=subprocess.DEVNULL)
            subprocess.run(["schtasks", "/Delete", "/TN", "AttendanceAutoStartExit", "/F"], stderr=subprocess.DEVNULL)    

        messagebox.showinfo("Settings", "Settings saved successfully.")
        root.destroy()
        

    Button(frame, text="Save Settings", command=save_settings, bg="#007acc", fg="white", padx=10, pady=5).pack(pady=20)

    root.mainloop()
