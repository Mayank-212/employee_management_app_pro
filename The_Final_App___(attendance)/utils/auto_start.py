# utils/auto_start.py

import subprocess
import os
from config_handler import load_config

def run_attendance_silently():
    try:
        mark_script = os.path.join(os.getcwd(), "mark_attendance.pyw")
        subprocess.Popen(["pythonw", mark_script], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print("Error running attendance silently:", e)

if __name__ == "__main__":
    config = load_config()
    if config.get("auto_start_enabled", False):
        run_attendance_silently()
