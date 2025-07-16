import os
import json
import pickle
from datetime import datetime, timedelta
import pyttsx3
from tkinter import messagebox
from config import load_config
import time
from tkinter.simpledialog import askstring
from pyfingerprint.pyfingerprint import PyFingerprint


# ---------- TTS ----------
def speak(message):
    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

# ---------- JSON Utilities ----------
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ---------- Config & Init ----------
def initialize_app_environment():
    folders = [
        "data/employees",
        "data/attendance",
        "data/reports",
        "assets",
        "config",
        "employees_data",
        "employee_documents"
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists("config.json"):
        default_config = {
            "entry_cutoff_time": "10:00",
            "exit_cutoff_time": "17:00",
            "admin_password": "6965",
            "fingerprint_port": "COM4",
            "attendance_data_dir": "data/attendance",
            "employee_data_directory": "employees_data",
            "summary_data_dir": "data/reports",
            "auto_start_enabled": False,
            "auto_start_time": "09:00"
        }
        save_json("config.json", default_config)

# ---------- File Paths ----------
def get_employee_file_path(emp_id):
    folder = load_config().get("employee_data_directory", "employees_data")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{emp_id}.pkl")

def get_attendance_file_path(emp_id, date=None):
    config = load_config()
    att_dir = config.get("attendance_data_dir", "data/attendance")
    os.makedirs(att_dir, exist_ok=True)
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(att_dir, f"{emp_id}_{date}.json")

def get_attendance_folder():
    config = load_config()
    base_dir = config.get("attendance_data_dir", "data/attendance")
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def ensure_summary_dir():
    config = load_config()
    base_dir = config.get("summary_data_dir", "data/reports")
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# ---------- Sensor ----------
def initialize_sensor(port):
    try:
        sensor = PyFingerprint(port, 57600, 0xFFFFFFFF, 0x00000000)
        if sensor.verifyPassword():
            return sensor
        else:
            raise Exception("Incorrect fingerprint sensor password.")
    except Exception as e:
        print(f"[Sensor Error] {e}")
        return None

def match_fingerprint(sensor):
    try:
        while not sensor.readImage():
            time.sleep(0.1)

        sensor.convertImage(0x01)
        result = sensor.searchTemplate()
        position_number = result[0]
        accuracy_score = result[1]

        if position_number == -1:
            print("[ERROR] No match found.")
            return None
        else:
            print(f"Fingerprint matched at position: {position_number} (Score: {accuracy_score})")
            return position_number

    except Exception as e:
        error = str(e)
        if "0x17" in error:
            print("[Match Error] Unknown error 0x17 — possibly bad image.")
        else:
            print(f"[Match Error] {error}")
        return None


# ---------- Time ----------
def is_today_sunday():
    return datetime.today().weekday() == 6

def is_late(entry_time_str, cutoff_str):
    fmt = "%H:%M"
    entry_time = datetime.strptime(entry_time_str, fmt)
    cutoff_time = datetime.strptime(cutoff_str, fmt)
    return entry_time > cutoff_time

def is_early(exit_time_str, cutoff_str):
    fmt = "%H:%M"
    exit_time = datetime.strptime(exit_time_str, fmt)
    cutoff_time = datetime.strptime(cutoff_str, fmt)
    return exit_time < cutoff_time

def meets_minimum_gap(entry_time, exit_time):
    fmt = "%H:%M"
    t1 = datetime.strptime(entry_time, fmt)
    t2 = datetime.strptime(exit_time, fmt)
    return (t2 - t1) >= timedelta(minutes=2)

# ---------- Attendance ----------
def is_exit_scan(today_attendance):
    return today_attendance.get("entry_time") and not today_attendance.get("exit_time")

def get_today_attendance(emp_id):
    from datetime import date
    today_str = date.today().strftime("%Y-%m-%d")
    path = os.path.join("data", "attendance", str(emp_id), f"{today_str}.json")
    return load_json(path)

def save_attendance(emp_id, name, time_obj, date_obj, action):
    """Save attendance in JSON format per day per employee"""
    path = os.path.join("data", "attendance", str(emp_id), f"{date_obj.strftime('%Y-%m-%d')}.json")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    data = load_json(path)

    if action == "entry":
        data["entry_time"] = time_obj.strftime("%H:%M")
    elif action == "exit":
        data["exit_time"] = time_obj.strftime("%H:%M")

    data["name"] = name

    # ✅ Save the salary at the time of attendance
    try:
        all_employees = load_json("data/employees/employees.json")
        emp_info = all_employees.get(emp_id, {})
        data["salary_at_time"] = emp_info.get("salary", 0)
    except Exception as e:
        print(f"[WARN] Failed to fetch salary: {e}")
        data["salary_at_time"] = 0

    save_json(path, data)

# ---------- Multi-Fingerprint Support ----------
def load_employee_data(matched_id):
    config = load_config()
    base_dir = config.get("employee_data_directory", "employees_data")

    if not os.path.exists(base_dir):
        print(f"[ERROR] Employee data folder '{base_dir}' does not exist.")
        return None

    for filename in os.listdir(base_dir):
        if filename.endswith(".pkl"):
            path = os.path.join(base_dir, filename)
            try:
                with open(path, "rb") as f:
                    data = pickle.load(f)
                    fingerprint_ids = data.get("fingerprint_ids", [])
                    if matched_id in fingerprint_ids:
                        print(f"[MATCH] Employee matched for ID {data['id']} at position {matched_id}")
                        return data
            except Exception as e:
                print(f"[ERROR] Failed reading {path}: {e}")
    print(f"[ERROR] No employee data found for fingerprint ID {matched_id}")
    return None



# ---------- UI ----------
def show_error(title, message):
    messagebox.showerror(title, message)

def show_info(title, message):
    messagebox.showinfo(title, message)

def verify_admin_password(config):
    # from tkinter import messagebox
    # input_pwd = askstring("🔒 Admin Verification", "Enter admin password:", show="*")
    # if input_pwd != config.get("admin_password", "6965"):
    #     messagebox.showerror("Access Denied", "Incorrect password!")
    #     return False
    return True


def get_employee_document_folder(emp_id):
    folder = os.path.join("employee_documents", emp_id)
    os.makedirs(folder, exist_ok=True)
    return folder

def meets_minimum_gap(t1_str, t2_str, gap_minutes=2):
    fmt = "%H:%M"
    t1 = datetime.strptime(t1_str, fmt)
    t2 = datetime.strptime(t2_str, fmt)
    return (t2 - t1) >= timedelta(minutes=gap_minutes)
