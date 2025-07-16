import json
import os
from datetime import time

CONFIG_FILE = "config.json"

# Default configuration
default_config = {
    "entry_cutoff_time": "10:00",       # After this = late
    "exit_cutoff_time": "17:00",        # Before this = early leave
    "minimum_entry_exit_gap_min": 2,    # Minutes between entry & exit
    "sensor_port": "/dev/ttyUSB0",      # Default port for fingerprint sensor
    "data_directory": ".",              # Folder to store attendance/employee data
    "auto_start_enabled": False,        # Scheduler toggle
    "auto_start_time": "08:30",         # Auto-start attendance marking at this time
    "admin_password": "6965"            # Default admin password
}

# Ensure config file exists
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

def load_config():
    """Load config from file."""
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(new_config: dict):
    """Save updated config."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(new_config, f, indent=4)

# Optional: convert "HH:MM" string to datetime.time object
def parse_time_string(tstr):
    hour, minute = map(int, tstr.split(":"))
    return time(hour=hour, minute=minute)

# Access config as needed
config = load_config()
