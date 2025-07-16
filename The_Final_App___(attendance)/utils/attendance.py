# utils/attendance.py

import os
import json
import datetime

def record_attendance(emp_id, status):
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    attendance_path = f"data/attendance/{emp_id}.json"

    # Load existing logs
    logs = []
    if os.path.exists(attendance_path):
        with open(attendance_path, "r") as f:
            logs = json.load(f)

    logs.append({
        "date": today_str,
        "time": time_str,
        "status": status
    })

    # Save logs
    with open(attendance_path, "w") as f:
        json.dump(logs, f, indent=4)
