# utils/salary.py

import json
import os
from datetime import datetime
from config_handler import load_config

def update_salary_summary(emp_id):
    config = load_config()
    salary_file = f"data/salary_summary/{emp_id}.json"
    attendance_file = f"data/attendance/{emp_id}.json"

    daily_salary = float(config.get("default_daily_salary", 500))
    sunday_bonus = float(config.get("sunday_bonus", 500))
    half_day_percent = float(config.get("half_day_percent", 0.5))
    entry_cutoff = config.get("entry_cutoff_time", "09:30")
    exit_cutoff = config.get("exit_cutoff_time", "17:00")

    salary_summary = {}
    if os.path.exists(salary_file):
        with open(salary_file, "r") as f:
            salary_summary = json.load(f)

    if not os.path.exists(attendance_file):
        return

    with open(attendance_file, "r") as f:
        logs = json.load(f)

    day_logs = {}
    for log in logs:
        date = log["date"]
        if date not in day_logs:
            day_logs[date] = {}
        day_logs[date][log["status"]] = log["time"]

    for date, entry_exit in day_logs.items():
        if "entry" not in entry_exit or "exit" not in entry_exit:
            continue

        entry_time = entry_exit["entry"]
        exit_time = entry_exit["exit"]

        # Full day by default
        full_day = True
        if entry_time > entry_cutoff or exit_time < exit_cutoff:
            full_day = False

        # Check for Sunday
        day_obj = datetime.strptime(date, "%Y-%m-%d")
        is_sunday = day_obj.weekday() == 6  # 0=Monday, 6=Sunday

        if is_sunday:
            amount = sunday_bonus
        elif not full_day:
            amount = daily_salary * half_day_percent
        else:
            amount = daily_salary

        salary_summary[date] = {
            "entry": entry_time,
            "exit": exit_time,
            "amount": round(amount, 2)
        }

    with open(salary_file, "w") as f:
        json.dump(salary_summary, f, indent=4)
