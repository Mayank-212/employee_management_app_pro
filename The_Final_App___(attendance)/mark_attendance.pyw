import os
import sys
import time
import datetime
from config_handler import load_config
from utils.helpers import (
    initialize_sensor,
    speak,
    load_employee_data,
    save_attendance,
    is_exit_scan,
    get_today_attendance,
    meets_minimum_gap
)

# ---------- Configurable thresholds ----------
MIN_MATCH_SCORE = 100        # Minimum fingerprint match score
MIN_GAP_MINUTES = 0.1          # Minimum time between entry and exit
attendance_running = True  # Global flag

# ---------- Match fingerprint with score threshold ----------
def match_fingerprint_with_score(sensor, min_score=MIN_MATCH_SCORE):
    try:
        print("Place finger on sensor...")
        while not sensor.readImage():
            pass
        sensor.convertImage(0x01)
        result = sensor.searchTemplate()
        position_number, accuracy_score = result

        if position_number >= 0:
            print(f"Fingerprint matched at position: {position_number} (Score: {accuracy_score})")
            if accuracy_score >= min_score:
                return position_number
            else:
                print("[INFO] Match score too low, ignoring.")
                return None
        else:
            print("No match found.")
            return None
    except Exception as e:
        print(f"[Match Error] {e}")
        return None

# ---------- Main attendance logic ----------
def log_attendance():
    global attendance_running
    config = load_config()
    port = config.get("fingerprint_port", "COM6")
    sensor = initialize_sensor(port)
    if not sensor:
        speak("Fingerprint sensor not detected.")
        return

    speak("Attendance system started.")
    attendance_running = True

    while attendance_running:
        print("📷 Waiting for fingerprint...")
        position_number = match_fingerprint_with_score(sensor)
        if position_number is None:
            continue

        employee = load_employee_data(position_number)
        if not employee:
            speak("Unrecognized fingerprint.")
            continue

        now = datetime.datetime.now()
        emp_id = employee["id"]
        name = employee["name"]
        current_time_str = now.strftime("%H:%M")

        today_log = get_today_attendance(emp_id)
        if not today_log.get("entry_time"):
            action = "entry"
        elif not today_log.get("exit_time"):
            action = "exit"
        else:
            speak(f"{name}, you have already marked both entry and exit.")
            continue

        last_time_str = today_log.get("entry_time" if action == "exit" else "exit_time", "00:00")
        if last_time_str != "00:00":
            if not meets_minimum_gap(last_time_str, current_time_str, MIN_GAP_MINUTES):
                speak(f"{name}, please wait at least {MIN_GAP_MINUTES} minutes before next scan.")
                continue

        save_attendance(emp_id, name, now.time(), now.date(), action)
        speak(f"{name} {action} recorded.")


def stop_attendance_loop():
    global attendance_running
    attendance_running = False
# ---------- Auto-start logic ----------
def should_start_for_period(start_str, end_str):
    now = datetime.datetime.now().time()
    start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
    end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
    return start_time <= now <= end_time

def auto_start_check():
    config = load_config()

    if not config.get("auto_start_enabled", False):
        print("🔕 Auto start is disabled in config.json")
        return

    entry_start = config.get("auto_start_entry", "08:00")
    entry_off = config.get("auto_off_entry", "10:00")
    exit_start = config.get("auto_start_exit", "17:00")
    exit_off = config.get("auto_off_exit", "19:00")

    if should_start_for_period(entry_start, entry_off) or should_start_for_period(exit_start, exit_off):
        speak("Auto attendance window matched.")
        log_attendance()
    else:
        print("🕒 Outside auto attendance time.")
        speak("Attendance will not start now.")

# ---------- Entry Point ----------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        log_attendance()
    else:
        auto_start_check()
