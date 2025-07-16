import os
import sys

def schedule_autostart():
    script_path = os.path.abspath("background_attendance.py")
    python_path = sys.executable
    task_name = "FingerprintAttendanceAutoStart"

    os.system(
        f'schtasks /create /tn {task_name} /tr "{python_path} {script_path}" /sc onlogon /rl highest /f'
    )
    print("✔ Auto-start task created.")

if __name__ == "__main__":
    schedule_autostart()
