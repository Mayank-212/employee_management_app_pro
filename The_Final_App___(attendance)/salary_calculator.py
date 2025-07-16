from datetime import datetime, timedelta
from utils.helpers import load_json, get_attendance_file_path
from config_handler import load_config
import os

def calculate_salary_summary(emp_id, from_date, to_date):
    config = load_config()
    employees = load_json("data/employees/employees.json")
    emp = employees.get(emp_id)
    if not emp:
        return None

    name = emp.get("name", "Unknown")
    entry_cutoff = datetime.strptime(config.get("entry_cutoff_time", "10:00"), "%H:%M").time()
    exit_cutoff = datetime.strptime(config.get("exit_cutoff_time", "17:00"), "%H:%M").time()

    summary_data = []
    full_days = 0
    half_days = 0
    sunday_bonus = 0
    total_salary = 0
    absent_days = 0
    late_entry_count = 0  # track number of late entries

    current = from_date
    while current <= to_date:
        date_str = current.strftime("%Y-%m-%d")
        att_file = get_attendance_file_path(emp_id, date_str)

        if not os.path.exists(att_file):
            absent_days += 1
            current += timedelta(days=1)
            continue

        rec = load_json(att_file)
        if not rec:
            absent_days += 1
            current += timedelta(days=1)
            continue

        entry_time_str = rec.get("entry_time")
        exit_time_str = rec.get("exit_time")
        salary_per_day = rec.get("salary_at_time", emp.get("salary", 0))

        if not entry_time_str or not exit_time_str:
            absent_days += 1
            current += timedelta(days=1)
            continue

        try:
            entry_time = datetime.strptime(entry_time_str, "%H:%M").time()
            exit_time = datetime.strptime(exit_time_str, "%H:%M").time()
        except ValueError:
            absent_days += 1
            current += timedelta(days=1)
            continue

        is_sunday = current.weekday() == 6
        late_entry = entry_time > entry_cutoff
        early_exit = exit_time < exit_cutoff

        entry_dt = datetime.combine(current, entry_time)
        exit_dt = datetime.combine(current, exit_time)
        work_duration = (exit_dt - entry_dt).total_seconds() / 3600  # in hours

        if late_entry:
            late_entry_count += 1

        if late_entry and early_exit:
            if work_duration < 6:
                status = "absent"
                day_salary = 0
                absent_days += 1
            else:
                status = "half"
                day_salary = 0.5 * salary_per_day
                half_days += 1

        elif early_exit:
            status = "half"
            day_salary = 0.5 * salary_per_day
            half_days += 1

        elif late_entry:
            if late_entry_count > 5:
                status = "half"
                day_salary = 0.5 * salary_per_day
                half_days += 1
            else:
                status = "present"
                day_salary = salary_per_day
                full_days += 1
        else:
            status = "present"
            day_salary = salary_per_day
            full_days += 1

        if is_sunday:
            sunday_bonus += 100

        total_salary += day_salary

        summary_data.append({
            "date": date_str,
            "entry": entry_time_str,
            "exit": exit_time_str,
            "status": status,
            "is_sunday": is_sunday
        })

        current += timedelta(days=1)

    total_salary += sunday_bonus

    return {
        "emp_id": emp_id,
        "name": name,
        "summary_data": summary_data,
        "full_days": full_days,
        "half_days": half_days,
        "sunday_bonus": sunday_bonus,
        "total_salary": int(total_salary),
        "absent_days": absent_days,
        "last_status": summary_data[-1]["status"] if summary_data else "-"
    }